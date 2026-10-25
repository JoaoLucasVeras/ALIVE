(() => {
  'use strict';
  const data = globalThis.ALIVE_HANDBOOK;
  const main = document.getElementById('main');
  const search = document.getElementById('search');
  const nav = document.getElementById('navigation');
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const status = text => `<span class="pill ${/Verified|Implemented|Established|User clarification/.test(text) ? 'good' : /Open|Proposed|Deferred|pending|Not /.test(text) ? 'pending' : ''}">${escape(text)}</span>`;
  const graph = () => `<svg viewBox="0 0 620 210" role="img" aria-label="Current technology graph: Fire is prerequisite to Cooking; Basic Tools is prerequisite to Storage."><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#739285"/></marker></defs><g stroke="#739285" stroke-width="2" marker-end="url(#arrow)"><path d="M170 70H405"/><path d="M170 153H405"/></g><g fill="#eaf1e2" stroke="#8ca48a"><rect x="20" y="42" width="150" height="55" rx="12"/><rect x="415" y="42" width="175" height="55" rx="12"/><rect x="20" y="126" width="150" height="55" rx="12"/><rect x="415" y="126" width="175" height="55" rx="12"/></g><g fill="#294c3c" font-family="Segoe UI,Arial,sans-serif" font-size="17" text-anchor="middle"><text x="95" y="76">Fire</text><text x="503" y="76">Cooking</text><text x="95" y="160">Basic Tools</text><text x="503" y="160">Storage</text></g><text x="310" y="25" text-anchor="middle" fill="#66806c" font-family="Segoe UI,Arial,sans-serif" font-size="11" letter-spacing="2">THE CURRENT FOUR-NODE GRAPH</text></svg>`;
  const hero = () => `<div class="hero"><div><span class="pill">ADAPTIVE LIFE IN VIRTUAL ENVIRONMENTS</span><h2>A world of possibilities.<br>A record of what is real.</h2><p>Learn the idea, inspect the foundation, and follow the next steps. This is our shared map—not a claim that the entire vision is already built.</p><a href="#state">Explore the current build →</a><a href="#work">Find the next task →</a></div>${graph()}</div>`;
  function block(b) {
    const title = `<h2>${escape(b.title)}</h2>`;
    switch (b.type) {
      case 'paragraph': return `<section class="block">${title}<p>${escape(b.text)}</p></section>`;
      case 'callout': return `<section class="block callout ${b.tone === 'warning' ? 'warning' : ''}">${title}<p>${escape(b.text)}</p></section>`;
      case 'list': return `<section class="block">${title}<ul>${b.items.map(t => `<li>${escape(t)}</li>`).join('')}</ul></section>`;
      case 'metrics': return `<div class="metrics">${b.items.map(i => `<div class="metric"><span>${escape(i.label)}</span><strong>${escape(i.value)}</strong></div>`).join('')}</div>`;
      case 'table': return `<section class="block">${title}<div class="table-wrap" tabindex="0" role="region" aria-label="${escape(b.title)}"><table><thead><tr>${b.columns.map(c => `<th scope="col">${escape(c)}</th>`).join('')}</tr></thead><tbody>${b.rows.map(row => `<tr>${row.map((c,i) => `<td>${i === 1 && /^(Implemented|Verified|Proposed|Deferred|Open|Not implemented|Not demonstrated|Established direction|User clarification)/.test(c) ? status(c) : escape(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`;
      case 'flow': return `<section class="block">${title}<div class="flow">${b.steps.map((s,i) => `${i ? '<b aria-hidden="true">→</b>' : ''}<span>${escape(s)}</span>`).join('')}</div></section>`;
      case 'technology': return `<section class="block">${title}<div class="technology">${graph()}<p>${escape(b.text)}</p></div></section>`;
      case 'source': return `<section class="block">${title}<div class="sources">${b.items.map(s => `<div class="source"><span>${escape(s.label)}</span><code>${escape(s.path)}</code></div>`).join('')}</div></section>`;
      case 'tasks': return `<section class="block">${title}<div class="task-controls" aria-label="Filter tasks by priority">${['All','P0','P1','P2'].map(p => `<button data-priority="${p}" aria-pressed="${p === 'All'}">${p === 'All' ? 'All tasks' : p}</button>`).join('')}</div><div id="task-list">${b.items.map(t => `<article class="task" data-task-priority="${escape(t.priority)}"><div class="task-header"><span class="pill">${escape(t.id)} · ${escape(t.priority)}</span>${status(t.status)}<span class="owner">${escape(t.owner)}</span></div><h3>${escape(t.title)}</h3><p><strong>Next action:</strong> ${escape(t.next)}</p><p><strong>Done when:</strong> ${escape(t.done)}</p></article>`).join('')}</div></section>`;
      case 'journal': return `<section class="block">${title}<div class="journal">${b.entries.map(e => `<article class="entry"><time>${escape(e.date)}</time>${status(e.status)}<h3>${escape(e.title)}</h3><p>${escape(e.body)}</p><p class="evidence">Evidence: ${escape(e.evidence)}</p><p class="evidence">Next: ${escape(e.next)}</p></article>`).join('')}</div></section>`;
      case 'references': return `<section class="block">${title}${b.items.map(r => `<article class="reference"><h3><a href="${escape(r.url)}" target="_blank" rel="noopener noreferrer">${escape(r.title)} ↗</a></h3><p class="meta">${escape(r.authors)} · ${escape(r.status)}</p><p>${escape(r.note)}</p></article>`).join('')}</section>`;
      default: throw Error(`Unknown content block: ${b.type}`);
    }
  }
  function page(s, print = false) {
    return `<div ${print ? 'class="print-section"' : ''}><p class="eyebrow">${escape(s.kicker)}</p><h1 class="page-title">${escape(s.title)}</h1><p class="intro">${escape(s.intro)}</p>${s.id === 'start' && !print ? hero() : ''}<div class="blocks">${s.blocks.map(block).join('')}</div></div>`;
  }
  nav.innerHTML = data.sections.map((s,i) => `<a href="#${s.id}"><span>${String(i+1).padStart(2,'0')}</span>${escape(s.title)}</a>`).join('');
  document.getElementById('revision').textContent = `Handbook v${data.revision} · Reviewed ${data.updated}`;
  function render(resetScroll = true) {
    const query = search.value.trim().toLocaleLowerCase();
    const selected = data.sections.find(s => s.id === location.hash.slice(1)) || data.sections[0];
    for (const link of nav.querySelectorAll('a')) {
      if (!query && link.hash === `#${selected.id}`) link.setAttribute('aria-current','page');
      else link.removeAttribute('aria-current');
    }
    if (query) {
      const matches = data.sections.filter(s => JSON.stringify(s).toLocaleLowerCase().includes(query));
      main.innerHTML = `<p class="eyebrow">SEARCH THE WHOLE HANDBOOK</p><h1 class="page-title">Find your bearings.</h1><p class="intro" role="status">${matches.length} section${matches.length === 1 ? '' : 's'} matching “${escape(search.value.trim())}”.</p>${matches.map(s => `<a class="search-result" href="#${s.id}"><h2>${escape(s.title)}</h2><p>${escape(s.intro)}</p><small>Open section →</small></a>`).join('') || '<p class="empty">No matching sections. Try technology, sharing, reward, roadmap, or T01.</p>'}`;
    } else {
      const index = data.sections.indexOf(selected);
      main.innerHTML = page(selected) + `<div class="page-next">${index ? `<a href="#${data.sections[index-1].id}">← ${escape(data.sections[index-1].title)}</a>` : '<span>Begin with the idea. End with a next action.</span>'}${index < data.sections.length-1 ? `<a href="#${data.sections[index+1].id}">${escape(data.sections[index+1].title)} →</a>` : '<a href="#start">Back to start ↑</a>'}</div>`;
    }
    document.title = `ALIVE · ${query ? 'Search' : selected.title}`;
    if (resetScroll) window.scrollTo({top:0,behavior:'instant'});
  }
  document.addEventListener('click', e => {
    const link = e.target.closest('a[href^="#"]');
    if (link && link.getAttribute('href') !== '#main') {
      search.value = '';
      if (location.hash === link.hash) render();
    }
    const filter = e.target.closest('[data-priority]');
    if (filter) {
      for (const button of document.querySelectorAll('[data-priority]')) button.setAttribute('aria-pressed',String(button === filter));
      for (const task of document.querySelectorAll('[data-task-priority]')) task.hidden = filter.dataset.priority !== 'All' && task.dataset.taskPriority !== filter.dataset.priority;
    }
  });
  search.addEventListener('input', () => render(false));
  window.addEventListener('hashchange', () => { if (location.hash !== '#main') render(); });
  document.addEventListener('keydown', e => {
    if (e.key === '/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) { e.preventDefault(); search.focus(); }
    if (e.key === 'Escape' && document.activeElement === search) { search.value = ''; render(); search.blur(); }
  });
  document.getElementById('download').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([globalThis.ALIVE_MARKDOWN()],{type:'text/markdown;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url; link.download = 'ALIVE_Project_Handbook.md'; link.click();
    setTimeout(() => URL.revokeObjectURL(url),1000);
  });
  let printMarkup = null;
  function preparePrint() {
    if (printMarkup !== null) return;
    printMarkup = main.innerHTML;
    main.innerHTML = `<div class="print-cover"><p class="eyebrow">PROJECT HANDBOOK</p><h1>ALIVE</h1><p>${escape(data.expansion)}</p><p>Version ${data.revision} · Reviewed ${data.updated}</p><p>Complete handbook: vision, current state, architecture, roadmap, journal, research, and decisions.</p></div>` + data.sections.map(s => page(s,true)).join('');
  }
  window.addEventListener('beforeprint', preparePrint);
  window.addEventListener('afterprint', () => { if (printMarkup !== null) { main.innerHTML = printMarkup; printMarkup = null; } });
  document.getElementById('print').addEventListener('click', () => { preparePrint(); window.print(); });
  render(false);
})();
