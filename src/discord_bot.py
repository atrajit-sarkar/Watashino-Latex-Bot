import os
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from src.LatexConverter import LatexConverter
from src.PreambleManager import PreambleManager
from src.ResourceManager import ResourceManager
from src.UserOptionsManager import UserOptionsManager
from src.UsersManager import UsersManager
from src.LoggingServer import LoggingServer


class PreambleModal(discord.ui.Modal, title="Set Custom LaTeX Preamble"):
    preamble = discord.ui.TextInput(label="Preamble", style=discord.TextStyle.paragraph, required=True, max_length=4000)

    def __init__(self, pm: PreambleManager, rm: ResourceManager, user_id: int):
        super().__init__()
        self.pm = pm
        self.rm = rm
        self.user_id = user_id
        self.logger = LoggingServer.getInstance()

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        valid, msg = self.pm.validatePreamble(str(self.preamble.value))
        if valid:
            self.pm.putPreambleToDatabase(self.user_id, str(self.preamble.value))
            await interaction.followup.send(self.rm.getString("preamble_registered"), ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)


class SettingsView(discord.ui.View):
    def __init__(self, uom: UserOptionsManager, user_id: int, pm: Optional[PreambleManager] = None, rm: Optional[ResourceManager] = None):
        super().__init__(timeout=180)
        self.uom = uom
        self.user_id = user_id
        self.pm = pm
        self.rm = rm

    @discord.ui.button(label="Show code in caption", style=discord.ButtonStyle.primary)
    async def code_on(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.uom.setCodeInCaptionOption(self.user_id, True)
        await interaction.response.send_message("Enabled code in caption.", ephemeral=True)

    @discord.ui.button(label="Hide code in caption", style=discord.ButtonStyle.secondary)
    async def code_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.uom.setCodeInCaptionOption(self.user_id, False)
        await interaction.response.send_message("Disabled code in caption.", ephemeral=True)

    @discord.ui.button(label="Edit preamble", style=discord.ButtonStyle.success)
    async def edit_preamble(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.pm or not self.rm:
            await interaction.response.send_message("Preamble manager not available.", ephemeral=True)
            return
        await interaction.response.send_modal(PreambleModal(self.pm, self.rm, interaction.user.id))


class InLatexDiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # Enable message content intent only if explicitly requested via env var
        enable_message_content = os.environ.get("DISCORD_ENABLE_MESSAGE_CONTENT", "").lower() in ("1", "true", "yes", "on")
        if enable_message_content:
            intents.message_content = True
        # Use mention-only prefix to avoid conflicts with slash commands when users type '/start' as plain text
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

        self.logger = LoggingServer.getInstance()
        self.rm = ResourceManager()
        self.uom = UserOptionsManager()
        self.um = UsersManager()
        self.pm = PreambleManager(self.rm)
        self.converter = LatexConverter(self.pm, self.uom)

    async def setup_hook(self) -> None:
        guild_id = os.environ.get("DISCORD_GUILD_ID")
        if guild_id and guild_id.isdigit():
            guild = discord.Object(id=int(guild_id))
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self):
        self.logger.debug("Discord bot logged in as %s", self.user.name)
        # Ensure dirs/files exist
        os.makedirs("build", exist_ok=True)
        os.makedirs("log", exist_ok=True)

    async def on_message(self, message: discord.Message):
        # Ignore our own messages and other bots
        if message.author.bot:
            return
        # Always allow DMs; for guild messages require message content intent env toggle
        in_dm = message.guild is None
        enable_guild_msgs = os.environ.get("DISCORD_ENABLE_MESSAGE_CONTENT", "").lower() in ("1", "true", "yes", "on")

        # Heuristics to detect LaTeX content
        content = message.content or ""
        content_stripped = content.strip()
        has_latex_markers = (
            "\\documentclass" in content_stripped or
            content_stripped.startswith("$") or
            content_stripped.startswith("\\[") or
            content_stripped.startswith("\\(") or
            content_stripped.startswith("\\begin") or
            (content_stripped.count("$") >= 2)
        )

        # Support ```latex code blocks
        if content_stripped.lower().startswith("```latex") and content_stripped.endswith("```"):
            # Extract inner code
            inner = content_stripped[len("```latex"):].strip()
            if inner.endswith("```"):
                inner = inner[:-3].strip()
            content_stripped = inner
            has_latex_markers = True

        # Only proceed if allowed and markers found
        if (in_dm or enable_guild_msgs) and has_latex_markers and content_stripped:
            try:
                user_id = message.author.id
                session_id = f"{message.id}_{user_id}"
                image_stream, pdf_stream = self.converter.convertExpression(content_stripped, user_id, session_id, returnPdf=True)
                image_stream.seek(0)
                pdf_stream.seek(0)
                files = [
                    discord.File(fp=image_stream, filename="expression.png"),
                    discord.File(fp=pdf_stream, filename="expression.pdf")
                ]
                await message.reply(files=files)
            except ValueError as err:
                await message.reply(f"Syntax error or processing issue:\n{err}")
            except Exception as err:
                self.logger.warn("Unhandled exception in message render: %s", str(err))
                await message.reply(f"Unexpected error during rendering. {type(err).__name__}: {err}")

        # Keep command processing working
        await self.process_commands(message)


bot = InLatexDiscordBot()


@bot.tree.command(name="start", description="Introduction and demo of the LaTeX bot")
async def start_cmd(interaction: discord.Interaction):
    user_id = interaction.user.id
    # Register known user
    try:
        _ = bot.um.getUser(user_id)
    except Exception:
        bot.um.setUser(user_id, {})
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(bot.rm.getString("greeting_line_one"), ephemeral=True)
    # send demo image if available
    demo_path = os.path.join("resources", "demo.png")
    if os.path.exists(demo_path):
        await interaction.followup.send(file=discord.File(demo_path), ephemeral=True)
    await interaction.followup.send(bot.rm.getString("greeting_line_two"), ephemeral=True)


@bot.tree.command(name="latex", description="Render a LaTeX expression to image (and PDF)")
@app_commands.describe(code="Your LaTeX expression. Use $...$ for math.")
async def latex_cmd(interaction: discord.Interaction, code: str):
    await interaction.response.defer(thinking=True)
    user_id = interaction.user.id
    session_id = f"{interaction.id}_{user_id}"
    try:
        image_stream, pdf_stream = bot.converter.convertExpression(code, user_id, session_id, returnPdf=True)
        image_stream.seek(0)
        pdf_stream.seek(0)
        files = [
            discord.File(fp=image_stream, filename="expression.png"),
            discord.File(fp=pdf_stream, filename="expression.pdf")
        ]
        await interaction.followup.send(files=files)
    except ValueError as err:
        await interaction.followup.send(f"Syntax error or processing issue:\n{err}", ephemeral=True)
    except Exception as err:
        bot.logger.warn("Unhandled exception in /latex: %s", str(err))
        await interaction.followup.send(f"Unexpected error during rendering.\n{type(err).__name__}: {err}", ephemeral=True)


@bot.tree.command(name="settings", description="Open settings to configure caption, DPI and preamble")
async def settings_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("Adjust your preferences:", view=SettingsView(bot.uom, interaction.user.id, bot.pm, bot.rm), ephemeral=True)


@bot.tree.command(name="setdpi", description="Set image DPI (100-1000)")
@app_commands.describe(dpi="DPI value between 100 and 1000")
async def setdpi_cmd(interaction: discord.Interaction, dpi: int):
    if dpi < 100 or dpi > 1000:
        await interaction.response.send_message(bot.rm.getString("dpi_value_error"), ephemeral=True)
        return
    bot.uom.setDpiOption(interaction.user.id, dpi)
    await interaction.response.send_message(bot.rm.getString("dpi_set") % dpi, ephemeral=True)


@bot.tree.command(name="getmypreamble", description="Show your current preamble")
async def getmypreamble_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        preamble = bot.pm.getPreambleFromDatabase(interaction.user.id)
        await interaction.followup.send(bot.rm.getString("your_preamble_custom") + preamble, ephemeral=True)
    except KeyError:
        preamble = bot.pm.getDefaultPreamble()
        await interaction.followup.send(bot.rm.getString("your_preamble_default") + preamble, ephemeral=True)


@bot.tree.command(name="getdefaultpreamble", description="Show the default preamble")
async def getdefaultpreamble_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(bot.rm.getString("default_preamble") + bot.pm.getDefaultPreamble(), ephemeral=True)


@bot.tree.command(name="setcustompreamble", description="Set your custom preamble (opens a modal)")
async def setcustompreamble_cmd(interaction: discord.Interaction):
    modal = PreambleModal(bot.pm, bot.rm, interaction.user.id)
    await interaction.response.send_modal(modal)


def run():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable")
    bot.run(token)


@bot.tree.command(name="diagnose", description="Check if pdflatex and Ghostscript are available on PATH")
async def diagnose_cmd(interaction: discord.Interaction):
    import shutil
    await interaction.response.defer(ephemeral=True)
    pdflatex_path = shutil.which("pdflatex")
    gs_path = shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c")
    lines = []
    if pdflatex_path:
        lines.append(f"pdflatex: found at {pdflatex_path}")
    else:
        lines.append("pdflatex: NOT FOUND — install TeX Live/MiKTeX and ensure it’s on PATH")
    if gs_path:
        lines.append(f"Ghostscript: found at {gs_path}")
    else:
        lines.append("Ghostscript: NOT FOUND — install Ghostscript and ensure 'gs', 'gswin64c' or 'gswin32c' is on PATH")
    await interaction.followup.send("\n".join(lines), ephemeral=True)


if __name__ == "__main__":
    run()
