# Wandering Notes

A lightweight travel blog powered by [Jekyll](https://jekyllrb.com/) and the built-in GitHub Pages-compatible **Minima** theme.

## Publish with GitHub Pages

1. Create a GitHub repository and push this project to its `main` branch.
2. On GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Choose the `main` branch and the `/ (root)` folder, then save.
5. GitHub builds the site after each push. The first publication can take several minutes.

For a project repository, your site is normally published at `https://YOUR-USERNAME.github.io/REPOSITORY-NAME/`. Set `baseurl: "/REPOSITORY-NAME"` in `_config.yml` for that setup. Keep `baseurl: ""` for a user site named `YOUR-USERNAME.github.io` or a custom domain.

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
---

![A quiet lane in Kyoto]({{ '/images/kyoto-lane.jpg' | relative_url }})

English text here.

中文写在这里。
```

## Add photos from your phone

Upload photos into `images/`, then reference them with the `relative_url` form shown above. It works both on a custom domain and when GitHub serves the site under a repository name. Compress or resize photos first (for example, about 1600–2400px on the long edge) so the repository and site stay fast. Everything committed to this public repository, including images and post text, is public.

## Preview locally (optional)

Install Ruby and Bundler, then run:

```sh
bundle install
bundle exec jekyll serve
```

Open `http://localhost:4000` in a browser.
