# Watashino LaTeX Bot

Watashino LaTeX Bot renders your LaTeX into crisp PNGs and vector PDFs right inside Discord. It supports slash commands, buttons, modals, and even rendering directly from chat messages.

### How to write direct latex code to bot's dm:

<p>
	<img alt="x^2" width="420" src="/assets/howtowritecodedirectlyinbotsdm.png" />
</p>

### How to write inline code if you prefer to:
<img alt="x^2 repeated" width="420" src="/assets/inlineExpressionsusage.png" />

### How your full document render will look like:
<img alt="x^2 repeated" width="420" src="/assets/renderedEquations.png" />

## Discord bot usage

A beautiful website demonstrating commands and usage is available at `index.html` in the root folder. You can open it locally in your browser or host it anywhere.

Prerequisites:
- Python 3.9+
- Ghostscript installed and available on PATH (on Windows: gswin64c or gswin32c)
- A Discord bot token (create at https://discord.com/developers, invite with applications.commands scope)
- Optional: to render messages you just type in chat (like the original Telegram flow), enable the "Message Content Intent" in the Developer Portal and set `DISCORD_ENABLE_MESSAGE_CONTENT=true` in `.env`.

Setup:
1. Install dependencies

```
pip install -r requirements.txt
```

2. Configure environment via `.env`

Copy `.env.example` to `.env` and fill values:

```
copy .env.example .env
notepad .env
```

3. Run the bot

```
python main.py
```

Slash commands:
- `/start` — welcome and quick usage guide
- `/latex code:"$x^2$"` — render to PNG and PDF
- `/settings` — configure caption, DPI, and edit preamble
- `/setdpi 300` — set rendering DPI (100-1000)
- `/getmypreamble` — show your current preamble
- `/getdefaultpreamble` — show default preamble
- `/setcustompreamble` — open a modal to set your preamble

### Render by just typing in chat

Besides `/latex`, you can simply type LaTeX in DMs or in servers (if `DISCORD_ENABLE_MESSAGE_CONTENT=true`):

- Inline math: type `$x^2 + \alpha$`
- Display math: type `\[\int_0^1 x^2\,dx\]`
- Full documents: paste anything containing `\documentclass{...}`
- Code fences: use ```latex ... ``` and the bot will render the code inside

If you type LaTeX-like content without delimiters (e.g., `\frac{a}{b}`), the bot will auto-wrap it: single-line becomes inline `$...$`; multi-line or block-like becomes display `\[...\]`.

### PDF margins and layout

- For standalone expressions (not full documents), the bot produces a tightly-cropped PDF with comfortable padding around the content.
	- Default padding is 24pt on each side. You can change it via environment variable `LATEXBOT_PDF_MARGIN_PT` (value in PostScript points; 72pt = 1 inch).
	- Example: set `LATEXBOT_PDF_MARGIN_PT=36` for 0.5 inch padding.
- If your input includes a full LaTeX document (`\documentclass{...}`), the bot preserves the document’s own page size and margins (no cropping applied), similar to Overleaf output.

## Customization
The main feature of the bot is the customizable preamble used in the document into which your expression will be inserted:
```latex

\documentclass{article}
\usepackage[T1]{fontenc}
...
%You can modify everything above this comment
\begin{document}
<your expression goes here>
\end{document}
```
This means you can include the packages that you need or define your own expressions and commands which will afterwards be available when rendering. The bot works with a standard LaTeX installation (TeX Live or MiKTeX) and Ghostscript.

Additionally, it is possible to change how the messages will look like after they've been sent, i.e. include the raw expression in the caption of the image or not, or set the resolution of the picture to control its size.

The customization applies both to slash commands and chat message rendering.

## Notes
- Preamble length in the modal is limited to 4000 characters for safety.
- Rendering dependencies: `pdflatex` and Ghostscript must be available on PATH.

## Assets
- Example images used above are located under `resources/test/`.
- You can replace or add your own examples and reference them in this README.
