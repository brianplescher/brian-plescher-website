# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static HTML author portfolio for brianplescher.com, deployed directly to Netlify with no build step. The site showcases three books (*The Directed Author*, *Woundwise*, *Slickens*) and published essays.

## Local Development

There is no build system, package manager, or bundler. To preview locally, serve the root directory with any static file server:

```bash
npx serve .
# or
python3 -m http.server 8080
```

Netlify Forms (`data-netlify="true"`) only work on the deployed site — form submissions will 404 locally. The Netlify CLI can simulate this:

```bash
netlify dev
```

## Architecture

**No templating.** Every page is a standalone `.html` file. The nav and footer HTML are copy-pasted across all pages. When adding or changing nav items, update every page individually.

**About dropdown.** In every main nav, About is a `.nav-dropdown` with a `.nav-submenu` holding Media Kit (`/media-kit/`). It opens on hover/focus on desktop (CSS only) and is always expanded inside the mobile menu. `read.html` has its own inline copy of these styles.

**Single stylesheet.** All styles live in `style.css`, organized with section comments. The design system is defined entirely via CSS custom properties in `:root` — use these variables rather than hardcoding values:
- Colors: `--bg`, `--surface`, `--cyan`, `--headline`, `--body`, `--muted`, `--border`
- Typography: IM Fell English (headings), Libre Baskerville (body), Montserrat (UI/labels/buttons)

**Shared script.** `js/nav.js` handles the hamburger menu (any `.nav-hamburger` button toggles the element named by its `aria-controls`) and the `.fade-in` IntersectionObserver. Include `<script src="/js/nav.js" defer></script>` on every page that has either; without it `.fade-in` content stays invisible.

**Netlify Forms.** Contact, newsletter, and Slickens notify forms use `data-netlify="true"` with a hidden `form-name` input. Submissions redirect to `thankyou.html`. No backend code needed.

**Analytics.** Every page loads Plausible (`plausible.io/js/pa-…js` plus an inline `plausible.init()`) just before `</head>`; copy it into new pages. The CSP in `netlify.toml` allows `https://plausible.io` in `script-src` and `connect-src`.

**No server code.** There are no Netlify Functions. Don't add pages that call paid APIs from the browser.

**Canonical URLs.** The canonical host is `https://brianplescher.com` (www 301s to it). Clean URLs are served from directories: `/about/`, `/books/woundwise/`, `/books/the-directed-author/` (each an `index.html`). Netlify 301s the no-slash form to the trailing-slash form, so always link, canonicalize and redirect to the trailing-slash URL. Use absolute paths (`/style.css`, `/books/woundwise/`) in links.

**Structured data.** Each indexable page has one JSON-LD `@graph` block in `<head>` containing the full `Person` (`https://brianplescher.com/#person`), the `WebSite` (`#website`), the page node (`<url>#webpage`) and any `Book`/`BlogPosting` nodes on that page. Books use `<book url>#book` ids and reference the author by `{"@id": ".../#person"}`. Keep the Person node identical on every page.

**Footer contact.** Every footer ends with `<p class="footer-contact">Contact Brian: <a href="mailto:brian@sonexial.com">…</a></p>`.

**Canonical check.** `python3 scripts/check_canonicals.py` (add `--live` after deploy) verifies every `sitemap.xml` URL has a matching canonical and `og:url`, valid JSON-LD, and that no indexable page is missing from the sitemap. `/scripts/*` is blocked with a 404 rule.

## Deployments & Redirects

Deployment is automatic via Netlify on push. The publish directory is `.` (repo root).

All redirects live in `netlify.toml` (there is no `_redirects`). Every rule uses `force = true`; without it Netlify ignores a redirect whenever a file exists at the old path. Dev files (`CLAUDE.md`, `README.md`, `.kiro/`, …) are blocked with forced 404 rules because the repo root is published.

When adding new pages, also update:
- `sitemap.xml` (add `<url>` entry with `<lastmod>`)
- `netlify.toml` (add redirects for any old paths)
- Nav and footer on all existing pages

## SEO Conventions

Each indexable page includes: canonical URL (apex domain), meta description, Open Graph tags, Twitter Card tags, and a `<script type="application/ld+json">` block with appropriate Schema.org type (`Person`, `Book`, `BlogPosting`, etc.). Follow the existing pattern when adding pages or essays.

Utility pages (`thankyou.html`, `order-confirmed.html`, `404.html`) use `<meta name="robots" content="noindex">` and stay out of `sitemap.xml`.
