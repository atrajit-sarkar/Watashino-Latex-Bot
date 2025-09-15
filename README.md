<img src=https://cloud.githubusercontent.com/assets/3819012/21799537/1dab0e90-d733-11e6-88ab-76ebd37275c7.jpg /> 

LaTeX rendering bot core with Telegram handlers (original project) and a Discord bot interface. The Discord bot exposes the same functionality with slash commands and UI.

## Description and general usage
This bot converts LaTeX expressions to .png images when called in inline mode (@inlatexbot \<your expression\>) and then shows you the image it has generated from your code. Everything happens live, so you can just gradually type and continuously monitor the result. When expression contains errors, they will be displayed instead of the image. Finally, when you are ready, click or tap the suggested picture to send it.

<img width=200 src=https://cloud.githubusercontent.com/assets/3819012/21800504/56bf38ec-d737-11e6-8b8b-e4e3b90d43ae.png /><img width=200 src=https://cloud.githubusercontent.com/assets/3819012/21800503/56be411c-d737-11e6-8598-e43fb7126eb3.png /><img width=200 src=https://cloud.githubusercontent.com/assets/3819012/21800505/56e9283c-d737-11e6-9195-1be0c2ca046c.png />

Since v2.0 the bot also supports direct conversion of LaTeX expressions in a conversation. You can send it messages containing the code, and it will respond with a .pdf file and an image containing the expression. This allows larger (than in the inline mode) expressions to be converted; moreover, .pdf file contains graphics in vector format, so further processing of the expression in a VG application, i.e. in Inkscape, is possible.

## Discord bot usage

A simple website demonstrating commands and usage is available at `website/index.html`. You can open it locally in your browser.

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
- `/start` — greeting and demo
- `/latex code:"$x^2$"` — render to PNG and PDF
- `/settings` — toggle caption code on/off with buttons
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
This means you can inlude the packages that you need or define your own expressions and commands which will be afterwards available in the inline mode. The bot uses full installation of Texlive2016, so any of its packages should be within the bot's reach.

Additionally, it is possible to change how the messages will look like after they've been sent, i.e. include the raw expression in the caption of the image or not, or set the resolution of the picture to control its size.

The customization applies both to the inline and standard modes.

## Limitations
The expression length is limited by the length of the inline query to approximately 250 characters (despite the statement in the API docs that inline queries can span up to 512 characters)

The preamble length is currently limited by 4000 characters as the longest messages that Telegram can send in one piece are of 4096 chars.

Bot should be currently online, so in case it's down it's either maintenance or some emergency. Also, feel free to open an issue if you find a bug or contact me <a href=http://t.me/fedorovgp>directly</a> in Telegram should you have any related questions.

## Support the project
https://www.donationalerts.com/r/glebfedorov
