# Visual companion

A local page that shows mockups to the user and hands their ticks back as JSON. The server is Python
standard library only, bound to 127.0.0.1 on a free port, behind a session key, and keeps
everything in `<temp>/claude-skills/concevoir/<topic>-<stamp>/`, where `<temp>` is the system temp folder
(`tempfile.gettempdir()`). Nothing is installed and nothing lands in the project.

## Start

Run it once the user has picked the page for a visual question:

```bash
python -I "<skill>/scripts/companion.py" start --topic "fiche produit"
```

It prints five lines: `session`, `screens`, `url`, `log` and the `stop` command. Keep them. The
server runs detached at below normal priority and stops by itself after 120 minutes with no page
load and no choice (`--idle <minutes>` changes that).

Give the user the whole URL, key included, as a link they click. They open it in their own browser.
Never open it for them, never through `start` or `explorer`, never in a Chrome you drive.

## Show a screen

Write one HTML file per question into the `screens` folder with the Write tool, a new name each
time: `mise-en-page.html`, then `mise-en-page-v2.html`. The page shows the newest file and reloads
by itself within three seconds of a new one.

A fragment, with no `<html>` or `<!doctype>`, is wrapped in the frame: a header, the light theme, a
note box and the "Envoyer mes choix" button. A full document is served as it is, without the
button, so write fragments whenever an answer is wanted. Every radio button or checkbox in the
fragment is a choice: `name` groups them, `value` is what comes back. Radio buttons take one
answer, checkboxes several.

```html
<h1>Quelle mise en page pour la fiche ?</h1>
<p>La colonne de droite garde le bouton d'achat visible.</p>
<div class="options">
  <label class="option"><input type="radio" name="mise-en-page" value="une-colonne">
    <span>Une colonne<small>Photo en haut, texte dessous.</small></span></label>
  <label class="option"><input type="radio" name="mise-en-page" value="deux-colonnes">
    <span>Deux colonnes<small>Photo à gauche, achat à droite.</small></span></label>
</div>
<div class="split">
  <div class="mockup"><div class="label">Une colonne</div>
    <div class="body"><div class="placeholder">Photo</div><p>Texte de la fiche</p></div></div>
  <div class="mockup"><div class="label">Deux colonnes</div>
    <div class="body"><div class="placeholder">Photo et bouton d'achat</div></div></div>
</div>
```

The frame styles a few classes, enough for wireframes.

| Class | Use |
|---|---|
| `options`, `option` | a list of choice rows; a ticked row turns green |
| `small` inside an option | the line under the option title |
| `split` | blocks side by side, stacked on a narrow screen |
| `mockup` with `label` and `body` | a framed preview with its caption |
| `placeholder` | a dashed block standing for an image or a zone |

An image goes into the `screens` folder and is shown with `src="/files/<name>"`. Text on the page
is French, for the user. Two to four options per screen. Use the real words (the product name, the
real copy) when the question is how it reads, plain grey blocks when it is where things go.

The frame follows `anti-empreinte` `reference/visual.md`: Segoe UI, a light paper background, one
green accent. A mockup that needs its own look sets inline styles, and keeps away from Inter, Space
Grotesk, Geist and the indigo to violet gradient.

## Read the answer

After writing a screen, tell the user in one or two lines what is on it, and that they can tick then
press "Envoyer mes choix", or answer in the conversation. Then end the turn. To be woken by the
button rather than by their next message, start this wait with `run_in_background` first:

```bash
for i in $(seq 120); do grep -q 'sent mise-en-page.html' "<log>" && break; sleep 2; done
```

Whichever comes first, read the choices:

```bash
python -I "<skill>/scripts/companion.py" choices --session "<session>"
```

It prints one line per screen, such as
`mise-en-page.html: sent, mise-en-page = deux-colonnes, note: plus de photo`. "ticked, not sent yet"
means they clicked without confirming: read it as a lean, not an answer. When their message in the
conversation and their ticks disagree, the message wins.

A change to a screen is a new file. When the next question is not visual, write a short fragment
such as `<p class="waiting">La suite se passe dans la conversation.</p>` so the page stops showing
a settled choice.

## Look at the page yourself

To check that a mockup renders, use `chrome-bidi`: its `launch.py` with the URL, a `shot`, read the
image, then `close`. It runs headless on its own port and profile. The user's own Chrome is never
touched.

## Stop

At the end of the brainstorming, and before the task ends at the latest:

```bash
python -I "<skill>/scripts/companion.py" stop --session "<session>"
```

It prints the last choices, asks the server to stop, ends the process only after checking it is
Python, and deletes the session folder. A mockup worth keeping is copied next to the spec in
`.ia/specs/` before the stop. `--keep` leaves the folder in place to look into a fault; delete it
by hand afterwards. `status --session "<session>"` says whether the server still runs; after an
idle stop, `start` again and give the new URL.

## Without the page

When the user prefers text, or the server will not start, describe each option in its
`AskUserQuestion` description, or draw a small ASCII sketch in a code block in the chat.
