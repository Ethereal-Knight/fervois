import { createRenderer, createSplatInstances } from '@shapeshift-labs/ink-studio'
import { arrive, cameraFor, createSession, step } from './world.js'

const ink = await import(new URL('ink-studio.mjs', document.baseURI).href)
const { makeBuilder, makeSculpt, KIT, PixelLook } = ink

const canvas = document.querySelector('#view')
const hud = {
  hp: document.querySelector('#hp-fill'),
  hpText: document.querySelector('#hp-text'),
  dashes: [...document.querySelectorAll('[data-dash]')],
  glint: document.querySelector('#glint'),
  room: document.querySelector('#room'),
  fps: document.querySelector('#fps'),
  banner: document.querySelector('#banner'),
  title: document.querySelector('#title'),
  fade: document.querySelector('#fade'),
  dead: document.querySelector('#dead'),
  swap: document.querySelector('#swap'),
  stress: document.querySelector('#stress'),
  numbers: document.querySelector('#numbers')
}

const params = new URLSearchParams(location.search)
const enemies = params.has('enemies') ? Number(params.get('enemies')) : null
const closeShot = params.has('close')
const bench = params.has('bench')
const session = createSession({ makeBuilder, makeSculpt, KIT }, {
  enemies: Number.isFinite(enemies) && enemies > 0 ? Math.min(500, enemies) : undefined
})

const placements = []
for (const enemy of session.enemies) {
  placements.push({
    id: enemy.id,
    prototype: enemy.kind,
    position: [enemy.x, enemy.y, enemy.z]
  })
}
for (const gate of session.gates) {
  placements.push({
    id: gate.id,
    prototype: 'crystal',
    position: [gate.x, gate.y, gate.z],
    visible: false
  })
}
const instances = createSplatInstances(session.prototypes, placements)
const renderer = createRenderer(canvas, { toolkit: { KIT, PixelLook } })

const keys = new Set()
const pointer = { x: 0, y: 0, attack: false, dash: false }
let swapEdge = false
let travelLock = false
const floats = []
let fpsFrames = 0
let fpsTime = 0
let shownFps = 0
const samples = []
const renderSamples = []

const rooms = ['I-1', 'I-2']
const titles = ['Ocular Yard', 'Violet Stair']

function showTitle(text) {
  hud.title.textContent = text
  hud.title.hidden = false
  window.setTimeout(() => {
    hud.title.hidden = true
  }, 1700)
}

function resize() {
  const width = Math.max(240, Math.min(480, Math.floor(window.innerWidth / 2)))
  const height = Math.max(135, Math.round(width * 9 / 16))
  canvas.width = width
  canvas.height = height
}

function pressed(code) {
  return keys.has(code)
}

function readMove() {
  let x = pointer.x
  let y = pointer.y
  if (pressed('KeyA') || pressed('ArrowLeft')) x -= 1
  if (pressed('KeyD') || pressed('ArrowRight')) x += 1
  if (pressed('KeyW') || pressed('ArrowUp')) y += 1
  if (pressed('KeyS') || pressed('ArrowDown')) y -= 1
  const len = Math.hypot(x, y)
  if (len > 1) {
    x /= len
    y /= len
  }
  return { x, y }
}

function syncInstances() {
  for (const enemy of session.enemies) {
    const patch = {
      position: [enemy.x, enemy.y, enemy.z],
      visible: enemy.alive
    }
    if (enemy.flash > 0) patch.palette = session.flashes[enemy.kind]
    else patch.palette = {}
    instances.update(enemy.id, patch)
  }
  for (const gate of session.gates) {
    instances.update(gate.id, { visible: gate.lit, position: [gate.x, gate.y, gate.z] })
  }
}

