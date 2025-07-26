# Post Fiat Media Kit

This directory contains the official Post Fiat logo generation scripts and source files. **All downloadable assets are now located in `static/media-kit/` for public use.**

## Organization

- **Scripts & Source SVG:**
  - Remain in this directory (`content/media-kit/`)
  - Not published to the website
- **Public Assets (PNG, SVG, ICO):**
  - Located in `static/media-kit/`
  - Downloadable at `/media-kit/` on the website
- **Favicon:**
  - `favicon.ico` is symlinked at `static/favicon.ico` for browser auto-detection

## Usage

- To regenerate all assets, use the comprehensive script:

```bash
./generate_all.sh [OPTIONS]
```

See script help for options.

## Adding New Sizes

To add new dimensions, edit the `dimensions` array in `generate_all.sh`.

## Brand Guidelines

- Always maintain the logo's aspect ratio
- Don't modify the logo colors or proportions
- Ensure adequate clear space around the logo (minimum 1x logo height)
- Use the SVG version for web applications when possible

## See Also

- The public media kit page at `/media-kit/` for download links and brand usage guidelines. 