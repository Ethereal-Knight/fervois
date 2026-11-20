// One-room (then a second room) splat chamber. Veris is an Ink Studio character:
// each gear slot is a tagged solid on a bone, so the main hand can swap without
// rebaking the room.

export const PAL = [
  0x07060e, 0x14101c, 0x241c38, 0x1a332c, 0x3a4568, 0x5d5f6b, 0xb9bcc6, 0xe4e2ee,
  0xf0d2c2, 0x1b1d26, 0x5b4a8a, 0xc9b6ff, 0x3ee0ff, 0xffe14a, 0xff4ad8, 0xf7f4ff
]

export const CAMERA = { yaw: 0.7, pitch: 0.62, fov: (42 * Math.PI) / 180, rest: 7.2, combat: 9.4 }
export const ROOM = { half: 6.35, gap: 1.55 }
export const ROOM2_Z = -28

const SKIN = [8, 7, 5]
const HAIR = [9, 1, 4]
const SILVER = [5, 6, 7]
const COAT = [1, 4, 6]
const VIOLET = [10, 11, 15]
const BOOT = [9, 1, 5]

function part(T, bone, gear) {
  const tag = T(bone)
  if (gear) tag.tag.gear = gear
  return tag
}

function verisSpec(gearIndex) {
  return {
    height: 1.72,
    hp: 8,
    mortal: true,
    res: 0.06,
    reach: 1.45,
    atk: 'slash',
    fx: 13,
    dust: 4,
    speed: { walk: 3.4, run: 5.2, dash: 14 },
    x0: 0,
    pts: {
      hip: [0, 0.9, 0],
      chest: [0, 1.16, 0],
      hem: [0, 0.5, 0],
      neck: [0, 1.4, 0],
      sock: [0.02, 0.58, 0.11],
      ank: [0.04, 0.14, 0.12],
      sho: [0.08, 1.3, 0.2],
      hand: [0.32, 0.98, 0.26]
    },
    legs: { r0: 0.055, r1: 0.045, mat: [5, 6, 7], foot: false },
    tails: [
      { at: [0.12, 0.62, 0.08], dir: [-0.25, -0.95, 0.12], n: 4, seg: 0.16, r0: 0.07, r1: 0.03, mat: COAT },
      { at: [0.02, 0.58, 0], dir: [-0.15, -0.98, 0], n: 5, seg: 0.15, r0: 0.08, r1: 0.028, mat: COAT },
      { at: [0.12, 0.62, -0.08], dir: [-0.25, -0.95, -0.12], n: 4, seg: 0.16, r0: 0.07, r1: 0.03, mat: COAT }
    ],
    world: {
      height(x, z) {
        return onPlatform(x, z) ? 0 : -40
      }
    },
    sculpt(S, T) {
      const orig = S.capture.bind(S)
      let n = 0
      S.capture = (prim, ...rest) => {
        const index = n
        n += 1
        orig(prim, ...rest)
        const gear = prim.tag && prim.tag.gear
        if (gear) {
          const list = gearIndex[gear] || (gearIndex[gear] = [])
          list.push(index)
        }
      }
      const head = part(T, 'head')
      const chest = part(T, 'chest')
      const hem = part(T, 'hem')
      const arm = part(T, 'arm')
      const blade = part(T, 'item', 'blade')
      const focus = part(T, 'item', 'focus')
      S.ball([0.04, 1.05, 0], [0.2, 0.32, 0.24], { r: COAT }, hem)
      S.ball([-0.02, 0.72, 0], [0.26, 0.38, 0.3], { r: COAT }, hem)
      S.ball([0.06, 1.2, 0], [0.16, 0.22, 0.2], { r: [1, 9, 5] }, chest)
      S.ball([0.14, 1.18, 0], [0.06, 0.14, 0.13], { r: SILVER }, chest)
      S.ball([0.18, 1.2, 0], 0.04, { r: [11, 15], em: true }, chest)
      S.ball([0.16, 1.38, 0.16], 0.06, { r: SILVER }, chest)
      S.ball([0.16, 1.38, -0.16], 0.06, { r: SILVER }, chest)
      S.ball([0.06, 1.52, 0], [0.13, 0.15, 0.14], { r: SKIN }, head)
      S.ball([0.02, 1.62, 0], [0.16, 0.16, 0.17], { r: HAIR }, head)
      S.tube([[0.04, 1.58, 0], [-0.08, 1.15, 0.02], [-0.16, 0.62, 0.04]], 0.11, 0.04, HAIR, head)
      S.tube([[0.06, 1.58, 0.1], [-0.02, 1.2, 0.12], [-0.08, 0.78, 0.1]], 0.03, 0.015, SILVER, head)
      S.torus([0.04, 1.66, 0], 0.13, 0.016, { r: SILVER }, head)
      S.ball([0.14, 1.54, 0.05], 0.018, { r: [11], em: true }, head)
      S.ball([0.14, 1.54, -0.05], 0.018, { r: [11], em: true }, head)
      for (const s of [-1, 1]) {
        const foot = part(T, s < 0 ? 'footL' : 'footR')
        const leg = part(T, s < 0 ? 'legL' : 'legR')
        const z = s * 0.12
        S.ball([0.05, 0.4, z], [0.07, 0.12, 0.07], { r: SILVER }, leg)
        S.ball([0.06, 0.22, z], [0.08, 0.14, 0.08], { r: BOOT }, foot)
        S.ball([0.1, 0.18, z], [0.05, 0.08, 0.045], { r: SILVER }, foot)
        S.ball([0.02, 0.05, z], [0.05, 0.07, 0.05], { r: BOOT }, foot)
        S.ball([0.1, 0.035, z], [0.1, 0.025, 0.07], { r: [9, 1, 6] }, foot)
      }
      S.ball([0.32, 0.98, 0.26], [0.07, 0.05, 0.06], { r: SILVER }, arm)
      S.tube([[0.18, 1.2, 0.22], [0.32, 0.98, 0.26]], 0.045, 0.035, SILVER, arm)
      S.tube([[0.36, 1.02, 0.26], [0.85, 1.18, 0.26]], 0.035, 0.012, SILVER, blade)
      S.tube([[0.4, 1.0, 0.29], [0.82, 1.16, 0.3]], 0.012, 0.008, VIOLET, blade)
      S.ball([0.34, 1.0, 0.26], [0.04, 0.02, 0.07], { r: [5, 10, 11] }, blade)
      S.tube([[0.32, 0.98, 0.26], [0.32, 1.35, 0.26]], 0.02, 0.018, SILVER, focus)
      S.ball([0.32, 1.42, 0.26], 0.07, { r: [11, 14, 15], em: true }, focus)
    }
  }
}

