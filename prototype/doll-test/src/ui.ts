import type { Manifest } from './manifest'
import type { Loadout } from './doll'
import { loadoutFrom } from './doll'

export const stick = { x: 0, y: 0, held: false }

function byId<T extends HTMLElement>(id: string, kind: new () => T): T {
  const node = document.getElementById(id)
  if (!(node instanceof kind)) throw new Error(`Missing #${id}`)
  return node
}

export function bindStick(): void {
  const pad = byId('pad', HTMLDivElement)
  const nub = byId('nub', HTMLDivElement)
  const radius = 42
  let pointerId: number | null = null

  const place = (clientX: number, clientY: number): void => {
    const rect = pad.getBoundingClientRect()
    let dx = clientX - (rect.left + rect.width / 2)
    let dy = clientY - (rect.top + rect.height / 2)
    const len = Math.hypot(dx, dy)
    if (len > radius) {
      dx = (dx / len) * radius
      dy = (dy / len) * radius
    }
    nub.style.transform = `translate(${dx}px, ${dy}px)`
    const nx = dx / radius
    const ny = dy / radius
    if (Math.hypot(nx, ny) < 0.2) {
      stick.x = 0
      stick.y = 0
      stick.held = false
      return
    }
    stick.x = nx
    stick.y = ny
    stick.held = true
  }

  const release = (event: PointerEvent): void => {
    if (event.pointerId !== pointerId) return
    pointerId = null
    stick.x = 0
    stick.y = 0
    stick.held = false
    nub.style.transform = 'translate(0px, 0px)'
  }

  pad.addEventListener('pointerdown', (event) => {
    pointerId = event.pointerId
    pad.setPointerCapture(event.pointerId)
    place(event.clientX, event.clientY)
  })
  pad.addEventListener('pointermove', (event) => {
    if (event.pointerId !== pointerId) return
    place(event.clientX, event.clientY)
  })
  pad.addEventListener('pointerup', release)
  pad.addEventListener('pointercancel', release)
}

export interface Wardrobe {
  loadout: Loadout
  variant: string
  onChange: () => void
}

export function mountWardrobe(manifest: Manifest, wardrobe: Wardrobe): void {
  const palette = byId('palette', HTMLSelectElement)
  const presets = byId('presets', HTMLDivElement)
  const slots = byId('slots', HTMLDivElement)
  const turntable = byId('turntable', HTMLInputElement)
  const attack = byId('attack', HTMLButtonElement)
  const twohand = byId('twohand', HTMLParagraphElement)
  const selects = new Map<string, HTMLSelectElement>()

  const addOption = (select: HTMLSelectElement, value: string, label: string): void => {
    const option = document.createElement('option')
    option.value = value
    option.textContent = label
    select.append(option)
  }

  for (const variant of manifest.variants) addOption(palette, variant.id, variant.name)
  palette.value = wardrobe.variant
  palette.addEventListener('change', () => {
    wardrobe.variant = palette.value
    wardrobe.onChange()
  })

  for (const preset of manifest.presets) {
    const button = document.createElement('button')
    button.type = 'button'
    button.textContent = preset.name
    button.addEventListener('click', () => {
      wardrobe.loadout = loadoutFrom(preset.loadout)
      wardrobe.variant = preset.variant
      palette.value = preset.variant
      reflect()
      wardrobe.onChange()
    })
    presets.append(button)
  }

  for (const slot of manifest.slots) {
    const row = document.createElement('label')
    row.className = 'slot'
    row.append(document.createTextNode(slot.name))
    const select = document.createElement('select')
    select.id = `slot-${slot.id}`
    select.setAttribute('aria-label', slot.name)
    if (slot.optional) addOption(select, '', 'None')
    for (const item of slot.items) addOption(select, item.id, item.name)
    select.addEventListener('change', () => {
      const value = select.value
      if (slot.id === 'hair') {
        if (value) wardrobe.loadout.hair = value
      } else if (value) {
        wardrobe.loadout[slot.id as Exclude<keyof Loadout, 'hair'>] = value
      } else {
        delete wardrobe.loadout[slot.id as Exclude<keyof Loadout, 'hair'>]
      }
      if (wardrobe.loadout.main && manifest.twoHand.includes(wardrobe.loadout.main)) {
        delete wardrobe.loadout.off
      }
      reflect()
      wardrobe.onChange()
    })
    row.append(select)
    slots.append(row)
    selects.set(slot.id, select)
  }

  const reflect = (): void => {
    for (const [slot, select] of selects) {
      const value = slot === 'hair' ? wardrobe.loadout.hair : (wardrobe.loadout[slot as keyof Loadout] ?? '')
      select.value = value
    }
    const bow = Boolean(wardrobe.loadout.main && manifest.twoHand.includes(wardrobe.loadout.main))
    const off = selects.get('off')
    if (off) off.disabled = bow
    twohand.hidden = !bow
  }

  turntable.addEventListener('change', () => {
    document.dispatchEvent(new CustomEvent('doll-turntable', { detail: turntable.checked }))
  })
  attack.addEventListener('click', () => {
    document.dispatchEvent(new CustomEvent('doll-attack'))
  })
  reflect()
}
