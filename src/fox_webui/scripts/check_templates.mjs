/**
 * 前端模板编译检查（免浏览器）
 * ─────────────────────────────────────────────────────────────
 * 为什么需要：本项目前端是"免构建 Vue3"（模板写在 template 字符串里），
 * 组件文件能通过 `node --check`（JS 语法没问题）但**模板可能有编译错误**，
 * 那样整个 app 会在 mount 时抛错、页面永远停在"正在加载前端…"，
 * 而浏览器里看日志很不方便（尤其远程/无头环境）。
 *
 * 用法：
 *     node src/fox_webui/scripts/check_templates.mjs
 *
 * 原理：用本地那份 vue.esm-browser.prod.js 的 compile()，给 min 的 DOM shim
 * （Vue 的浏览器编译器解码 HTML 实体时会用 document.createElement）。
 */
import fs from 'fs'
import os from 'os'
import path from 'path'
import { fileURLToPath, pathToFileURL } from 'url'

const here = path.dirname(fileURLToPath(import.meta.url))
const webJs = path.resolve(here, '..', 'web', 'js')

// ⚠️ Node 会把 .js 当 CommonJS → 具名导出 import 会失败，
//    所以先拷成 .mjs 再动态 import（浏览器里没这个问题，importmap 直接吃 .js）
const vueSrc = path.resolve(here, '..', 'web', 'lib', 'vue.esm-browser.prod.js')
const vueTmp = path.join(os.tmpdir(), 'vue_for_template_check.mjs')
fs.copyFileSync(vueSrc, vueTmp)
const { compile } = await import(pathToFileURL(vueTmp).href)

// 最小 DOM shim（只为让编译器的实体解码可用）
globalThis.document = {
  createElement() {
    return {
      _html: '',
      set innerHTML(v) { this._html = v },
      get innerHTML() { return this._html },
      get textContent() { return this._html.replace(/<[^>]*>/g, '') },
      get children() {
        const m = /foo="([^"]*)"/.exec(this._html)
        return [{
          getAttribute: () => (m ? m[1].replace(/&quot;/g, '"') : ''),
        }]
      },
    }
  },
}

const files = fs.readdirSync(path.join(webJs, 'components')).map((f) => `components/${f}`)
files.push('main.js')

let bad = 0
let checked = 0
for (const f of files) {
  const src = fs.readFileSync(path.join(webJs, f), 'utf8')
  const m = src.match(/template:\s*`([\s\S]*)`\s*\}\s*$/m)
  if (!m) { console.log(`SKIP  ${f}（没有 template 字符串）`); continue }
  checked++
  try {
    compile(m[1], { onError(e) { throw e }, onWarn(w) { console.log(`WARN  ${f}: ${w.message}`) } })
    console.log(`OK    ${f}`)
  } catch (e) {
    bad++
    console.log(`FAIL  ${f} -> ${String(e.message).split('\n')[0].slice(0, 300)}`)
  }
}
console.log(bad ? `❌ ${bad}/${checked} 个模板编译失败` : `✅ ${checked} 个模板全部编译通过`)
process.exit(bad ? 1 : 0)