export function onPlatform(x, z) {
  const half = ROOM.half
  if (Math.abs(x) <= half && Math.abs(z) <= half) return true
  if (Math.abs(x) <= half && Math.abs(z - ROOM2_Z) <= half) return true
  return false
}

function bakeProp(kit, sculpt) {
  const { makeBuilder, makeSculpt } = kit
  const B = makeBuilder(11, PAL)
  const S = makeSculpt(B)
  S.res = 0.1
  S.sun = S.sun
  sculpt(S)
  S.bake()
  const world = B.finish({ cam: { target: [0, 0.4, 0], dist: 4, pitch: 0.4, yaw: 0.4 } })
  return { data: world.data, count: world.count }
}

function flashMap(proto) {
  const map = {}
  const data = proto.data
  for (let i = 0; i < proto.count; i++) {
    const packed = data[i * 16 + 7] | 0
    const r = packed & 255
    const g = (packed >> 8) & 255
    const b = (packed >> 16) & 255
    const hex = '#' + [r, g, b].map(n => n.toString(16).padStart(2, '0')).join('')
    map[hex] = '#ffffff'
    if (Object.keys(map).length >= 16) break
  }
  return map
}

function placeEnemies(count) {
  const list = []
  if (count == null) {
    const story = [
      ['wisp', -2.4, 1.2],
      ['wisp', 2.2, -0.4],
      ['wisp', 0.4, -2.6],
      ['grub', -3.2, -1.6],
      ['grub', 3.1, 1.8],
      ['grub', 1.4, 2.8]
    ]
    story.forEach(([kind, x, z], i) => {
      list.push({ id: kind + '-' + i, kind, x, z, room: 0, hp: kind === 'wisp' ? 2 : 3 })
    })
    ;[[-2.2, -2], [2.4, -1.2], [0, -3.4], [1.6, 2.2]].forEach(([x, z], i) => {
      list.push({ id: 'wisp-b' + i, kind: 'wisp', x, z: ROOM2_Z + z, room: 1, hp: 2 })
    })
    return list
  }
  const side = Math.ceil(Math.sqrt(count))
  const span = ROOM.half * 1.7
  for (let i = 0; i < count; i++) {
    const col = i % side
    const row = Math.floor(i / side)
    const x = -span / 2 + (span * (col + 0.5)) / side
    const z = -span / 2 + (span * (row + 0.5)) / side
    list.push({ id: 'wisp-' + i, kind: 'wisp', x, z, room: 0, hp: 1 })
  }
  return list
}

