import { createRequire } from 'node:module'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const require = createRequire(import.meta.url)
const studio = require('@shapeshift-labs/ink-studio')
const here = path.dirname(fileURLToPath(import.meta.url))
const out = path.join(here, '..', 'public', 'ink-studio.mjs')
const body = studio.bundle({ format: 'module' })
const pinned = '9d73158d6b8e92b2a4571e4a7ce98924d0759556'
const note = `// Generated from @shapeshift-labs/ink-studio ${pinned}. Do not edit.\n`
fs.mkdirSync(path.dirname(out), { recursive: true })
fs.writeFileSync(out, note + body)
console.log('ink bundle', out, body.length)
