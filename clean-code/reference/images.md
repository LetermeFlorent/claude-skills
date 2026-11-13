# Rule 19: every image fitted to its box

Image ships at its box size, cropped to box ratio, compressed, in WebP, with 1x and 2x file. SVG
stays SVG.

## 1. Static check

`checks/project/images.py` flags: non-WebP raster (favicons, touch icons and Open Graph images
exempt), file over `max_image_kb` or `max_bytes_per_pixel`, natural pixels beyond twice the box or
ratio more than 2 % off the box, `<img>` without `width`/`height` or without 1x and 2x `srcset`,
unreferenced image (rule 3, references counted over whole project). Box = `width` and `height`
written within three lines of reference, a guess CSS or `object-fit` can change.

## 2. Live boxes

When project renders pages, dev server running:

```bash
python -I "<browser-bidi>/scripts/measure_images.py" --url <page url> --widths 390,1440 --out "<run>/boxes-home.json"
```

Add widths where CSS media queries change layout. One `--out` per page, then stop server. Rerun
measure with every file; largest box per image wins over static guess:

```bash
python -I "<skill>/scripts/measure.py" <scope> --boxes "<run>/boxes-home.json" --boxes "<run>/boxes-about.json"
```

This makes a new run: audit step 3 scan comes after it. No page to render: declare
`findings.py unmeasured --rule 19 --why "..."` when no box could be read.

## 3. Fit

```bash
python -I "<skill>/scripts/apply/fit_image.py" <image> --box 400x400 --box 350x200:767 --focus 0.5,0.4 --prefix /img/
```

`--box` = CSS-pixel box, once per layout; `:767` means "up to a 767 px viewport" (breakpoint read
from CSS), box without it is default. `--focus` keeps that point (fractions of width and height) in
frame: look at image before cropping off a face or product. Never upscales, writes
`<name>-<w>x<h>.webp` next to source, keeps lighter of lossy (quality `webp_quality`) or lossless,
prints `<img srcset>` or `<picture>` to paste.

Git Bash rewrites `--prefix` starting with `/` into Windows path: prefix command with
`MSYS_NO_PATHCONV=1`. "heavier than the source" line = source compresses better as is: keep its
format for that size, say so in plan.

## 4. Swap

Replace every reference with printed markup, adapted to framework (Next's `<Image>` takes `width`,
`height`, `sizes`; CSS background takes `image-set()`). `git rm` old file once unreferenced, measure
again, compare headless screenshots at each width.
