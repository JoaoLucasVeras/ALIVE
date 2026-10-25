/* Shared browser/build formatter: generated documents never become a second source. */
globalThis.ALIVE_MARKDOWN = function markdown(data = globalThis.ALIVE_HANDBOOK) {
  const lines = [`# ${data.name}: Project handbook`, `\n${data.expansion}\n\nVersion ${data.revision} · Reviewed ${data.updated}\n`, '> Maintained snapshot. Implemented features, proposals, and open questions are distinct.\n'];
  for (const s of data.sections) {
    lines.push(`\n## ${s.title}\n`, s.intro + '\n');
    for (const b of s.blocks) {
      if (b.title) lines.push(`\n### ${b.title}\n`);
      if (b.text) lines.push(b.text + '\n');
      if (b.type === 'list') lines.push(b.items.map(i => '- ' + i).join('\n') + '\n');
      if (b.type === 'metrics') lines.push(b.items.map(i => `- ${i.label}: ${i.value}`).join('\n') + '\n');
      if (b.type === 'table') { const cell = x => String(x).replace(/\|/g,'\\|').replace(/\n/g,' '); lines.push('| ' + b.columns.map(cell).join(' | ') + ' |', '| ' + b.columns.map(()=>'---').join(' | ') + ' |', ...b.rows.map(r => '| ' + r.map(cell).join(' | ') + ' |'), ''); }
      if (b.type === 'flow') lines.push(b.steps.join(' → ') + '\n');
      if (b.type === 'technology') lines.push('```text\nFire ────────> Cooking\nBasic Tools ─> Storage\n```\n');
      if (b.type === 'source') lines.push(b.items.map(i => `- ${i.label}: ${i.path}`).join('\n') + '\n');
      if (b.type === 'tasks') for (const t of b.items) lines.push(`\n#### ${t.id} · ${t.title}\n`, `${t.priority} · ${t.status} · Owner: ${t.owner}\n`, `Next action: ${t.next}\n`, `Done when: ${t.done}\n`);
      if (b.type === 'journal') for (const e of b.entries) lines.push(`\n#### ${e.date} · ${e.title}\n`, `Status: ${e.status}\n\n${e.body}\n`, `Evidence: ${e.evidence}\n\nNext: ${e.next}\n`);
      if (b.type === 'references') for (const r of b.items) lines.push(`\n#### [${r.title}](${r.url})\n`, `${r.authors}\n\n${r.status}\n\n${r.note}\n`);
    }
  }
  return lines.join('\n');
};
