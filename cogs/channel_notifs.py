import websockets
from websockets.exceptions import ConnectionClosedError

import discord
from discord import app_commands
from discord.ext import commands

import asyncio
import aiohttp

import pprint
import json

async def register_twitch(channel_name: str) -> None:

    """Register a twitch channel to receive notifications."""
    headers = {"Authorization": "Bearer token",
               "Client-Id": "ieo1c827mnoz7xj7atyxp3ljdtzvsk"}

    async with aiohttp.ClientSession() as session:
        # Gets user data from twitch
        async with session.get(f"https://api.twitch.tv/helix/users?login={channel_name}",
                               headers=headers) as id_resp:
            user_data = await id_resp.json()
            print(user_data)
            # await interaction.response.send_message(user_data)

        data = {"type": "stream.online",
                "version": "1",
                "condition": {"broadcaster_user_id": user_data["data"][0]["id"]},
                "transport": {"method": "webhook",
                              "callback": "https://*****.ngrok.io",
                              "secret": "secret"}
                }

        # Subscribes to EventSub
        async with session.post("https://api.twitch.tv/helix/eventsub/subscriptions",
                                json=data,
                                headers=headers) as resp:
            print(await resp.json())
            # await interaction.response.send_message(await resp.json())

    # embed = discord.Embed(title="Registering a Twitch Channel.",
    #                       description="To register your twitch channel to send a notification when you go live, "
    #                                   "click [this link]() to register your twitch channel.")

class Notifs(commands.Cog):
    """
    Make me notify this server whenever a Twitch channel goes live, a YouTube video is posted, and more! [INCOMPLETE]
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @commands.is_owner()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def test_webhook(self, interaction: discord.Interaction, channel_name: str):
        """Test the webhook."""

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": "Bearer token",
                       "Client-Id": "ieo1c827mnoz7xj7atyxp3ljdtzvsk"}

            async with session.get(f"https://api.twitch.tv/helix/users?login={channel_name}",
                                   headers=headers) as id_resp:
                user_data = await id_resp.json()

            async with session.post(f"https://*****.ngrok.io/createWebhook/{user_data['data'][0]['id']}"):
                await interaction.response.send_message(await id_resp.json())
        # await register_twitch(channel_name)

"""
    @app_commands.command()
    @commands.is_owner()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def start_websocket(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        async with websockets.connect("wss://eventsub-beta.wss.twitch.tv/ws") as websocket:
            welcome_message = json.loads(await websocket.recv())

            await register_twitch(welcome_message["payload"]["session"]["id"], "twitch_api_testing")

            while True:
                try:
                    message = await websocket.recv()
                    guild = interaction.guild
                    channel = guild.get_channel(1040784052510261288)
                    await channel.send(message)
                except ConnectionClosedError:
                    print("Connection closed.")
                    break

    @app_commands.command()
    @commands.is_owner()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def websocket_test(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with websockets.connect("wss://eventsub-beta.wss.twitch.tv/ws") as websocket:
            welcome_message = await websocket.recv()
            while True:
                message = await websocket.recv()
                guild = interaction.guild
                channel = guild.get_channel(1040784052510261288)
                await channel.send(message)
"""


async def setup(bot):
    await bot.add_cog(Notifs(bot))
