import Phaser from 'phaser'
import { assetUrl } from './assets'
import { bakeVariant, sourceKey, textureKey } from './bake'
import { PaperDoll, loadoutFrom, type Facing, type Loadout } from './doll'
import type { Manifest } from './manifest'
import { bindStick, mountWardrobe, stick } from './ui'

const TILE = 32
const COLS = 40
const ROWS = 30
const SPEED = 104

interface Keys {
  left: Phaser.Input.Keyboard.Key
  right: Phaser.Input.Keyboard.Key
  up: Phaser.Input.Keyboard.Key
  down: Phaser.Input.Keyboard.Key
  arrowLeft: Phaser.Input.Keyboard.Key
  arrowRight: Phaser.Input.Keyboard.Key
  arrowUp: Phaser.Input.Keyboard.Key
  arrowDown: Phaser.Input.Keyboard.Key
  space: Phaser.Input.Keyboard.Key
}

function paintGround(): HTMLCanvasElement {
  const canvas = document.createElement('canvas')
  canvas.width = COLS * TILE
  canvas.height = ROWS * TILE
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('Could not paint the ground')
  ctx.imageSmoothingEnabled = false
  const grass = ['#2f6a45', '#38764c', '#275a3b', '#468556']
  const dirt = ['#8a6240', '#6e4c32', '#a07850']
  for (let y = 0; y < ROWS; y += 1) {
    for (let x = 0; x < COLS; x += 1) {
      const path = (x >= 18 && x <= 21) || (y >= 14 && y <= 16 && x >= 8 && x <= 32)
      const n = (x * 17 + y * 31) % 4
      ctx.fillStyle = path ? dirt[(x + y) % dirt.length] ?? dirt[0] : grass[n] ?? grass[0]
      ctx.fillRect(x * TILE, y * TILE, TILE, TILE)
      if (!path && (x * 13 + y * 7) % 11 === 0) {
        ctx.fillStyle = '#1e4630'
        ctx.fillRect(x * TILE + 8, y * TILE + 18, 3, 3)
        ctx.fillRect(x * TILE + 20, y * TILE + 8, 2, 2)
      }
    }
  }
  return canvas
}

function pointerIsTouch(pointer: Phaser.Input.Pointer): boolean {
  if (pointer.wasTouch) return true
  const event = pointer.event
  return event instanceof PointerEvent && event.pointerType !== 'mouse'
}

export class PlayScene extends Phaser.Scene {
  private doll!: PaperDoll
  private keys!: Keys
  private facing: Facing = 'down'
  private tap: { x: number; y: number } | null = null
  private turntable: PaperDoll[] = []
  private turntableLabels: Phaser.GameObjects.Text[] = []
  private turntableBack!: Phaser.GameObjects.Rectangle
  private fpsTick = 0
  private readonly manifest: Manifest
  private loadout: Loadout
  private variant: string

  constructor(manifest: Manifest) {
    super('play')
    this.manifest = manifest
    const preset = manifest.presets[0]
    if (!preset) throw new Error('Paper doll manifest has no preset')
    this.loadout = loadoutFrom(preset.loadout)
    this.variant = preset.variant
  }

  preload(): void {
    for (const sheet of this.manifest.sheets) {
      this.load.image(sourceKey(sheet.slot, sheet.item), assetUrl(`hero/${sheet.file}`))
    }
  }

