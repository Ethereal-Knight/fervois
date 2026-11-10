import Phaser from 'phaser'
import { bakeVariant, sourceKey, textureKey } from './bake'
import type { Manifest } from './manifest'

export type Facing = 'down' | 'left' | 'up' | 'right'
export type AnimName = 'idle' | 'walk' | 'attack'

const FACINGS: Facing[] = ['down', 'left', 'up', 'right']
const PIVOT_Y = 60 / 64

export interface Loadout {
  hair: string
  head?: string
  chest?: string
  legs?: string
  feet?: string
  hands?: string
  back?: string
  main?: string
  off?: string
}

export function loadoutFrom(raw: Record<string, string>): Loadout {
  const hair = raw.hair
  if (!hair) throw new Error('A paper doll needs a hair style')
  const next: Loadout = { hair }
  for (const slot of ['head', 'chest', 'legs', 'feet', 'hands', 'back', 'main', 'off'] as const) {
    const item = raw[slot]
    if (item) next[slot] = item
  }
  return next
}

function frameList(manifest: Manifest, anim: AnimName, facing: Facing): number[] {
  const spec = manifest.anims[anim]
  if (!spec) throw new Error(`Missing anim ${anim}`)
  const row = spec.row + FACINGS.indexOf(facing)
  const start = row * manifest.columns
  return Array.from({ length: spec.frames }, (_, index) => start + index)
}

function asFrameIndex(frame: Phaser.Animations.AnimationFrame): number {
  const value = frame.textureFrame
  const index = typeof value === 'number' ? value : Number(value)
  return Number.isInteger(index) ? index : 0
}

export class PaperDoll {
  readonly root: Phaser.GameObjects.Container
  private readonly body: Phaser.GameObjects.Sprite
  private readonly sprites = new Map<string, Phaser.GameObjects.Sprite>()
  private facing: Facing = 'down'
  private anim: AnimName = 'idle'
  private frameIndex = 0
  private attacking = false
  private moving = false
  private locked = false
  private variant: string
  private loadout: Loadout

  constructor(
    private readonly scene: Phaser.Scene,
    private readonly manifest: Manifest,
    x: number,
    y: number,
    loadout: Loadout,
    variant: string,
  ) {
    this.loadout = loadout
    this.variant = variant
    this.root = scene.add.container(x, y)
    this.body = this.makeSprite('body', 'base')
    this.sprites.set('body', this.body)
    for (const slot of ['hair', 'head', 'chest', 'legs', 'feet', 'hands', 'back', 'main', 'off']) {
      const item = slot === 'hair' ? loadout.hair : loadout[slot as keyof Loadout]
      const sprite = this.makeSprite(slot, item || this.fallbackItem(slot))
      sprite.setVisible(false)
      this.sprites.set(slot, sprite)
    }
    this.body.on('animationupdate', this.onFrame)
    this.body.on('animationcomplete', this.onComplete)
    this.equip()
    this.play('idle')
  }

  destroy(): void {
    this.body.off('animationupdate', this.onFrame)
    this.body.off('animationcomplete', this.onComplete)
    this.root.destroy()
  }

  lockWalk(facing: Facing): void {
    this.locked = true
    this.facing = facing
    this.attacking = false
    this.play('walk')
  }

  setScrollLocked(): void {
    this.root.setScrollFactor(0, 0)
  }

  setLoadout(loadout: Loadout, variant: string): void {
    const variantChanged = variant !== this.variant
    this.loadout = loadout
    this.variant = variant
    if (variantChanged) this.ensureVariant(variant)
    this.equip()
    if (this.locked) this.play('walk')
    else this.play(this.attacking ? 'attack' : this.moving ? 'walk' : 'idle')
  }

  setMoving(facing: Facing, moving: boolean): void {
    if (this.locked) return
    this.moving = moving
    if (this.attacking) return
    if (facing === this.facing && (moving ? 'walk' : 'idle') === this.anim) return
    this.facing = facing
    this.play(moving ? 'walk' : 'idle')
  }

  attack(): void {
    if (this.locked || this.attacking) return
    this.attacking = true
    this.play('attack')
  }

