import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import test from 'node:test'
import { arrive, createSession, step } from '../src/world.js'

const require = createRequire(import.meta.url)
const kit = require('@shapeshift-labs/ink-studio').load()

test('Veris bakes with swappable main-hand parts', () => {
  const session = createSession(kit)
  assert.ok(session.gear.blade.length > 8, 'blade splats')
  assert.ok(session.gear.focus.length > 8, 'focus splats')
  assert.equal(session.enemies.length, 10)
  assert.ok(session.prototypes.wisp.count > 10)
  assert.ok(session.prototypes.wisp.count < 800)
  const before = session.player.st.x
  for (let i = 0; i < 40; i++) step(session, 1 / 60, { x: 1, y: 0, attack: false, dash: false })
  assert.notEqual(session.player.st.x, before)
  session.hand = 'focus'
  step(session, 1 / 60, { x: 0, y: 0, attack: false, dash: false })
  const hidden = session.gear.blade[0]
  const y = session.world.data[(session.at + hidden) * 16 + 1]
  assert.equal(y, -50)
})

test('a slash can fell a wisp and a cleared room can travel', () => {
  const session = createSession(kit)
  session.enemies.forEach(enemy => {
    enemy.hp = 1
    enemy.x = session.player.st.x + 0.8
    enemy.z = session.player.st.z
  })
  let deaths = 0
  for (let i = 0; i < 90 && deaths < session.enemies.length; i++) {
    const events = step(session, 1 / 60, { x: 0, y: 0, attack: true, dash: false })
    deaths += events.deaths.length
  }
  assert.equal(session.enemies.some(enemy => enemy.room === 0 && enemy.alive), false)
  assert.equal(session.gates[0].lit, true)
  session.player.st.x = 0
  session.player.st.z = -6.2
  const travel = step(session, 1 / 60, { x: 0, y: 0, attack: false, dash: false })
  assert.equal(travel.travel, true)
  arrive(session)
  assert.equal(session.room, 1)
})