function project(x, y, z, cam) {
  const dist = cam.dist
  const eye = [
    cam.target[0] + dist * Math.cos(cam.pitch) * Math.sin(cam.yaw),
    cam.target[1] + dist * Math.sin(cam.pitch),
    cam.target[2] + dist * Math.cos(cam.pitch) * Math.cos(cam.yaw)
  ]
  const fx = cam.target[0] - eye[0]
  const fy = cam.target[1] - eye[1]
  const fz = cam.target[2] - eye[2]
  const fl = Math.hypot(fx, fy, fz) || 1
  const f = [fx / fl, fy / fl, fz / fl]
  const rx = f[1] * 0 - f[2] * 1
  const ry = f[2] * 0 - f[0] * 0
  const rz = f[0] * 1 - f[1] * 0
  const rl = Math.hypot(rx, ry, rz) || 1
  const right = [rx / rl, ry / rl, rz / rl]
  const up = [
    right[1] * f[2] - right[2] * f[1],
    right[2] * f[0] - right[0] * f[2],
    right[0] * f[1] - right[1] * f[0]
  ]
  const px = x - eye[0]
  const py = y - eye[1]
  const pz = z - eye[2]
  const cz = px * f[0] + py * f[1] + pz * f[2]
  if (cz < 0.2) return null
  const cx = px * right[0] + py * right[1] + pz * right[2]
  const cy = px * up[0] + py * up[1] + pz * up[2]
  const scale = (canvas.height / 2) / Math.tan(cam.fov / 2)
  return {
    x: canvas.width / 2 + (cx / cz) * scale,
    y: canvas.height / 2 - (cy / cz) * scale
  }
}

function paintNumbers(cam) {
  hud.numbers.replaceChildren()
  const rect = canvas.getBoundingClientRect()
  const sx = rect.width / canvas.width
  const sy = rect.height / canvas.height
  for (const num of floats) {
    const p = project(num.x, num.y, num.z, cam)
    if (!p) continue
    const node = document.createElement('span')
    node.textContent = num.text
    node.style.left = p.x * sx + 'px'
    node.style.top = p.y * sy + 'px'
    hud.numbers.append(node)
  }
}

function paintHud() {
  const st = session.player.st
  const max = session.player.spec.hp
  const hp = Math.max(0, st.hp)
  hud.hp.style.width = (100 * hp) / max + '%'
  hud.hpText.textContent = hp + '/' + max
  hud.dashes.forEach((pip, i) => {
    pip.classList.toggle('ready', i < session.dashes)
  })
  hud.glint.textContent = String(session.glint)
  hud.room.textContent = rooms[session.room]
  hud.fps.textContent = 'FPS ' + shownFps
  hud.banner.hidden = session.bannerT <= 0
  hud.banner.textContent = session.banner
  hud.swap.textContent = session.hand === 'blade' ? 'Swap to focus' : 'Swap to blade'
  hud.dead.hidden = st.dead < 0
}

function frame(now) {
  const previous = frame.last || now
  frame.last = now
  const dt = Math.min(0.05, (now - previous) / 1000)
  const move = readMove()
  const attack = pointer.attack || pressed('KeyJ') || pressed('KeyK') || pressed('Mouse')
  const dash = pointer.dash || pressed('Space') || pressed('ShiftLeft') || pressed('ShiftRight')
  const events = step(session, dt, { x: move.x, y: move.y, attack, dash })
  if (swapEdge) {
    session.hand = session.hand === 'blade' ? 'focus' : 'blade'
    swapEdge = false
  }
  for (const hit of events.hits) floats.push({ ...hit, vy: 0.8 })
  for (const num of floats) {
    num.age += dt
    num.y += num.vy * dt
    num.vy -= dt * 1.4
  }
  while (floats.length && floats[0].age > 0.7) floats.shift()
  if (events.travel && !travelLock) {
    travelLock = true
    hud.fade.classList.add('on')
    window.setTimeout(() => {
      arrive(session)
      showTitle(titles[1])
      hud.fade.classList.remove('on')
      travelLock = false
    }, 420)
  }
  const renderStart = performance.now()
  syncInstances()
  const cam = cameraFor(session)
  if (closeShot) {
    cam.dist = 3.1
    cam.pitch = 0.42
    cam.target[1] = 1.25
  }
  renderer.render(session.world, {
    width: canvas.width,
    height: canvas.height,
    time: session.time,
    instances,
    stepAnimation: true,
    ...cam
  })
  if (bench) canvas.getContext('webgl2')?.finish()
  renderSamples.push(performance.now() - renderStart)
  if (renderSamples.length > 120) renderSamples.shift()
  paintNumbers(cam)
  paintHud()
  fpsFrames += 1
  fpsTime += dt
  samples.push(dt * 1000)
  if (samples.length > 240) samples.shift()
  if (fpsTime >= 0.5) {
    shownFps = Math.round(fpsFrames / fpsTime)
    fpsFrames = 0
    fpsTime = 0
    const sorted = samples.slice().sort((a, b) => a - b)
    const renderSorted = renderSamples.slice().sort((a, b) => a - b)
    window.__splat.fps = shownFps
    window.__splat.frameMs = sorted[Math.floor(sorted.length / 2)] || 0
    window.__splat.renderMs = renderSorted[Math.floor(renderSorted.length / 2)] || 0
    window.__splat.enemies = session.enemies.length
    window.__splat.splats = session.world.count + instances.splats
  }
  requestAnimationFrame(frame)
}