export function createSession(kit, options = {}) {
  const { makeBuilder, makeSculpt, KIT: K } = kit
  const gear = {}
  const stress = Number.isFinite(options.enemies)
  const roster = placeEnemies(stress ? options.enemies : null)
  const B = makeBuilder(7, PAL)
  const S = makeSculpt(B)
  S.res = 0.32
  S.sun = [-0.35, 0.82, 0.4]
  const stone = { r: [2, 3, 1] }
  const metal = { r: [1, 5, 6] }
  for (const cz of [0, ROOM2_Z]) {
    S.box([0, -0.2, cz], [ROOM.half, 0.2, ROOM.half], stone, { rd: 0.08 })
    S.box([-1.35, 0.7, cz - ROOM.half + 0.35], [0.16, 0.7, 0.16], metal)
    S.box([1.35, 0.7, cz - ROOM.half + 0.35], [0.16, 0.7, 0.16], metal)
    S.box([0, 1.35, cz - ROOM.half + 0.35], [1.5, 0.12, 0.14], metal)
  }
  S.box([-3.4, 0.28, 1.6], [0.45, 0.28, 0.35], { r: [2, 4, 5] }, { rd: 0.06 })
  S.box([2.8, 0.18, -1.2], [0.3, 0.18, 0.4], { r: [3, 2, 5] }, { rd: 0.05 })
  S.box([-2.2, 0.22, ROOM2_Z + 1.4], [0.4, 0.22, 0.3], { r: [2, 10, 4] }, { rd: 0.05 })
  S.bake()

  const pool = K.pool(B, 96)
  const player = K.character(B, verisSpec(gear), 3.2)
  const world = B.finish({
    cam: { target: [0, 1.1, 3.2], dist: CAMERA.rest, pitch: CAMERA.pitch, yaw: CAMERA.yaw, fov: CAMERA.fov },
    detail: 12,
    dither: 0.2
  })
  const at = world.count - player.total
  player.bind(world, at)
  const stage = K.stage(world)
  const motes = stage.add(K.particles(stage, pool, { ground: () => -8 }))

  const wisp = bakeProp(kit, S2 => {
    S2.ball([0, 0.55, 0], 0.18, { r: [12, 4, 11], em: true })
    S2.ball([0, 0.6, 0.08], 0.045, { r: [1, 9] })
    S2.ball([0, 0.02, 0], [0.16, 0.015, 0.12], { r: [1, 1, 2] })
  })
  const grub = bakeProp(kit, S2 => {
    S2.ball([0, 0.26, 0], [0.34, 0.16, 0.24], { r: [3, 2, 4] })
    S2.ball([0.1, 0.32, 0.08], 0.04, { r: [13, 15], em: true })
    S2.ball([0, 0.02, 0], [0.24, 0.015, 0.16], { r: [1, 1, 2] })
  })
  const crystal = bakeProp(kit, S2 => {
    S2.ball([0, 0.9, 0], 0.14, { r: [13, 15, 11], em: true })
  })

  const enemies = roster.map(row => ({
    ...row,
    y: row.kind === 'wisp' ? 0 : 0,
    hp: row.hp,
    maxHp: row.hp,
    alive: true,
    flash: 0,
    cool: 0
  }))
  const gates = [0, ROOM2_Z].map(cz => ({
    id: 'gate-' + cz,
    x: 0,
    y: 0,
    z: cz - ROOM.half + 0.2,
    lit: false
  }))

  const session = {
    world,
    player,
    stage,
    motes,
    at,
    gear,
    hand: 'blade',
    enemies,
    gates,
    prototypes: { wisp, grub, crystal },
    flashes: { wisp: flashMap(wisp), grub: flashMap(grub) },
    room: 0,
    glint: 0,
    dashes: 2,
    dashRegen: 0,
    combo: 0,
    comboUntil: 0,
    attackWas: false,
    dashWas: false,
    shake: 0,
    banner: '',
    bannerT: 0,
    travel: false,
    stress,
    announced: false,
    moteAt: 0,
    time: 0
  }
  player.update(1 / 60, { move: 0, mz: 0 }, 0)
  applyGear(session)
  return session
}

