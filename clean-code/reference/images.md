# Rule 19 in detail: every image fitted to its box

An image ships at the size of the box that shows it, cropped to that box's ratio, compressed, and
in WebP, with a 1x and a 2x file. An SVG stays SVG. This holds in an audit and every time code
places an image.

## 1. What the code says

`checks/project/images.py` reads every raster image in the scope and every reference to it in
code and prose. It flags:

- a PNG, JPEG, GIF, BMP or TIFF that is not WebP (favicons, touch icons and Open Graph images are
  exempt, their format is imposed);
- a file over `max_image_kb`, or heavier than `max_bytes_per_pixel`;
- natural pixels beyond twice the box, or a ratio more than 2 % off the box, which means a crop;
- an `<img>` without `width` and `height`, or without a 1x and 2x `srcset`;
- an image no file references, which is dead code (rule 3).

The box comes from the `width` and `height` written within three lines of the reference. That is
the static guess: CSS, a grid or `object-fit` can change it.

## 2. What the page shows

When the project renders pages, measure the real boxes, always through the `chrome-bidi` skill and
always headless: no window ever opens on the user's screen. Start the dev server, then:

```bash
python -I "<chrome-bidi>/scripts/measure_images.py" --url <page url> --widths 390,1440 --out "<run>/boxes-home.json"
```

390 is a phone, 1440 a desktop. Add the widths where the CSS changes layout, read from its media
queries. Measure every page that shows an image of the scope, one `--out` file per page, then stop
the server.

Rerun the measure with every file of live boxes. They override the static guess, and the largest
box per image wins:

```bash
python -I "<skill>/scripts/measure.py" <scope> --boxes "<run>/boxes-home.json" --boxes "<run>/boxes-about.json"
```

A project with no page to render (a library, a CLI) keeps the static guess, and the run says so
through `findings.py unmeasured --rule 19 --why "..."` when no box could be read at all.

## 3. Fit the file

For each confirmed rule 19 finding:

```bash
python -I "<skill>/scripts/apply/fit_image.py" <image> --box 400x400 --box 350x200:767 --focus 0.5,0.4 --prefix /img/
```

`--box` is the box in CSS pixels, once per layout. `:767` means "up to a 767 px wide viewport",
the breakpoint read from the CSS; the box without it is the default. `--focus` keeps that point of
the image in frame, as fractions of width and height: look at the image before cropping a face or
a product off. The script never upscales, writes `<name>-<w>x<h>.webp` next to the source, keeps
whichever of lossy (quality `webp_quality`) or lossless is lighter, and prints the markup to paste:
an `<img>` with its `srcset`, or a `<picture>` when the layouts differ.

On Git Bash a `--prefix` starting with `/` is rewritten into a Windows path: run the command with
`MSYS_NO_PATHCONV=1` in front.

A line that says "heavier than the source" means the source compresses better as it is: keep the
source format for that size and say so in the plan.

## 4. Swap the references

Replace every reference with the printed markup, adapted to the framework: Next's `<Image>` takes
`width`, `height` and `sizes`, and builds its own `srcset`; a CSS background takes `image-set()`.
Delete the old file with `git rm` once nothing references it, then measure again: the finding must
be gone and the page must look the same, checked by a headless screenshot through `chrome-bidi`
at each width.
