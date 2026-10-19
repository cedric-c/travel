# Spike: responsive image generation and historical backfill

## Context

The site is a Jekyll 4.3 / Minima 2.5 GitHub Pages site deployed from `main` (repository root). The documented publishing flow uploads photographs directly to `images/` from a phone. Existing post Markdown uses image URLs such as `{{ '/images/photo.jpg' | relative_url }}`. The homepage uses each post's `image` front-matter URL as its thumbnail, with CSS sizing only; the browser downloads the original bytes. The homepage currently lazy-loads *all* thumbnails, including the featured/latest image.

**Goal:** optimize historical and future images without breaking existing links, changing mobile authoring, or replacing originals.

## Recommended approach

A Python/Pillow batch processor run in GitHub Actions. Retain originals under `images/`, and write generated derivatives to `images/optimized/` (git-tracked). Make a first, manually triggered backfill; after validation, enable automatic processing on image uploads.

Derivatives per source:
- 320px wide WebP (small cards; do not confuse with square cropping)
- 800px wide WebP (mobile)
- 1600px wide WebP (article / desktop)
- Optionally 2000px wide for wide/high-density hero images after measurements

Width means maximum width; preserve aspect ratio and EXIF orientation. Never upscale. Quality ~80, method=6 as a starting point; measure real output before finalizing. Keep PNG with transparency as needed; handle animated GIF separately, do not silently flatten animation. Avoid SVG conversion. Support JPG/JPEG/PNG/HEIC only when decoder support is installed; Pillow alone does not guarantee HEIC support.

## Naming and manifest

For `images/foo.jpg`, generate `images/optimized/foo-320.webp`, `foo-800.webp`, and `foo-1600.webp` (only if source width supports each). Beware filename collisions such as `foo.jpg` vs `foo.png`: encode extension in basename or use a stable source hash. Write a deterministic JSON manifest mapping original public paths to available derivative URLs and intrinsic dimensions; this avoids guessing whether 1600px variants exist. Include a source digest and processor settings/version so reprocessing detects changed inputs and changed quality settings. A simple output-exists check is not sufficient for idempotence.

## Rendering

- Homepage: use a Jekyll include that looks up the manifest by the existing `post.image` URL, emits `srcset` and `sizes`, and falls back to the original URL if no manifest entry exists.
- Featured image: `loading="eager" fetchpriority="high"`; others `loading="lazy" decoding="async"`.
- Preserve the original link and the post's `image` front matter; use a derived responsive image only in the HTML rendering.
- Article Markdown images need a separate integration: Kramdown/Jekyll render hooks are not a built-in feature in this configuration. Consider a tested Jekyll plugin for image rewriting **only if compatible with the chosen Pages build path**, or explicitly migrate Markdown image markup to a reusable Liquid include. Avoid blanket regex replacement of Markdown.
- For a 112px square thumbnail, choose a 320px derivative and use CSS `object-fit: cover`; do not crop originals.
- For featured images use responsive `sizes` matching the real layout, not a fixed 112px HTML width/height. Emit actual intrinsic aspect ratios to prevent layout shift.

## GitHub Actions design

1. Start with `workflow_dispatch` and inputs `force` (default false), `dry_run` (default true).
2. Checkout with write permission limited to repository contents for the commit job; install pinned Python dependencies and any HEIC support intentionally.
3. Scan `images/` recursively, exclude `images/optimized/`, ignore unsupported formats, enforce per-file safety limits, produce a concise report (count, total bytes before/after, skipped/failed).
4. Generate deterministic variants and manifest. Skip unchanged source/config pairs; `force` overrides.
5. For a non-dry run, commit only generated derivatives/manifest to a dedicated branch or open a PR for review; **do not directly push to main initially**.
6. After initial review and verification, optionally trigger on pushes touching `images/**` while excluding generated outputs. Ensure generated commits cannot cause infinite loops.
7. Avoid untrusted PR workflows with write tokens; use minimal permissions.

**GitHub Pages constraint:** The README specifies branch deployment, not a custom build workflow. Verify whether the Pages build accepts the manifest lookup and any custom Liquid includes; do not assume arbitrary Jekyll plugins can execute in the GitHub Pages build. A pure-Liquid include + committed JSON manifest is the lowest-risk path.

## Backfill strategy

- Inventory originals, extensions, byte sizes, dimensions, and references before making changes.
- Run a dry run and inspect report, then generate a small sample (landscape, portrait, PNG, HEIC if present).
- Verify actual browser `currentSrc`, transfer sizes, LCP, and layout shifts on iPhone/mobile throttling.
- Run full backfill on a branch and review generated files and repository growth before merging.
- Originals remain addressable; a missing variant falls back to original.
- Do not bulk-commit generated assets without checking GitHub repository size and GitHub Pages published-site size limits.

## Acceptance criteria

- Existing image URLs remain valid and unchanged.
- Running twice with identical inputs/config yields zero changes on the second run.
- Changed source or compression configuration regenerates expected variants.
- No upscaling; portrait/landscape orientation preserved.
- Featured image is eager; offscreen thumbnails are lazy.
- Homepage downloads a ~320px variant for thumbnails on typical mobile DPR, and an appropriately sized featured image.
- All images render if a manifest entry is absent.
- Document measured before/after bytes and at least one mobile performance trace.
- Image generation failures are reported and do not silently publish broken references.

## Open questions / risks

1. Inventory actual file sizes, source dimensions, and formats (especially HEIC), which are not yet measured.
2. Determine whether photo names collide across extensions and directories.
3. Decide whether generated derivatives should be committed (simple Pages compatibility, repo growth) or uploaded as a build artifact in a custom Pages deployment (more complexity, cleaner git history).
4. Article-body Markdown rewriting is distinct from the straightforward homepage fix.
5. GitHub Pages build behavior and action permissions need validation on a test branch.

## Proposed rollout

**Phase 1:** inventory + manual dry-run/backfill script and manifest.  
**Phase 2:** homepage responsive image include, fix hero loading, validate mobile.  
**Phase 3:** article-body integration and automatic on-upload processing.  

No production image rewrites should occur as part of this spike.
