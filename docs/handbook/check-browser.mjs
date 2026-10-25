// Optional integration QA using an installed Chromium browser, not a new dependency.
// Start the local server with docs/handbook as its directory before running this.
import { execFileSync } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const browser = process.argv[2];
const origin = process.argv[3] || 'http://127.0.0.1:8766';
if (!browser) throw Error('Usage: node docs/handbook/check-browser.mjs <Chromium executable> [local preview origin]');
const url = new URL(origin);
if (!['127.0.0.1','localhost'].includes(url.hostname)) throw Error('QA must use the local preview origin.');
const html = execFileSync(browser, ['--headless=new','--no-first-run','--disable-extensions','--disable-background-networking',
  `--user-data-dir=${resolve(root,'tmp/handbook-tests')}`, '--dump-dom','--virtual-time-budget=10000',new URL('qa.html', url).href],
  {encoding:'utf8',timeout:30000,stdio:['ignore','pipe','ignore']});
const result = html.match(/<pre id="results">([\s\S]*?)<\/pre>/);
console.log(result ? result[1] : 'No browser test result returned.');
if (!result || !result[1].startsWith('PASS:')) process.exitCode = 1;
