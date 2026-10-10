# Artwork originals: recovery and publication

The museum is at `rooms/inside/visual-art/index.html`. The currently published files in `assets/visual-art/2025/` are **previews**, not preservation masters. Many are only 2–14 KB. Do not upscale those files and call the result an original.

## Where the originals are

- `knowledge/creative/chatgpt-library-originals-inventory-2026-10-10.json` inventories 81 larger PNGs found in the user's ChatGPT Library (names and byte sizes only).
- `knowledge/creative/art-gallery-pending-acquisitions-2026-10.json` contains descriptions, dates, and pending titles.
- **The image bytes in the private ChatGPT Library are not accessible to GitHub Actions by default.** Neither inventory is a backup of the image pixels.

## Recovery procedure

1. Export the image PNGs from ChatGPT Library to one folder on a local computer.
2. Clone this repository and install Pillow with `python -m pip install Pillow`.
3. Run `python scripts/import_gallery_originals.py /path/to/exported/pngs --dry-run` and inspect matches. Unmatched images are not silently mislabelled.
4. Run the same command with `--apply`, inspect `git status`, and review changes to `rooms/inside/visual-art/index.html`.
5. Add missing works with proper dated cards and text; never create a card whose image has not actually arrived.
6. Commit and push the new files under `assets/visual-art/originals/`, preserving the source PNG bytes. If a file is larger than GitHub's normal limits, use an appropriate externally hosted originals store and keep a verified public reference.
7. Check the GitHub Pages run for **the same commit SHA**, load the gallery URL, and inspect the original image's natural width/height.

## Image quality rules

- Store each received master without recompression, cropping, recoloring, or AI re-generation.
- Serve optimized derivatives only as previews when needed; retain the original and allow opening it.
- Verify image signature, dimensions, bytes, and the network URL that was actually deployed.
- The museum uses one chronological wall; do not create separate rooms for each batch.
- A source inventory entry is not a published painting.

## Current limitation

The GitHub connection can write text and Git objects, but no direct connector-to-connector binary upload from a ChatGPT Library file is exposed here. A local export plus the importer is presently the reliable way to move source pixels into this repository.
