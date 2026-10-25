# ALIVE project handbook

This is the central, maintained project record and local documentation website. It does not run the simulation. The first edition consolidates the local implementation, earlier project documents, selected meeting notes, and recent discussion without changing simulation code or approving proposed scope.

Edition 0.2 adds the individual-agent feasibility section, the measured baseline failure diagnosis, and discussion-capture decisions. Individuals remain a deferred option; validating the current community-level loop remains the user-supported priority.

## Open or share

- Double-click `ALIVE_Handbook.html` for the complete offline website. Share that **single file** with a teammate or advisor; no Python, Node, internet, or server is required to read it.
- Read `../PROJECT_HANDBOOK.md` for the generated plain-text/Markdown edition.
- Use **Download .md** for a copy of the whole handbook or **Print / PDF** to print every section. A browser's normal print command also prints the whole handbook, not only the selected page.
- Optional local server: from the repository root, run `powershell -ExecutionPolicy Bypass -File .\Start_ALIVE_Handbook.ps1`, then visit the URL printed by the launcher. Stop the foreground server with Ctrl+C.

No public website, accounts, collaborative editor, or auto-updating monitor is included. Source paths identify local evidence; they are deliberately not misleading links to unpushed GitHub files. External research links require internet; the rest works offline.

## Maintain one source of truth

1. Edit **`dist/content.js`**. This contains the authoritative handbook content. Do not edit the generated HTML or Markdown directly.
2. Update Current state, Work queue, Journal, and Decisions for meaningful work. Include evidence, verification, and limitations. Keep proposed changes labeled until approved.
3. Run `node docs/handbook/build.mjs` from the repository root. Node.js is needed only to regenerate the shareable copies, not to read the website. The helper validates section IDs, block types, tables, task records, source paths, research URLs, and JavaScript syntax, then regenerates both documents.
4. Open the offline HTML and check the changed pages, global search, priority filters, and print layout.
5. Review with the team; publish repository or website changes only when authorized. The buildless `dist/` folder is ready for later static hosting, but no deployment is performed here.

## Structure

- `dist/content.js`: canonical vision, capabilities, roadmap, tasks, journal, sources, decisions, and upkeep content.
- `dist/index.html`, `styles.css`, `app.js`: responsive website shell and interactions.
- `dist/format.js`: shared Markdown generator used by the browser and build helper.
- `build.mjs`: validation and portable-artifact generation.
- `ALIVE_Handbook.html`: generated single-file offline edition.
- `../PROJECT_HANDBOOK.md`: generated complete Markdown edition.

Search and task-priority filters do not modify project status or persist edits. Keep dated journals append-only; if a decision is superseded, retain the original and link to its replacement. Review dates describe the maintained snapshot, not a live code audit.

## Optional browser checks

For repeatable integration checks, serve this folder (not `dist/` alone):

```powershell
python -m http.server 8766 --bind 127.0.0.1 --directory docs/handbook
# In another terminal, with an installed Chromium browser:
node docs/handbook/check-browser.mjs 'C:\Program Files\Google\Chrome\Application\chrome.exe'
```

`qa.html` exercises browser assertions covering all navigation routes, global search, priority filtering, whole-handbook print-content preparation/restoration, mobile page overflow, discussion/diagnosis content, and agreement between standalone and website Markdown. The runner prints the current check count. It uses a separate project-local browser profile in ignored `tmp/`; no personal browser profile is touched. Native print dialogs and download destinations are not automated by these checks. The QA page is outside the hosting `dist/` directory.