  /** Body drives the frame. Other layers copy it, so a missed event cannot drift. */
  sync(): void {
    const frame = this.body.anims.currentFrame
    if (!frame) return
    const index = asFrameIndex(frame)
    if (index !== this.frameIndex) this.applyFrame(index)
  }

  private fallbackItem(slot: string): string {
    const found = this.manifest.sheets.find((sheet) => sheet.slot === slot)
    if (!found) throw new Error(`No sheet for ${slot}`)
    return found.item
  }

  private ensureVariant(variant: string): void {
    const colors = this.manifest.variants.find((entry) => entry.id === variant)?.colors
    if (!colors) throw new Error(`Unknown palette ${variant}`)
    for (const sheet of this.manifest.sheets) {
      bakeVariant(this.scene, sourceKey(sheet.slot, sheet.item), textureKey(sheet.slot, sheet.item, variant), colors)
    }
  }

  private makeSprite(slot: string, item: string): Phaser.GameObjects.Sprite {
    const key = textureKey(slot, item, this.variant)
    const sprite = this.scene.add.sprite(0, 0, key, 0)
    sprite.setOrigin(0.5, PIVOT_Y)
    this.root.add(sprite)
    return sprite
  }

  private equip(): void {
    const head = this.loadout.head
    const hideHair = head ? this.manifest.hidesHair.includes(head) : false
    const lockOff = this.loadout.main ? this.manifest.twoHand.includes(this.loadout.main) : false
    for (const [slot, sprite] of this.sprites) {
      if (slot === 'body') continue
      const item = slot === 'hair' ? this.loadout.hair : this.loadout[slot as keyof Loadout]
      const hidden = !item || (slot === 'hair' && hideHair) || (slot === 'off' && lockOff)
      if (hidden || !item) {
        sprite.setVisible(false)
        continue
      }
      sprite.setTexture(textureKey(slot, item, this.variant), this.frameIndex)
      sprite.setOrigin(0.5, PIVOT_Y)
      sprite.setVisible(true)
    }
    if (this.body.texture.key !== textureKey('body', 'base', this.variant)) {
      this.body.setTexture(textureKey('body', 'base', this.variant), this.frameIndex)
      this.body.setOrigin(0.5, PIVOT_Y)
    }
    this.layout()
  }

  private play(anim: AnimName): void {
    this.anim = anim
    const spec = this.manifest.anims[anim]
    if (!spec) return
    const key = `${this.body.texture.key}:${anim}_${this.facing}`
    if (!this.body.anims.exists(key)) {
      this.body.anims.create({
        key,
        frames: this.scene.anims.generateFrameNumbers(this.body.texture.key, {
          frames: frameList(this.manifest, anim, this.facing),
        }),
        frameRate: spec.fps,
        repeat: anim === 'attack' ? 0 : -1,
      })
    }
    this.body.play(key)
    const frame = this.body.anims.currentFrame
    if (frame) this.applyFrame(asFrameIndex(frame))
  }

  private applyFrame(index: number): void {
    this.frameIndex = index
    for (const [slot, sprite] of this.sprites) {
      if (slot === 'body' || !sprite.visible) continue
      if (sprite.frame.name !== String(index)) sprite.setFrame(index)
    }
    this.layout()
  }

  private currentOrder(): string[] {
    const facing = this.facing === 'right' ? 'left' : this.facing
    const local = this.frameIndex % this.manifest.columns
    const override = this.manifest.orderOverrides[this.anim]?.[facing]?.[String(local)]
    return override ?? this.manifest.order[this.facing] ?? this.manifest.order.down ?? []
  }

  private layout(): void {
    let index = 0
    for (const slot of this.currentOrder()) {
      const sprite = this.sprites.get(slot)
      if (!sprite || !sprite.visible) continue
      this.root.moveTo(sprite, index)
      index += 1
    }
  }

  private readonly onFrame = (
    _anim: Phaser.Animations.Animation,
    frame: Phaser.Animations.AnimationFrame,
  ): void => {
    this.applyFrame(asFrameIndex(frame))
  }

  private readonly onComplete = (anim: Phaser.Animations.Animation): void => {
    if (!anim.key.includes('attack') || this.locked) return
    this.attacking = false
    this.play(this.moving ? 'walk' : 'idle')
  }
}