export function applyGear(session) {
  const data = session.world.data
  const hide = session.hand === 'blade' ? session.gear.focus : session.gear.blade
  if (!hide) return
  for (const index of hide) {
    const o = (session.at + index) * 16
    data[o + 1] = -50
    data[o + 3] = 0
  }
}

function roomOrigin(room) {
  return room === 0 ? 0 : ROOM2_Z
}

function roomCleared(session, room) {
  return session.enemies.every(enemy => enemy.room !== room || !enemy.alive)
}

export function stickToWorld(x, y) {
  const yaw = CAMERA.yaw
  const lookX = -Math.sin(yaw)
  const lookZ = -Math.cos(yaw)
  const rightX = Math.cos(yaw)
  const rightZ = -Math.sin(yaw)
  return {
    move: x * rightX + y * lookX,
    mz: x * rightZ + y * lookZ
  }
}

export function step(session, dt, input) {
  dt = Math.max(0, Math.min(0.05, dt))
  session.time += dt
  const st = session.player.st
  const events = { hits: [], deaths: [], shake: 0, cleared: false, travel: false }

  if (session.dashes < 2) {
    session.dashRegen += dt
    if (session.dashRegen >= 1.35) {
      session.dashRegen = 0
      session.dashes = Math.min(2, session.dashes + 1)
    }
  }
  const dashEdge = input.dash && !session.dashWas
  session.dashWas = input.dash
  const canDash = dashEdge && session.dashes > 0 && st.dash <= 0 && st.dashAge > 0.45 && st.dead < 0
  if (canDash) session.dashes -= 1

  const attackEdge = input.attack && !session.attackWas
  session.attackWas = input.attack
  let attack = false
  if (st.dead < 0 && st.atk < 0 && (attackEdge || (input.attack && session.time < session.comboUntil))) {
    if (session.time < session.comboUntil) session.combo = session.combo >= 3 ? 1 : session.combo + 1
    else session.combo = 1
    session.comboUntil = session.time + 0.48
    attack = true
  }

  const stick = stickToWorld(input.x || 0, input.y || 0)
  session.player.update(dt, {
    move: stick.move,
    mz: stick.mz,
    attack,
    dash: canDash
  }, session.time)
  const half = ROOM.half - 0.25
  const origin = roomOrigin(session.room)
  st.x = Math.max(-half, Math.min(half, st.x))
  st.z = Math.max(origin - half, Math.min(origin + half, st.z))
  if (st.y < 0 && onPlatform(st.x, st.z)) {
    st.y = 0
    st.gh = 0
    st.vy = 0
    st.ground = true
  }
  applyGear(session)

  if (st.dead >= 0) {
    session.stage.update(dt, session.time)
    return events
  }

  const fx = Math.cos(st.face)
  const fz = Math.sin(st.face)
  const reach = session.combo >= 3 ? 1.9 : session.combo === 2 ? 1.55 : 1.35
  if (session.player.striking()) {
    st.connected = true
    for (const enemy of session.enemies) {
      if (!enemy.alive || enemy.room !== session.room) continue
      const dx = enemy.x - st.x
      const dz = enemy.z - st.z
      const dist = Math.hypot(dx, dz)
      if (dist > reach || dx * fx + dz * fz < dist * 0.25) continue
      enemy.hp -= session.combo >= 3 ? 2 : 1
      enemy.flash = 0.09
      const num = { x: enemy.x, y: 1.3, z: enemy.z, text: String(session.combo >= 3 ? 2 : 1), age: 0 }
      events.hits.push(num)
      if (session.combo >= 3) {
        session.shake = Math.max(session.shake, 1)
        events.shake = 1
      }
      if (enemy.hp <= 0) {
        enemy.alive = false
        session.glint += 3
        events.deaths.push(enemy)
      }
    }
  }

  for (const enemy of session.enemies) {
    if (!enemy.alive) continue
    enemy.flash = Math.max(0, enemy.flash - dt)
    enemy.cool = Math.max(0, enemy.cool - dt)
    if (enemy.room !== session.room) continue
    const dx = st.x - enemy.x
    const dz = st.z - enemy.z
    const dist = Math.hypot(dx, dz) || 0.0001
    const speed = enemy.kind === 'wisp' ? 1.7 : 1.25
    if (dist > 0.72) {
      enemy.x += (dx / dist) * speed * dt
      enemy.z += (dz / dist) * speed * dt
      enemy.x = Math.max(-half, Math.min(half, enemy.x))
      enemy.z = Math.max(origin - half, Math.min(origin + half, enemy.z))
    }
    const dashing = st.dash > 0 && st.dashAge >= 0
    if (dist < 0.78 && enemy.cool <= 0 && !dashing && st.hitT <= 0) {
      session.player.hurt((st.x - enemy.x) / dist, (st.z - enemy.z) / dist)
      enemy.cool = 0.7
    }
  }

  if (roomCleared(session, session.room)) {
    for (const gate of session.gates) {
      const mouth = roomOrigin(session.room) - ROOM.half
      if (!gate.lit && Math.abs(gate.z - mouth) < 1) gate.lit = true
    }
    if (!session.announced) {
      session.announced = true
      session.banner = 'CHAMBER CLEARED'
      session.bannerT = 2.4
      events.cleared = true
    }
  }
  if (session.bannerT > 0) session.bannerT -= dt
  else session.banner = ''

  const gate = session.gates[session.room]
  if (!session.travel && gate && gate.lit && session.room === 0 && Math.abs(st.x) < ROOM.gap && st.z < origin - half + 0.85) {
    session.travel = true
    events.travel = true
  }

  if (session.time >= session.moteAt) {
    const ox = (Math.random() - 0.5) * 16
    const oz = roomOrigin(session.room) + (Math.random() - 0.5) * 16
    session.motes.dust([ox, 0.4 + Math.random() * 2.2, oz], 1, [2, 4, 10])
    session.moteAt = session.time + 0.08
  }
  session.stage.update(dt, session.time)
  session.shake *= Math.pow(0.04, dt)
  return events
}

export function arrive(session) {
  session.room = 1
  session.travel = false
  session.announced = false
  session.banner = ''
  const st = session.player.st
  st.x = 0
  st.z = ROOM2_Z + 4.2
  st.vx = 0
  st.vz = 0
  st.y = 0
  session.player.update(1 / 60, { move: 0, mz: 0 }, session.time)
  applyGear(session)
}

export function cameraFor(session) {
  const st = session.player.st
  const busy = session.enemies.some(enemy => enemy.alive && enemy.room === session.room &&
    Math.hypot(enemy.x - st.x, enemy.z - st.z) < 5.5)
  let dist = busy || st.atk >= 0 ? CAMERA.combat : CAMERA.rest
  if (session.stress) dist = 13.5
  const jx = (Math.random() - 0.5) * session.shake * 0.18
  const jz = (Math.random() - 0.5) * session.shake * 0.18
  return {
    target: [st.x + jx, 1.15, st.z + jz],
    dist,
    yaw: CAMERA.yaw,
    pitch: CAMERA.pitch,
    fov: CAMERA.fov
  }
}
