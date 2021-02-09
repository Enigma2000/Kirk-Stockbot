#!/bin/python
import Parsers.Environment
from Parsers.ParserException import ParserException
import Parsers.financialmodelingprep_topgainers
import Agents.Environment
import Agents.week_hold
import profile_loader
import alpaca_markets
import os
import datetime
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from context_list_wrapper import ContextList



# TODO: Host on Raspberry Pi

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEV_USER = os.getenv('DISCORD_USER_ID')
ACTIVE = True

print("Agents loaded: {0}".format(list(Agents.Environment.AGENT_LIST.keys())))
print("Parsers loaded: {0}".format(list(Parsers.Environment.PARSER_LIST.keys())))
print("Profiles loaded: {0}".format([profile.NAME for profile in profile_loader.profile_list]))
bot = commands.Bot(command_prefix='$')
channels = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    if len(bot.guilds) < 11:
        for guild in bot.guilds:
            print("Connected to: " + guild.name)
    else:
        print("Connected to {0} servers".format(len(bot.guilds)))
    asyncio.ensure_future(check_time())

@bot.command(name="execute")
async def execute(context):
    if type(context) != ContextList and context.author.id != DEV_USER:
        await context.send("Sorry, you are not the developer.")
        return
    for profile in profile_loader.profile_list:
        if profile.PARSER in Parsers.Environment.PARSER_LIST and profile.AGENT in Agents.Environment.AGENT_LIST:
            print("Executing profile {0}".format(profile.NAME))
            trader = alpaca_markets.PaperTrader(profile.get_info_dict())
            tickers = Parsers.Environment.PARSER_LIST[profile.PARSER](profile.get_info_dict())
            orders = Agents.Environment.AGENT_LIST[profile.AGENT](tickers, trader.get_positions(), trader.cash, profile.get_info_dict())

            buying = '\n'.join(["{0} x {1}".format(symbol, count) for symbol, count in orders["buy"]])
            if len(orders["buy"]) == 0: buying = "NONE"

            selling = '\n'.join(["{0} x {1}".format(symbol, count) for symbol, count in orders["sell"]])
            if len(orders["sell"]) == 0: selling = "NONE"

            orders_embed = discord.Embed(title="__Orders__", colour=discord.Colour(0xF5A623),
                                  timestamp=datetime.datetime.utcnow())

            orders_embed.set_footer(text="I am not a financial advisor. I just like these stocks.")
            orders_embed.add_field(name="*__BUYING__*", value=buying, inline=True)
            orders_embed.add_field(name="*__SELLING__*", value=selling, inline=True)
            orders_embed.add_field(name="​", value="​")
            orders_embed.add_field(name="Cash:", value=f"${trader.cash}")

            await context.send(f"Here is my current portfolio for profile {profile.NAME}:", embed=portfolio_embed(trader))
            await context.send(f"Here are my decisions for profile {profile.NAME} today:", embed=orders_embed)
            trader.execute_orders(orders)


@bot.command(name="ping")
async def ping(context):
    await context.send("What? Do I look like @Artsy?")


@bot.command(name="invite")
async def invite(context):
    await context.send("https://discord.com/api/oauth2/authorize?client_id=806937025131446332&permissions=8&scope=bot")


@bot.command(name="portfolio")
async def publish_portfolios(context):
    for profile in profile_loader.profile_list:
        if profile.PARSER in Parsers.Environment.PARSER_LIST and profile.AGENT in Agents.Environment.AGENT_LIST:
            trader = alpaca_markets.PaperTrader(profile.get_info_dict())
            await context.send(f"Here is my current portfolio for profile {profile.NAME}:",
                               embed=portfolio_embed(trader))

@bot.command(name="setchannel")
async def setchannel(context):
    channels[context.guild] = context.channel
    await context.send("Okay, I'll publish my moves here!")

def portfolio_embed(trader):
    neg_color = discord.Colour(0xD0021B)
    pos_color = discord.Colour(0x7ED321)
    percent_diff_total = float(trader.equity) / float(trader.initial)
    percent_diff_last = float(trader.equity) / float(trader.last_equity)
    if (percent_diff_last<1):
        color = neg_color
    else:
        color = pos_color
    timestamp = datetime.datetime.utcnow()
    positions = trader.get_positions()
    positions_str = '\n'.join(["{0} x {1}".format(symbol, count) for symbol, count in positions])
    if len(positions) == 0: positions_str = "NONE"

    agent_name = trader._profile_info["AGENT"]
    parser_name = trader._profile_info["PARSER"]

    agent_name = Agents.Environment.DISPLAY_NAMES[agent_name] if agent_name in Agents.Environment.DISPLAY_NAMES else agent_name
    parser_name = Parsers.Environment.DISPLAY_NAMES[parser_name] if parser_name in Parsers.Environment.DISPLAY_NAMES else parser_name

    portfolio_embed = discord.Embed(colour=color, timestamp=timestamp)

    portfolio_embed.set_footer(text="I am not a financial advisor. I just like these stocks.")

    portfolio_embed.add_field(name="Equity:", value=f"${trader.equity}")
    portfolio_embed.add_field(name="Parser:", value=f"{parser_name}", inline=True)
    portfolio_embed.add_field(name="​", value="​", inline=False)
    portfolio_embed.add_field(name="Cash:", value=f"${trader.cash}")
    portfolio_embed.add_field(name="Agent:", value=f"{agent_name}", inline=True)
    portfolio_embed.add_field(name="​", value="​", inline=False)
    portfolio_embed.add_field(name="Percent (To Date)", value=f"{round((percent_diff_total-1)*100,2)}%", inline=True)
    portfolio_embed.add_field(name="Percent (Last)", value=f"{round((percent_diff_last-1)*100,2)}%", inline=True)
    portfolio_embed.add_field(name="​", value="​", inline=False)
    portfolio_embed.add_field(name="Positions:", value=f"{positions_str}", inline=False)

    return portfolio_embed


async def check_time():
    context_list = ContextList()
    has_executed = False
    while ACTIVE:
        if it_is_market_open() and not has_executed:
            print("executing")
            for guild in bot.guilds:
                if guild in channels:
                    context_list.add(channels[guild])
            await execute(context_list)
            has_executed = True
        elif not it_is_market_open() and has_executed:
            print("resetting")
            has_executed = False
        else:
            print("n/a")
        await asyncio.sleep(120)
    print("killing loop")
    return

def it_is_market_open():
    now = datetime.datetime.utcnow().time()
    market_open = datetime.time(14, 30) # 8:30 AM
    end_period = datetime.time(15, 30) # 9:30 AM
    if now > market_open and now < end_period:
        return True
    return False

@bot.command(name="killloop")
async def killloop(context):
    global ACTIVE
    if context.author.id != DEV_USER:
        await context.send("Sorry, you are not the developer.")
        return
    ACTIVE = False

bot.run(TOKEN)