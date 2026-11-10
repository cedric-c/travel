# Cédric Elsewhere

A lightweight travel blog powered by [Jekyll](https://jekyllrb.com/) and the built-in GitHub Pages-compatible **Minima** theme.

## Publish with GitHub Pages

1. Create a GitHub repository and push this project to its `main` branch.
2. On GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Choose the `main` branch and the `/ (root)` folder, then save.
5. GitHub builds the site after each push. The first publication can take several minutes.

This repository is configured for `https://cedric-c.github.io/travel/`. If the repository name or domain changes, update `url` and `baseurl` in `_config.yml`.

## Add a post

Create a Markdown file under `_posts/` with a filename in this form:

```text
YYYY-MM-DD-a-short-title.md
```

Start it with front matter, then write normally in Markdown:

```markdown
---
layout: post
title: "A day in Kyoto / 京都的一天"
description: "A quiet Kyoto lane, a good meal, and another chance to put my Mandarin to the test."
locations: [Kyoto, Japan]
---

![A quiet lane in Kyoto]({{ '/images/kyoto-lane.jpg' | relative_url }})

English text here.

中文写在这里。
```

Set `description` to a short, plain-text summary of the story. It supplies the homepage preview and the article's description metadata through `jekyll-seo-tag`. Descriptions are shown in full on the homepage; keep them concise (roughly 100–160 characters). If a future post omits it, the homepage falls back to an excerpt shortened at a word boundary.

The home page filters entries by year (from the filename date) and location. Set `locations` to a list of place names, such as `[Kyoto, Japan]`, using the same names across related posts. Every listed place appears in the filter, and all places appear below the date on the home page. Posts without `locations` appear under **Unspecified**. Filters work together and are applied in the browser; posts remain visible if JavaScript is unavailable.

## Homepage selections

The compact **Start here** section is curated through `selected_stories` in `index.html` front matter. List post IDs in display order, for example `/2026/10/17/hello-chengdu` (no trailing slash). Each selection uses the post's title, image, and description. The chronological **Latest entries** feed and its filters remain separate.

## Reading between entries

Every post includes links to the previous and next entries in publication order, plus up to two stories under **Keep reading**. Recommendations prefer the same primary location (the first item in `locations`), then overlapping locations. Newer entries break ties and fill any remaining slots. The current entry and duplicate recommendations are excluded. This is rendered by Jekyll and works without JavaScript.

## Add photos from your phone

Upload photos into `images/`, then reference them with the `relative_url` form shown above. It works both on a custom domain and when GitHub serves the site under a repository name. Compress or resize photos first (for example, about 1600–2400px on the long edge) so the repository and site stay fast. Everything committed to this public repository, including images and post text, is public.

## Preview locally (optional)

Install Ruby and Bundler, then run:

```sh
bundle install
bundle exec jekyll serve
```

Open `http://localhost:4000/travel/` in a browser.

## Choose a photo's width

Use the photo include as its own block, with a blank line before and after it:

```liquid
{% include photo.html
   src="/images/pastures1-2026-10-13.jpeg"
   alt="Open pastures at Fairy Mountain"
   caption="Fairy Mountain."
   size="full"
%}
```

| `size` | Desktop presentation |
| --- | --- |
| `normal` (default) | Fits the 680px prose column |
| `wide` | Extends beyond the prose, up to 1100px with outer margins |
| `full` | Spans the page edge to edge |

Choose the size separately for each shot. On screens up to 600px, all three
use the text column's margins. Photos keep their original aspect ratio with no
cropping; captions stay near the prose width and inherit the light/dark palette.
Omit `caption` when it is not needed. Captions are plain text. Supply meaningful
`alt` text, or `alt=""` for a purely decorative image.

Pass the source path without `relative_url`; the include applies it and reuses
the responsive image manifest, WebP variants, and lazy loading. Ordinary Markdown
images keep their existing layout. Unrecognized sizes fall back to `normal`.
Browsers without CSS container units also fall back to the normal width.
