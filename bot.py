import asqlite

import discord
from discord.ext import commands

from typing import Optional, Literal

import time
import os

VERSION = 0.1
INTENTS = discord.Intents().all()


async def get_prefix(_, message):
    async with asqlite.connect("data.db") as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT prefix FROM guild_settings WHERE id = ?", (message.guild.id,))
            prefix = await cursor.fetchone()
            if prefix:
                return prefix
            else:
                return "s!"


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=INTENTS,
                         status=discord.Status.online,
                         owner_ids=[843230753734918154, 468941074245615617],
                         activity=discord.Game("Fall Guys"))

    async def on_ready(self):
        print("Hello Kyle :)")
        print(f"I am currently running v{VERSION} and am logged in as {self.user} with id {self.user.id}.")

        self.remove_command('help')

        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and not filename.startswith("_"):
                await bot.load_extension(f'cogs.{filename[:-3]}')


bot = Bot()


@bot.command(hidden=True)
@commands.guild_only()
@commands.is_owner()
async def sync(
        ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) \
        -> None:
    """
    !sync -> global sync
    !sync ~ -> sync current guild
    !sync * -> copies all global app commands to current guild and syncs
    !sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
    !sync id_1 id_2 -> syncs guilds with id 1 and 2
    """

    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid Command Used.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You are missing permissions to run this command.\n"
                       f"If you think this is a mistake, please contact {bot.application_info().owner}.")
    elif isinstance(error, commands.ExtensionNotLoaded):
        await ctx.send("The extension(s) you are trying to unload are currently not loaded.")
    elif isinstance(error, commands.ExtensionAlreadyLoaded):
        await ctx.send("The extension(s) you are trying to load are currently already loaded.")
    elif isinstance(error, commands.ExtensionNotFound):
        await ctx.send("The extension you are trying to load does not exist.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("The command you are trying to call can only be called in a server, not a DM.")
    else:
        embed = discord.Embed(title='An Error Occurred, and has been sent to the developers.',
                              description='', colour=discord.Colour.red())
        embed.add_field(name="Error", value=error)
        bug_message = await ctx.send(embed=embed)

        guild = bot.get_guild(1028420851772690483)
        dev = guild.get_member(843230753734918154)
        await dev.send(bug_message.jump_url)
        flabbergasted = "<:flabbergasted:1039792731423248414>" * 3
        embed.title = f"{flabbergasted} ERROR {flabbergasted}"
        await dev.send(embed=embed)
        await dev.send(f"The command `{ctx.command.name}` failed to run properly.")


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    loaded_cogs = ''
    if extension != '~':
        await bot.load_extension(extension)
        loaded_cogs += f'\U000023eb {extension}'
    else:
        for filename in os.listdir('cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
                loaded_cogs += f'\U000023eb cogs.{filename[:-3]}\n\n'
        loaded_cogs = loaded_cogs[:-2]
    await ctx.send(loaded_cogs)


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    unloaded_cogs = ''
    if extension != '~':
        await bot.unload_extension(extension)
        unloaded_cogs += f'\U000023ec {extension}'
    else:
        for filename in os.listdir('cogs'):
            if filename.endswith('.py'):
                await bot.unload_extension(f'cogs.{filename[:-3]}')
                unloaded_cogs += f'\U000023ec cogs.{filename[:-3]}\n\n'
        unloaded_cogs = unloaded_cogs[:-2]
    await ctx.send(unloaded_cogs)


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension="~"):
    reload_start = time.time()
    reloaded_cogs = ''
    if extension != '~':
        await bot.unload_extension(extension)
        await bot.load_extension(extension)
        reloaded_cogs += f'\U0001f502 {extension}'
    else:
        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and not filename.startswith("_"):
                try:
                    await bot.unload_extension(f'cogs.{filename[:-3]}')
                except commands.ExtensionNotLoaded:
                    pass
                await bot.load_extension(f'cogs.{filename[:-3]}')
                reloaded_cogs += f'\U0001f501 cogs.{filename[:-3]}\n\n'
        reloaded_cogs = reloaded_cogs[:-2]
    await ctx.message.add_reaction('<a:ReloadCheck:1028467537920401428>')
    reload_end = time.time()
    await ctx.send(f'{reloaded_cogs}\nTook {reload_end - reload_start} to reload all')

bot.run("Token")
