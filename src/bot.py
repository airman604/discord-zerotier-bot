#!/usr/bin/env python3

import os
import logging
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

import zt

bot = commands.Bot(command_prefix='$')
slash = SlashCommand(bot, sync_commands=True)
zero_tier = None

@bot.event
async def on_ready():
    logging.info("Ready!")

@slash.subcommand(base="zerotier-bot", name="help",
                    description="Get help for ZeroTier Bot")
async def _help(ctx):
    await ctx.send(f"Hey {ctx.author}, usage: `/zerotier-bot register <node_id>`. To find out your node ID run `zerotier-cli info` on your host.")

@slash.subcommand(base="zerotier-bot", name="register",
                    description="Submit a request to authorize your ZeroTier node",
                    options=[
                        create_option(
                            name="node_id",
                            description="Node ID to authorize for ZeroTier access.",
                            option_type=3,
                            required=True
                        )
                    ])
async def _register(ctx, node_id: str):
    global zero_tier

    logging.info(f"Register command received from {ctx.author} for node {node_id}")

    zt_node = zero_tier.get_member(node_id)
    if zt_node == None:
        logging.info(f"Node {node_id} not found in ZeroTier")
        await ctx.send(f"Hey {ctx.author}, ZeroTier node {node_id} could not be found, did you run `zerotier-cli join {zero_tier.zt_network}`?")
        return

    if zt_node["config"]["authorized"]:
        logging.info(f"Node {node_id} already authorized")
        await ctx.send(f"Hey {ctx.author}, your node is already authorized, check by running `zerotier-cli listnetworks`, contact admin if you're still having issues.")
        return

    if "ban" in zt_node["description"]:
        logging.warning(f"Node {node_id} is banned")
        await ctx.send(f"Hey {ctx.author}, your node have been banned, please contact admin.")
        return

    name = str(ctx.author)
    if zero_tier.authorize_member(node_id, name):
        logging.info(f"Node {node_id} successfully authorized")
        await ctx.send(f"Hey {ctx.author}, your node has been authorized, check by running `zerotier-cli listnetworks`")
    else:
        logging.error(f"Node {node_id} could not be authorized")
        await ctx.send(f"Hey {ctx.author}, something went wrong, please contact admin.")

def main():
    logging.basicConfig(level=logging.INFO)

    global zero_tier
    zt_token = os.getenv("ZT_TOKEN")
    zt_network = os.getenv("ZT_NETWORK")
    zero_tier = zt.ZeroTier(zt_network, zt_token)

    discord_token = os.getenv("DISCORD_TOKEN")
    bot.run(discord_token)

if __name__ == "__main__":
    main()