import Phaser from 'phaser'
import { assetUrl } from './assets'
import { readManifest } from './manifest'
import { PlayScene } from './play'
import './style.css'

const WIDTH = 512
const HEIGHT = 384

function fit(game: Phaser.Game): void {
  const panel = document.getElementById('panel')
  const stacked = window.matchMedia('(max-width: 860px)').matches
  const panelWidth = stacked ? 0 : (panel?.getBoundingClientRect().width ?? 0)
  const availW = Math.max(1, window.innerWidth - panelWidth)
  const availH = stacked ? Math.max(220, Math.floor(window.innerHeight * 0.56)) : window.innerHeight
  const zoom = Math.max(1, Math.floor(Math.min(availW / WIDTH, availH / HEIGHT)))
  game.scale.setZoom(zoom)
}

function showError(error: unknown): void {
  const stage = document.getElementById('stage')
  const message = error instanceof Error ? error.message : 'The paper doll test failed to start'
  if (stage) stage.textContent = message
}

async function main(): Promise<void> {
  const response = await fetch(assetUrl('hero/manifest.json'))
  if (!response.ok) throw new Error('Could not load the paper doll manifest')
  const manifest = readManifest(await response.json())
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent: 'stage',
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: '#12161c',
    pixelArt: true,
    roundPixels: true,
    antialias: false,
    banner: false,
    scale: {
      mode: Phaser.Scale.NONE,
      autoCenter: Phaser.Scale.NO_CENTER,
      zoom: 2,
    },
    scene: [new PlayScene(manifest)],
    input: { keyboard: true },
  })
  const resize = (): void => fit(game)
  window.addEventListener('resize', resize)
  game.events.once('ready', resize)
  resize()
}

main().catch(showError)
