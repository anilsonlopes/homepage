# Repository Guidelines

## Project Structure & Module Organization

This is a Vue 3 single-page site built with Vite and Tailwind CSS. Application code lives in `src/`: `main.js` mounts the app, `App.vue` defines the page, and reusable Vue components belong in `src/components/`. Global styles are in `src/style.css`; static files that must be served unchanged belong in `public/`. The root `index.html` contains the application shell and page metadata. Browser verification utilities and their reference screenshots live in `verification/`. Keep design rationale in `DESIGN.md` rather than embedding lengthy explanations in components.

## Build, Test, and Development Commands

Use Bun, matching the checked-in `bun.lock` and README examples. Node.js must be `^24.0.0` and Bun must be `>=1.3.0`.

- `bun install` installs dependencies.
- `bun dev` starts Vite with hot module replacement.
- `bun run build` creates the production bundle in `dist/`.
- `bun run preview` serves that bundle locally, normally at `http://localhost:4173/`.
- `python verification/verify_highlight.py` checks highlight hover/focus behavior against a running preview server. It requires Python Playwright and an installed Chromium browser.

Always run the production build before submitting changes.

## Coding Style & Naming Conventions

Follow the existing Vue Single-File Component pattern and use `<script setup>`. Indent JavaScript, Vue templates, and configuration with two spaces. Name components in PascalCase (`WordHighlight.vue`) and import them with the same casing. Use camelCase for JavaScript identifiers and kebab-case for custom elements in templates when appropriate. Prefer Tailwind utility classes for styling; reserve `src/style.css` for global rules. Use the `@` alias for imports rooted at `src/` when it improves readability. No formatter or linter is configured, so keep edits consistent with nearby code.

## Testing Guidelines

There is no automated unit-test suite or coverage threshold. For UI changes, run the build, start `bun run preview`, then execute the verification script. Inspect the generated images in `verification/`, especially keyboard focus and hover states. Add focused verification coverage when introducing new interactive behavior.

## Commit & Pull Request Guidelines

Recent history favors concise, imperative messages, often Conventional Commit style such as `feat(ux): improve WordHighlight accessibility`. Keep each commit scoped to one concern. Pull requests should explain the user-visible change, list validation performed, link relevant issues, and include before/after screenshots for visual updates. Call out accessibility, responsive-layout, or metadata changes explicitly.
