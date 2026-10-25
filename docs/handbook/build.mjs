// Buildless site; this helper validates content and creates portable artifacts.
import { readFile, writeFile, access } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const directory = dirname(fileURLToPath(import.meta.url));
const root = resolve(directory, '../..');
const source = await readFile(resolve(directory, 'dist/content.js'), 'utf8');
const formatter = await readFile(resolve(directory, 'dist/format.js'), 'utf8');
const app = await readFile(resolve(directory, 'dist/app.js'), 'utf8');
const styles = await readFile(resolve(directory, 'dist/styles.css'), 'utf8');
const index = await readFile(resolve(directory, 'dist/index.html'), 'utf8');
const context = vm.createContext({});
vm.runInContext(source, context);
vm.runInContext(formatter, context);
new vm.Script(app); // Syntax check without inventing a browser DOM.
const data = context.ALIVE_HANDBOOK;
assert.equal(data.sections.length, 13);
assert(data.sections.some(s => s.id === 'individuals'), 'Future individual-agent section is missing');
assert(data.sections.some(s => s.id === 'interface'), 'Interface vision section is missing');
assert(data.sections.some(s => s.id === 'uirebuild'), 'UI rebuild plan section is missing');
assert.match(data.updated, /^\d{4}-\d{2}-\d{2}$/);
const ids = new Set();
const supported = new Set(['paragraph','callout','list','metrics','table','flow','technology','source','tasks','journal','references']);
for (const section of data.sections) {
  assert.match(section.id, /^[a-z]+$/);
  assert(!ids.has(section.id), `Duplicate section ${section.id}`);
  ids.add(section.id);
  assert(section.title && section.intro && section.kicker);
  assert(section.blocks.length);
  for (const block of section.blocks) {
    assert(supported.has(block.type), `Unknown block ${block.type}`);
    if (block.type === 'table') for (const row of block.rows) assert.equal(row.length, block.columns.length);
    if (block.type === 'source') for (const item of block.items) {
      const path = resolve(root, item.path);
      assert(path.startsWith(root + '/') || path.startsWith(root + '\\'), `Source escapes project: ${item.path}`);
      await access(path);
    }
    if (block.type === 'tasks') {
      assert.equal(new Set(block.items.map(i=>i.id)).size, block.items.length);
      for (const item of block.items) assert(item.next && item.done && item.owner && item.status && item.priority);
    }
    if (block.type === 'references') for (const item of block.items) assert.equal(new URL(item.url).protocol, 'https:');
  }
}
const markdown = context.ALIVE_MARKDOWN();
for (const section of data.sections) assert(markdown.includes(`## ${section.title}`));
assert(markdown.includes('D10') && markdown.includes('D11') && markdown.includes('D12') && markdown.includes('D13') && markdown.includes('D14') && markdown.includes('D15'), 'Future option, discussion capture, interface, renderer and technology-value decisions must be documented');
const evidence = JSON.parse(await readFile(resolve(directory, 'evidence/2026-10-10-baseline-diagnosis.json'), 'utf8'));
assert.equal(evidence.results.length, 4);
assert.equal(evidence.configuration.total_runs, 80);
for (const result of evidence.results) assert.equal(result.collapsed + result.reached_limit, 20);
assert.equal(Object.values(evidence.stable_rules_seed_42.actions).reduce((a,b)=>a+b,0), 256);
const inline = text => text.replace(/<\/script/gi, '<\\/script');
const portable = index.replace('<link rel="stylesheet" href="styles.css">', () => `<style>${styles}</style>`)
  .replace('<script src="content.js" defer></script>', () => `<script defer>${inline(source)}</script>`)
  .replace('<script src="format.js" defer></script>', () => `<script defer>${inline(formatter)}</script>`)
  // Inline defer scripts do not defer execution; the app must run after parsing.
  .replace('<script src="app.js" defer></script>', '')
  .replace('</body>', () => `<script>${inline(app)}</script>\n</body>`);
assert(!/\b(?:src|href)="(?:styles\.css|content\.js|format\.js|app\.js)"/.test(portable));
await writeFile(resolve(root, 'docs/PROJECT_HANDBOOK.md'), markdown, 'utf8');
await writeFile(resolve(directory, 'ALIVE_Handbook.html'), portable, 'utf8');
console.log(`Validated ${data.sections.length} sections, source paths, tables, tasks, links and script syntax.`);
console.log('Generated docs/PROJECT_HANDBOOK.md and docs/handbook/ALIVE_Handbook.html.');
