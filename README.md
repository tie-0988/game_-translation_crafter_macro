# game_-translation_crafter_macro
## Phase 0: Raphael web build on GitHub Pages

Upstream snapshot and license: [raphael/UPSTREAM.md](raphael/UPSTREAM.md),
[raphael/LICENSE](raphael/LICENSE).

`.github/workflows/pages.yml` builds pull requests without deploying. A push to
`main` (or a manual run on `main`) builds and deploys a single Pages artifact:
existing root HTML pages and documentation, plus the app at
`https://tie-0988.github.io/game_-translation_crafter_macro/raphael/`.

Before the first deployment after merging, set **Settings → Pages → Build and
deployment → Source → GitHub Actions**. The current `main` / `root` publishing mode
cannot deploy this compiled artifact. Repository visibility is not changed.

The build uses upstream `nightly-2026-05-10`, Trunk 0.21.14, the Cargo lockfile,
and `bash raphael-gui/build-web.sh --public-url /game_-translation_crafter_macro/raphael/ --locked`.
`scripts/assemble-pages.py` copies the result and applies only hosting bootstrap
changes to the generated HTML. The vendored Rust, UI, and source HTML stay intact.
Root `index.html`, `PLAN.md`, and `FF14_001_英語制作マクロ置換.html` stay intact.

### Cross-origin isolation on Pages

Pages ignores Raphael's `_headers`. We ship the unmodified MIT-licensed
[coi-serviceworker](https://github.com/gzuidhof/coi-serviceworker) v0.1.7 from commit
`7b1d2a092d0d2dd2b7270b6f12f13605de26f214` under `/raphael/` only, alongside its
license. The worker adds COOP `same-origin` and, by the library's default, COEP `credentialless` to responses.
The worker switches to `require-corp` on its degrade path when a worker-controlled document is still not isolated.
On an initial visit, its normal registration/claim process automatically reloads the page; the upstream
pre-flight check and Wasm initialization run as emitted upstream, in the reloaded worker-controlled document.
There is no custom readiness wait and no `window.coi` override. On the first visit the upstream failure
message can flash briefly before the library's reload; if the app starts after that reload, startup is normal.
No worker is registered at the existing root pages' scope.

### Verification after merge (むーちゃん)

- Confirm the main workflow's build and deployment succeed.
- Open `/raphael/` in a normal, fresh browser profile with Service Workers enabled;
confirm the initial automatic reload and that the English upstream app starts.
- In DevTools confirm `crossOriginIsolated === true`, SharedArrayBuffer is
available, and the worker scope ends in `/raphael/`.
- Run a small solve, confirm completion and macro output; check icons/fonts and
network/console errors, then reload and revisit the page.
- Confirm the root hub and existing macro replacement HTML still open.
- Check another browser if available. Unsupported/private browsing modes may
prevent Service Worker registration; failure diagnostics should remain visible.

Live Pages deployment and real-browser startup are intentionally pending merge
and むーちゃん's verification. A successful build alone does not prove startup.
