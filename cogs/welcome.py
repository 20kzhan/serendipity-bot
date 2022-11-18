import asqlite

import string

import discord
from discord.ext import commands

class Welcome(commands.Cog):
    """
    Give new users a warm welcome! (And/Or send them off when they leave. But nobody would do that, right?)
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with asqlite.connect("data.db") as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT welcome_channel, welcome_message FROM guild_settings WHERE id = ?",
                                     (member.guild.id,))
                data = await cursor.fetchone()
                if not data:
                    await cursor.execute("INSERT INTO guild_settings VALUES (?, ?, ?, ?)",
                                         (member.guild.id, None, None, None))
                    return

                if data[0] and data[1]:
                    guild = member.guild
                    channel = guild.get_channel(data[0])

                    welcome_variables = {"user": member.mention,
                                         "user.id": member.id,
                                         "user.name": member.name,
                                         "user.discriminator": member.discriminator,
                                         "user.idname": member.name + "#" + member.discriminator,
                                         "user.avatar_url": member.avatar_url,
                                         "server": guild.name,
                                         "server.name": guild.name,
                                         "server.id": guild.id,
                                         "server.icon_url": guild.icon_url,
                                         "server.owner_id": guild.owner_id,
                                         "server.owner": guild.owner.mention,
                                         "server.member_count": guild.member_count}

                    await channel.send(data[1].safe_substitute(**welcome_variables))

async def setup(bot):
    await bot.add_cog(Welcome(bot))