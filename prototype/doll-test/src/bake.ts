import Phaser from 'phaser'

const COLUMNS = 8
const ROWS = 12
const FRAME = 64

function parseHex(hex: string): [number, number, number, number] {
  const body = hex.slice(1)
  const r = Number.parseInt(body.slice(0, 2), 16)
  const g = Number.parseInt(body.slice(2, 4), 16)
  const b = Number.parseInt(body.slice(4, 6), 16)
  const a = body.length >= 8 ? Number.parseInt(body.slice(6, 8), 16) : 255
  if ([r, g, b, a].some((channel) => Number.isNaN(channel))) {
    throw new Error(`Bad palette color ${hex}`)
  }
  return [r, g, b, a]
}

function sourceImage(scene: Phaser.Scene, key: string): HTMLImageElement | HTMLCanvasElement {
  const texture = scene.textures.get(key)
  const image = texture.getSourceImage()
  if (image instanceof HTMLImageElement || image instanceof HTMLCanvasElement) return image
  throw new Error(`Sheet ${key} did not load as an image`)
}

/** Indexed sheets store the palette index in red, with green 0 and blue 1. */
export function bakeVariant(
  scene: Phaser.Scene,
  sourceKey: string,
  destKey: string,
  colors: readonly string[],
): void {
  if (scene.textures.exists(destKey)) return
  const image = sourceImage(scene, sourceKey)
  const width = image instanceof HTMLImageElement ? image.naturalWidth : image.width
  const height = image instanceof HTMLImageElement ? image.naturalHeight : image.height
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  if (!ctx) throw new Error('Could not color a paper doll sheet')
  ctx.imageSmoothingEnabled = false
  ctx.drawImage(image, 0, 0)
  const pixels = ctx.getImageData(0, 0, width, height)
  const data = pixels.data
  const lut = colors.map(parseHex)
  let checked = false
  for (let i = 0; i < data.length; i += 4) {
    if (data[i + 3] === 0) continue
    const index = data[i] ?? 0
    if (!checked) {
      if ((data[i + 1] ?? 0) !== 0 || (data[i + 2] ?? 0) !== 1) {
        throw new Error(`Sheet ${sourceKey} is not a material-index image`)
      }
      checked = true
    }
    const mapped = lut[index]
    if (!mapped || mapped[3] === 0) {
      data[i + 3] = 0
      continue
    }
    data[i] = mapped[0]
    data[i + 1] = mapped[1]
    data[i + 2] = mapped[2]
    data[i + 3] = mapped[3]
  }
  ctx.putImageData(pixels, 0, 0)
  const texture = scene.textures.addCanvas(destKey, canvas)
  if (!texture) throw new Error(`Could not store ${destKey}`)
  for (let row = 0; row < ROWS; row += 1) {
    for (let col = 0; col < COLUMNS; col += 1) {
      texture.add(row * COLUMNS + col, 0, col * FRAME, row * FRAME, FRAME, FRAME)
    }
  }
  texture.setFilter(Phaser.Textures.FilterMode.NEAREST)
}

export function textureKey(slot: string, item: string, variant: string): string {
  return `doll.${slot}.${item}.${variant}`
}

export function sourceKey(slot: string, item: string): string {
  return `src.${slot}.${item}`
}