  create(): void {
    this.paintMap()
    const colors = this.manifest.variants.find((entry) => entry.id === this.variant)?.colors
    if (!colors) throw new Error(`Unknown palette ${this.variant}`)
    for (const sheet of this.manifest.sheets) {
      bakeVariant(this, sourceKey(sheet.slot, sheet.item), textureKey(sheet.slot, sheet.item, this.variant), colors)
    }
    const spawnX = (COLS * TILE) / 2
    const spawnY = (ROWS * TILE) / 2
    this.doll = new PaperDoll(this, this.manifest, spawnX, spawnY, this.loadout, this.variant)
    this.cameras.main.setBounds(0, 0, COLS * TILE, ROWS * TILE)
    this.cameras.main.setRoundPixels(true)
    this.cameras.main.startFollow(this.doll.root, true, 1, 1)
    this.keys = this.bindKeys()
    this.game.canvas.tabIndex = 0
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      this.game.canvas.focus({ preventScroll: true })
      if (pointerIsTouch(pointer)) {
        const world = this.cameras.main.getWorldPoint(pointer.x, pointer.y)
        this.tap = { x: world.x, y: world.y }
        return
      }
      this.doll.attack()
    })
    this.buildTurntable()
    bindStick()
    const wardrobe = {
      loadout: this.loadout,
      variant: this.variant,
      onChange: (): void => {
        this.variant = wardrobe.variant
        this.doll.setLoadout(this.loadout, this.variant)
        for (const doll of this.turntable) doll.setLoadout(this.loadout, this.variant)
      },
    }
    mountWardrobe(this.manifest, wardrobe)
    document.addEventListener('doll-attack', () => this.doll.attack())
    document.addEventListener('doll-turntable', (event) => {
      if (!(event instanceof CustomEvent) || typeof event.detail !== 'boolean') return
      this.showTurntable(event.detail)
    })
  }

  override update(_time: number, delta: number): void {
    this.fpsTick += 1
    if (this.fpsTick % 10 === 0) {
      const node = document.getElementById('fps')
      if (node) node.textContent = `FPS ${Math.round(this.game.loop.actualFps)}`
    }
    this.move(delta / 1000)
    this.doll.sync()
    for (const doll of this.turntable) doll.sync()
  }

  private paintMap(): void {
    const canvas = paintGround()
    if (this.textures.exists('ground')) this.textures.remove('ground')
    this.textures.addCanvas('ground', canvas)
    this.textures.get('ground').setFilter(Phaser.Textures.FilterMode.NEAREST)
    this.add.image(0, 0, 'ground').setOrigin(0, 0)
  }

  private bindKeys(): Keys {
    const keyboard = this.input.keyboard
    if (!keyboard) throw new Error('Keyboard input is unavailable')
    const codes = Phaser.Input.Keyboard.KeyCodes
    keyboard.addCapture([codes.UP, codes.DOWN, codes.LEFT, codes.RIGHT, codes.SPACE, codes.W, codes.A, codes.S, codes.D])
    return {
      left: keyboard.addKey(codes.A),
      right: keyboard.addKey(codes.D),
      up: keyboard.addKey(codes.W),
      down: keyboard.addKey(codes.S),
      arrowLeft: keyboard.addKey(codes.LEFT),
      arrowRight: keyboard.addKey(codes.RIGHT),
      arrowUp: keyboard.addKey(codes.UP),
      arrowDown: keyboard.addKey(codes.DOWN),
      space: keyboard.addKey(codes.SPACE),
    }
  }

  private move(dt: number): void {
    if (Phaser.Input.Keyboard.JustDown(this.keys.space)) this.doll.attack()
    let x = 0
    let y = 0
    if (this.keys.left.isDown || this.keys.arrowLeft.isDown) x -= 1
    if (this.keys.right.isDown || this.keys.arrowRight.isDown) x += 1
    if (this.keys.up.isDown || this.keys.arrowUp.isDown) y -= 1
    if (this.keys.down.isDown || this.keys.arrowDown.isDown) y += 1
    const keyHeld = x !== 0 || y !== 0
    if (keyHeld) this.tap = null
    if (!keyHeld && stick.held) {
      x = stick.x
      y = stick.y
    } else if (!keyHeld && this.tap) {
      x = this.tap.x - this.doll.root.x
      y = this.tap.y - this.doll.root.y
      if (Math.hypot(x, y) < 6) {
        this.tap = null
        x = 0
        y = 0
      }
    }
    const len = Math.hypot(x, y)
    if (len > 0.001) {
      x /= len
      y /= len
      this.doll.root.x = Phaser.Math.Clamp(this.doll.root.x + x * SPEED * dt, 24, COLS * TILE - 24)
      this.doll.root.y = Phaser.Math.Clamp(this.doll.root.y + y * SPEED * dt, 40, ROWS * TILE - 12)
      this.facing = Math.abs(x) > Math.abs(y) ? (x < 0 ? 'left' : 'right') : y < 0 ? 'up' : 'down'
      this.doll.setMoving(this.facing, true)
      return
    }
    this.doll.setMoving(this.facing, false)
  }

  private buildTurntable(): void {
    this.turntableBack = this.add.rectangle(256, 52, 512, 104, 0x10141a, 0.92)
    this.turntableBack.setScrollFactor(0)
    this.turntableBack.setDepth(20)
    this.turntableBack.setVisible(false)
    const facings: Facing[] = ['down', 'left', 'up', 'right']
    const labels = ['Down', 'Left', 'Up', 'Right']
    facings.forEach((facing, index) => {
      const x = 70 + index * 124
      const doll = new PaperDoll(this, this.manifest, x, 88, this.loadout, this.variant)
      doll.lockWalk(facing)
      doll.setScrollLocked()
      doll.root.setDepth(21)
      doll.root.setVisible(false)
      const label = this.add.text(x - 16, 8, labels[index] ?? facing, {
        fontFamily: 'monospace',
        fontSize: '12px',
        color: '#f4efe4',
      })
      label.setScrollFactor(0)
      label.setDepth(22)
      label.setVisible(false)
      this.turntable.push(doll)
      this.turntableLabels.push(label)
    })
  }

  private showTurntable(on: boolean): void {
    this.turntableBack.setVisible(on)
    for (const doll of this.turntable) doll.root.setVisible(on)
    for (const label of this.turntableLabels) label.setVisible(on)
  }
}
