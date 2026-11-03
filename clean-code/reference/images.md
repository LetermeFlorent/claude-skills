# Rule 19: every image fitted to its box

An image ships at its box size, cropped to the box ratio, compressed, in WebP, with a 1x and a 2x
file. An SVG stays SVG.

## 1. Static check

`checks/project/images.py` flags: a non-WebP raster (favicons, touch icons and Open Graph images
exempt), a file over `max_image_kb` or `max_bytes_per_pixel`, natural pixels beyond twice the box or
a ratio more than 2 % off the box, an `<img>` without `width`/`height` or without a 1x and 2x
`srcset`, and an unreferenced image (rule 3). The box is the `width` and `height` written within
three lines of the reference, a guess that CSS or `object-fit` can change.

## 2. Live boxes

When the project renders pages, with the dev server running:

```bash
python -I "<chrome-bidi>/scripts/measure_images.py" --url <page url> --widths 390,1440 --out "<run>/boxes-home.json"
```

Add the widths where the CSS media queries change layout. One `--out` per page, then stop the
server. Rerun the measure with every file; the largest box per image wins over the static guess:

```bash
python -I "<skill>/scripts/measure.py" <scope> --boxes "<run>/boxes-home.json" --boxes "<run>/boxes-about.json"
```

With no page to render, declare `findings.py unmeasured --rule 19 --why "..."` when no box could be
read.

## 3. Fit

```bash
python -I "<skill>/scripts/apply/fit_image.py" <image> --box 400x400 --box 350x200:767 --focus 0.5,0.4 --prefix /img/
```

`--box` is the CSS-pixel box, once per layout; `:767` means "up to a 767 px viewport" (breakpoint
read from the CSS), the box without it is the default. `--focus` keeps that point (fractions of
width and height) in frame: look at the image before cropping off a face or product. It never
upscales, writes `<name>-<w>x<h>.webp` next to the source, keeps the lighter of lossy (quality
`webp_quality`) or lossless, and prints the `<img srcset>` or `<picture>` to paste.

On Git Bash a `--prefix` starting with `/` is rewritten into a Windows path: prefix the command with
`MSYS_NO_PATHCONV=1`. A "heavier than the source" line means the source compresses better as is:
keep its format for that size and say so in the plan.

## 4. Swap

Replace every reference with the printed markup, adapted to the framework (Next's `<Image>` takes
`width`, `height`, `sizes`; a CSS background takes `image-set()`). `git rm` the old file once
unreferenced, measure again, and compare headless screenshots at each width.
