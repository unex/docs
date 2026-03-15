# Zensical Docs

This repository is configured for **Zensical** with automatic deployment to GitHub Pages via GitHub Actions.

## Run locally

```bash
python -m pip install -r requirements.txt
zensical serve
```

Open `http://127.0.0.1:8000`.

## Deployment

- Push to `main`
- GitHub Actions runs `.github/workflows/deploy.yml`
- The site is built with `zensical build --clean` and deployed via GitHub Pages Actions

## First-time GitHub setup

In your GitHub repository settings:

1. Go to **Settings → Pages**
2. Under **Build and deployment**, choose **GitHub Actions**