window.addEventListener('keydown', event => {
  if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.code)) event.preventDefault()
  if (event.code === 'KeyG' && !event.repeat) swapEdge = true
  keys.add(event.code)
})
window.addEventListener('keyup', event => keys.delete(event.code))
canvas.addEventListener('pointerdown', event => {
  if (event.pointerType === 'touch') return
  keys.add('Mouse')
})
window.addEventListener('pointerup', () => keys.delete('Mouse'))

function bindHold(button, flag) {
  const down = event => {
    event.preventDefault()
    pointer[flag] = true
  }
  const up = event => {
    event.preventDefault()
    pointer[flag] = false
  }
  button.addEventListener('pointerdown', down)
  button.addEventListener('pointerup', up)
  button.addEventListener('pointercancel', up)
  button.addEventListener('pointerleave', up)
}
bindHold(document.querySelector('#attack'), 'attack')
bindHold(document.querySelector('#dash'), 'dash')
hud.swap.addEventListener('click', () => {
  swapEdge = true
})
hud.stress.addEventListener('click', () => {
  const ladder = [50, 100, 200, 500]
  const current = Number(params.get('enemies'))
  const next = ladder.find(n => n > current) || 50
  const url = new URL(location.href)
  url.searchParams.set('enemies', String(next))
  location.assign(url.toString())
})
document.querySelector('#restart').addEventListener('click', () => location.reload())

const stick = document.querySelector('#stick')
const nub = document.querySelector('#nub')
let stickId = null
function placeStick(event) {
  const rect = stick.getBoundingClientRect()
  let dx = event.clientX - (rect.left + rect.width / 2)
  let dy = event.clientY - (rect.top + rect.height / 2)
  const radius = rect.width * 0.36
  const len = Math.hypot(dx, dy)
  if (len > radius) {
    dx = (dx / len) * radius
    dy = (dy / len) * radius
  }
  nub.style.transform = 'translate(' + dx + 'px,' + dy + 'px)'
  pointer.x = dx / radius
  pointer.y = -dy / radius
  if (Math.hypot(pointer.x, pointer.y) < 0.18) {
    pointer.x = 0
    pointer.y = 0
  }
}
stick.addEventListener('pointerdown', event => {
  stickId = event.pointerId
  stick.setPointerCapture(event.pointerId)
  placeStick(event)
})
stick.addEventListener('pointermove', event => {
  if (event.pointerId !== stickId) return
  placeStick(event)
})
function releaseStick(event) {
  if (event.pointerId !== stickId) return
  stickId = null
  pointer.x = 0
  pointer.y = 0
  nub.style.transform = 'translate(0px, 0px)'
}
stick.addEventListener('pointerup', releaseStick)
stick.addEventListener('pointercancel', releaseStick)

window.__splat = {
  session,
  fps: 0,
  frameMs: 0,
  enemies: session.enemies.length,
  splats: 0,
  swap() {
    swapEdge = true
  }
}

window.addEventListener('resize', resize)
resize()
showTitle(titles[0])
requestAnimationFrame(frame)
