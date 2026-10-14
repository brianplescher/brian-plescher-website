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

**Single stylesheet.** All styles live in `style.css`, organized with section comments. The design system is defined entirely via CSS custom properties in `:root` — use these variables rather than hardcoding values:
- Colors: `--bg`, `--surface`, `--cyan`, `--headline`, `--body`, `--muted`, `--border`
- Typography: IM Fell English (headings), Libre Baskerville (body), Montserrat (UI/labels/buttons)

**Shared script.** `js/nav.js` handles the hamburger menu (any `.nav-hamburger` button toggles the element named by its `aria-controls`) and the `.fade-in` IntersectionObserver. Include `<script src="/js/nav.js" defer></script>` on every page that has either; without it `.fade-in` content stays invisible.

**Netlify Forms.** Contact, newsletter, and Slickens notify forms use `data-netlify="true"` with a hidden `form-name` input. Submissions redirect to `thankyou.html`. No backend code needed.

**No server code.** There are no Netlify Functions. Don't add pages that call paid APIs from the browser.

**Canonical URLs.** The canonical host is `https://brianplescher.com` (www 301s to it). Clean URLs are served from directories: `/about/`, `/now/`, `/books/woundwise/`, `/books/the-directed-author/` (each an `index.html`). Netlify 301s the no-slash form to the trailing-slash form, so always link, canonicalize and redirect to the trailing-slash URL. Use absolute paths (`/style.css`, `/books/woundwise/`) in links.

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
