export interface AnimSpec {
  row: number
  frames: number
  fps: number
}

export interface ItemDef {
  id: string
  name: string
}

export interface SlotDef {
  id: string
  name: string
  optional: boolean
  items: ItemDef[]
}

export interface VariantDef {
  id: string
  name: string
  colors: string[]
}

export interface PresetDef {
  id: string
  name: string
  variant: string
  loadout: Record<string, string>
}

export interface SheetDef {
  slot: string
  item: string
  file: string
}

export interface Manifest {
  frame: number
  columns: number
  rows: number
  pivot: [number, number]
  directions: string[]
  anims: Record<string, AnimSpec>
  order: Record<string, string[]>
  orderOverrides: Record<string, Record<string, Record<string, string[]>>>
  hidesHair: string[]
  twoHand: string[]
  slots: SlotDef[]
  sheets: SheetDef[]
  variants: VariantDef[]
  presets: PresetDef[]
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function needString(value: unknown, label: string): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`Paper doll manifest is missing ${label}`)
  }
  return value
}

function needNumber(value: unknown, label: string): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`Paper doll manifest is missing ${label}`)
  }
  return value
}

function needStringList(value: unknown, label: string): string[] {
  if (!Array.isArray(value) || value.some((entry) => typeof entry !== 'string')) {
    throw new Error(`Paper doll manifest is missing ${label}`)
  }
  return value
}

function readAnims(value: unknown): Record<string, AnimSpec> {
  if (!isRecord(value)) throw new Error('Paper doll manifest is missing anims')
  const anims: Record<string, AnimSpec> = {}
  for (const name of ['idle', 'walk', 'attack']) {
    const spec = value[name]
    if (!isRecord(spec)) throw new Error(`Paper doll manifest is missing anim ${name}`)
    anims[name] = {
      row: needNumber(spec.row, `${name} row`),
      frames: needNumber(spec.frames, `${name} frames`),
      fps: needNumber(spec.fps, `${name} fps`),
    }
  }
  return anims
}

function readOrder(value: unknown): Record<string, string[]> {
  if (!isRecord(value)) throw new Error('Paper doll manifest is missing draw order')
  const order: Record<string, string[]> = {}
  for (const facing of ['down', 'left', 'up', 'right']) {
    order[facing] = needStringList(value[facing], `order ${facing}`)
  }
  return order
}

function readOverrides(value: unknown): Manifest['orderOverrides'] {
  if (!isRecord(value)) return {}
  const overrides: Manifest['orderOverrides'] = {}
  for (const [anim, byFacing] of Object.entries(value)) {
    if (!isRecord(byFacing)) throw new Error(`Paper doll manifest override ${anim} is invalid`)
    overrides[anim] = {}
    for (const [facing, byFrame] of Object.entries(byFacing)) {
      if (!isRecord(byFrame)) throw new Error(`Paper doll manifest override ${anim} ${facing} is invalid`)
      overrides[anim][facing] = {}
      for (const [frame, slots] of Object.entries(byFrame)) {
        overrides[anim][facing][frame] = needStringList(slots, `override ${anim} ${facing} ${frame}`)
      }
    }
  }
  return overrides
}

function readSlots(value: unknown): SlotDef[] {
  if (!Array.isArray(value)) throw new Error('Paper doll manifest is missing slots')
  return value.map((entry, index) => {
    if (!isRecord(entry) || !Array.isArray(entry.items)) {
      throw new Error(`Paper doll manifest slot ${index} is invalid`)
    }
    const items = entry.items.map((item, itemIndex) => {
      if (!isRecord(item)) throw new Error(`Paper doll manifest item ${index}.${itemIndex} is invalid`)
      return { id: needString(item.id, 'item id'), name: needString(item.name, 'item name') }
    })
    return {
      id: needString(entry.id, 'slot id'),
      name: needString(entry.name, 'slot name'),
      optional: entry.optional === true,
      items,
    }
  })
}

function readVariants(value: unknown): VariantDef[] {
  if (!Array.isArray(value) || value.length === 0) {
    throw new Error('Paper doll manifest is missing palettes')
  }
  return value.map((entry, index) => {
    if (!isRecord(entry) || !Array.isArray(entry.colors) || entry.colors.length < 65) {
      throw new Error(`Paper doll manifest palette ${index} is invalid`)
    }
    const colors = entry.colors.map((color, colorIndex) => {
      if (typeof color !== 'string' || !color.startsWith('#')) {
        throw new Error(`Paper doll manifest palette ${index} color ${colorIndex} is invalid`)
      }
      return color
    })
    return { id: needString(entry.id, 'palette id'), name: needString(entry.name, 'palette name'), colors }
  })
}

function readPresets(value: unknown): PresetDef[] {
  if (!Array.isArray(value)) throw new Error('Paper doll manifest is missing presets')
  return value.map((entry, index) => {
    if (!isRecord(entry) || !isRecord(entry.loadout)) {
      throw new Error(`Paper doll manifest preset ${index} is invalid`)
    }
    const loadout: Record<string, string> = {}
    for (const [slot, item] of Object.entries(entry.loadout)) {
      if (typeof item !== 'string') throw new Error(`Paper doll manifest preset ${index} is invalid`)
      loadout[slot] = item
    }
    return {
      id: needString(entry.id, 'preset id'),
      name: needString(entry.name, 'preset name'),
      variant: needString(entry.variant, 'preset palette'),
      loadout,
    }
  })
}

function readSheets(value: unknown): SheetDef[] {
  if (!Array.isArray(value) || value.length === 0) {
    throw new Error('Paper doll manifest is missing sheets')
  }
  return value.map((entry, index) => {
    if (!isRecord(entry)) throw new Error(`Paper doll manifest sheet ${index} is invalid`)
    return {
      slot: needString(entry.slot, 'sheet slot'),
      item: needString(entry.item, 'sheet item'),
      file: needString(entry.file, 'sheet file'),
    }
  })
}

export function readManifest(value: unknown): Manifest {
  if (!isRecord(value)) throw new Error('Paper doll manifest is not an object')
  const pivot = value.pivot
  if (!Array.isArray(pivot) || pivot.length !== 2 || typeof pivot[0] !== 'number' || typeof pivot[1] !== 'number') {
    throw new Error('Paper doll manifest is missing the pivot')
  }
  return {
    frame: needNumber(value.frame, 'frame size'),
    columns: needNumber(value.columns, 'columns'),
    rows: needNumber(value.rows, 'rows'),
    pivot: [pivot[0], pivot[1]],
    directions: needStringList(value.directions, 'directions'),
    anims: readAnims(value.anims),
    order: readOrder(value.order),
    orderOverrides: readOverrides(value.orderOverrides),
    hidesHair: needStringList(value.hidesHair, 'hidesHair'),
    twoHand: needStringList(value.twoHand, 'twoHand'),
    slots: readSlots(value.slots),
    sheets: readSheets(value.sheets),
    variants: readVariants(value.variants),
    presets: readPresets(value.presets),
  }
}
