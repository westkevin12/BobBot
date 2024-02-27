import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import ffmpeg
import random
from yt_dlp import YoutubeDL
import asyncio
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import json
import os
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

#set intents
intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.presences = True
intents.typing = True
intents.voice_states = True
intents.webhooks = True
#initialize bot
bot = commands.Bot(command_prefix='bob ', intents=intents)

(botspam) = 410186801026826240

@app.route('/sendEmbed', methods=['POST'])
def send_embed():
    try:
        data = request.get_json()
        message = data.get("message")
        channel = bot.get_channel(botspam)

        if channel:
            embed = discord.Embed(title="Order", description=message, color=discord.Color.green())
            asyncio.run(channel.send(embed=embed))
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Channel not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    #set status to Watching noobs get pwned
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="noobs get pwned"))

# Check if the user has any of the allowed roles
def is_allowed(ctx):
    allowed_roles = ["ADMIN", "DEV", "Owner"]
    return any(role.name in allowed_roles for role in ctx.author.roles)

with open('items_with_images.json', 'r') as json_file:
    items_with_images = json.load(json_file)

def get_item_image_url(item_name):
    best_match, _ = process.extractOne(item_name, items_with_images.keys())
    
    return items_with_images.get(best_match)

@bot.command()
async def price(ctx, *, item_name: str):
    # Load the ItemList.txt file and search for the item name
    with open("ItemList.txt", "r") as f:
        # Check for known abbreviations and synonyms
        if item_name == "glory":
            item_name = "amulet of glory"
        elif item_name == "zgs":
            item_name = "zaros godsword"   
        elif item_name == "hsr":
            item_name = "Hazelmere's signet ring"
        elif item_name == "bsh":
            item_name = "black santa hat"
        elif item_name == "botlg":
            item_name = "Bow of the Last Guardian"
        elif item_name == "green phat":
            item_name = "Green partyhat"
        elif item_name == "blue phat":
            item_name = "Blue partyhat"
        elif item_name == "red phat":
            item_name = "Red partyhat"
        elif item_name == "yellow phat":
            item_name = "Yellow partyhat"
        elif item_name == "white phat":
            item_name = "White partyhat"
        elif item_name == "purple phat":
            item_name = "Purple partyhat"
        elif item_name == "golden phat":
            item_name = "Golden partyhat"
        elif item_name == "fsoa":
            item_name = "Fractured Staff of Armadyl"
        elif item_name == "eof":
            item_name = "Essence of Finality amulet"
        elif item_name == "lotd":
            item_name = "Luck of the Dwarves"
        elif item_name == "bgs":
            item_name = "Bandos godsword"
        elif item_name == "ags":
            item_name = "Armadyl godsword"
        elif item_name == "sgs":
            item_name = "Saradomin godsword"
        elif item_name == "zammy gs":
            item_name = "Zamorak godsword"
        elif item_name == "botlg":
            item_name = "bow of the last gaurdian"
        elif item_name == "crown":
            item_name = "Crown of the First Necromancer"
        elif item_name == "foot wraps":
            item_name = "Foot wraps of the First Necromancer"
        elif item_name == "hand wraps":
            item_name = "Hand wrap of the First Necromancer"
        elif item_name == "robe bottom":
            item_name = "Robe bottom of the First Necromancer"
        elif item_name == "robe top":
            item_name = "Robe top of the First Necromancer"
        elif item_name == "omni":
            item_name = "Omni guard"
        elif item_name == "lantern":
            item_name = "Soulbound lantern"
        elif item_name == "ess":
            item_name = "Pure essence"
        elif item_name == "impure ess":
            item_name = "Impure essence"

        # use fuzzywuzzy to find the closest match to the item name
        for line in f:
            ratio = fuzz.token_set_ratio(line, item_name)
            if ratio >= 90:
                item_id = line.split()[0]
                matching_item_name = item_id
                break
            
        # If no matching items were found, send a message and return
        if not matching_item_name:
            await ctx.send(f"Sorry noob, I couldn't find an item with the name '{item_name}'.")
            return
           
    # Use the grand exchange API to get the current prices of the items
    prices = []
    for item_id in matching_item_name:
        api_url = f"http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item={matching_item_name}"
        r = requests.get(api_url)
        data = r.json()
        current_price = data["item"]["current"]["price"]
        prices.append(current_price)
    

        # Extract the item name, icon_large, description, and price information from the API response
        item_name = data["item"]["name"]
        icon_large = data["item"]["icon_large"]
        icon = data["item"]["icon"]
        description = data["item"]["description"]
        current_price = data["item"]["current"]["price"]
        day30 = data["item"]["day30"]["change"]
        day90 = data["item"]["day90"]["change"]
        day180 = data["item"]["day180"]["change"]
        today = data["item"]["today"]["price"]
        today_change = data["item"]["today"]["trend"]

        # list of colors to pick from
        colors = ["#10D6F3", "#67BDE4", "#B4A7D6", "#F48FB1", "#FF8A65", "#FFD54F", "#CDDC39", "#4CAF50", "#00BCD4", "#009688", "#FF5722", "#795548", "#607D8B", "#9E9E9E", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5", "#2196F3", "#03A9F4", "#00BCD4", "#009688", "#4CAF50", "#8BC34A", "#CDDC39", "#FFEB3B", "#FFC107", "#FF9800", "#FF5722", "#795548", "#9E9E9E", "#607D8B"]
        
        # pick a random color from the list
        random_color = random.choice(colors)

        # convert the hex color to an int
        color_int = int(random_color.lstrip('#'), 16)

        # Create a rich embed message
        embed = discord.Embed(title=" ", description=description, color=color_int)
        embed.set_thumbnail(url=icon_large)
        embed.set_author(name=item_name, icon_url=icon)
        embed.add_field(name="Current price", value=current_price + "\n", inline=True)
        embed.add_field(name="change", value=str(today) + "\n", inline=True)
        embed.add_field(name="Today", value=today_change + "\n", inline=True)
        embed.add_field(name="1 Month", value=day30 + "\n", inline=True)
        embed.add_field(name="3 Month", value=day90 + "\n", inline=True)
        embed.add_field(name="6 Month", value=day180, inline=True)
             
    # Send the rich embed message in the Discord channel
    await ctx.send(embed=embed)

scan_running = False
scan_paused = False

@bot.command()
async def scan(ctx):
    global scan_running, scan_paused
    
    if scan_running:
        await ctx.send("Scan is already running.")
        return
    
    scan_running = True
    
    item_names = []
    with open("scanList.txt", "r") as file:
        item_names = [line.strip() for line in file.readlines()]
    
    scan_embed = discord.Embed(title="Scanning...", description="Initializing scan...", color=discord.Color.blue())
    scan_message = await ctx.send(embed=scan_embed)
    
    no_profit_items = []
    
    for item_name in item_names:
        if scan_paused:
            await ctx.send("Scan paused. Use 'bob green light' to resume.")
            while scan_paused:
                await asyncio.sleep(1)
            await ctx.send("Scan resumed. Continuing...")
        
        flip_results = await ctx.invoke(bot.get_command("flip"), item_name)
        
        if flip_results is None:
            no_profit_items.append(item_name)
        
        if not scan_running:
            break
        
        await asyncio.sleep(4)  # 4-second delay between calls
    
        # Update the existing message with the latest item scanned
        scan_embed.description = f"Scanning {item_name}...\n\nNo profitable trading opportunities found."
        await scan_message.edit(embed=scan_embed)
    
    if len(no_profit_items) == len(item_names):
        scan_embed.description = "No profitable trading opportunities found for any item."
        await scan_message.edit(embed=scan_embed)
    else:
        scan_embed.description = "Scan completed."
        await scan_message.edit(embed=scan_embed)
    
    scan_running = False
    scan_paused = False

@bot.command()
async def noob(ctx, action: str):
    global scan_running, scan_paused
    
    if action == "no":
        scan_running = False
        scan_paused = False
        await ctx.send("Scan stopped.")
    elif action == "red light":
        scan_paused = True
        await ctx.send("Scan paused.")
    elif action == "green light":
        scan_paused = False
        await ctx.send("Scan resumed.")
    else:
        await ctx.send("Invalid action. Use 'noob no' to stop, 'noob red light' to pause, or 'noob green light' to resume.")

@bot.command()
async def flip(ctx, item_name: str):
    api_url = "https://api.shopdb.ecocitycraft.com/api/v3/chest-shops"
    
    try:
        current_page = 1
        profitable_trades = []
        while True:
            params = {
                "material": item_name,
                "hideUnavailable": "true",
                "page": current_page
            }
            response = requests.get(api_url, params=params)
            response_json = response.json()
            
            for buy_shop in response_json["results"]:
                if buy_shop["quantityAvailable"] > 0 and buy_shop["buySign"]:
                    buy_price_each = buy_shop["buyPriceEach"]
                    stock = buy_shop["quantityAvailable"]
                    
                    for sell_shop in response_json["results"]:
                        if sell_shop["quantityAvailable"] > 0 and sell_shop["sellSign"]:
                            sell_price_each = sell_shop["sellPriceEach"]
                            if sell_price_each > buy_price_each:
                                profit_margin = ((sell_price_each - buy_price_each) / buy_price_each) * 100
                                if profit_margin > 0:
                                    profit_per = (sell_price_each - buy_price_each)
                                    space = (3456 - sell_shop['quantityAvailable'])
                                    profitable_trades.append((buy_shop, sell_shop, profit_per, stock, space))
            
            current_page += 1
            if current_page > response_json["totalPages"]:
                break

    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while fetching data: {e}")
        return
    
    profitable_trades = sorted(profitable_trades, key=lambda trade: trade[2], reverse=True)
    
    if not profitable_trades and not scan_running:
        await ctx.send(f"No profitable trading opportunities found for {item_name}.")
        return
    
    for buy_shop, sell_shop, profit_per, stock, space in profitable_trades:
        item_name = buy_shop["material"]
        buy_server_name = buy_shop["server"]
        buy_town_name = buy_shop["town"]["name"]
        buy_coords = buy_shop["location"]
        buy_price_each = buy_shop["buyPriceEach"]
        sell_server_name = sell_shop["server"]
        sell_town_name = sell_shop["town"]["name"]
        sell_coords = sell_shop["location"]
        sell_price_each = sell_shop["sellPriceEach"]
        
        embed = discord.Embed(title=f"Profitable Flip Opportunity for {item_name}", color=discord.Color.green())
        item_image_url = get_item_image_url(item_name.lower())
        if item_image_url:
            embed.set_thumbnail(url=item_image_url)

        embed.add_field(name="Buy Shop", value=f"Server: {buy_server_name}\nTown: {buy_town_name}")
        profit_margin = ((sell_price_each - buy_price_each) / buy_price_each) * 100
        embed.add_field(name="Profit Margin", value=f"{profit_margin:.2f}%")
        embed.add_field(name="Sell Shop", value=f"Server: {sell_server_name}\nTown: {sell_town_name}")

        embed.add_field(name="Buy Price Each", value=f"${buy_price_each:.2f}")
        embed.add_field(name="Profit per", value =f"${profit_per:.2f}")
        embed.add_field(name="Sell Price Each", value=f"${sell_price_each:.2f}")
        embed.add_field(name="Stock", value=stock)
        profit = (profit_per * stock)
        formatted_profit = "{:.2f}".format(profit)
        embed.add_field(name="Profit", value=f"${formatted_profit}")
        embed.add_field(name="Can Buy", value=space)
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="\u200b", value="\u200b")
        
        coords_command_buy = f"/tpc {buy_coords['x']} {buy_coords['z']}"
        coords_command_sell = f"/tpc {sell_coords['x']} {sell_coords['z']}"
        warp_command_buy = f"/warp {buy_town_name}"
        warp_command_sell = f"/warp {sell_town_name}"
        embed.add_field(name="(Buy Shop)", value=f" Y: {buy_coords['y']}", inline=False)
        embed.add_field(name=f"{buy_town_name}", value=f"```\n{coords_command_buy}\n```", inline=False)
        embed.add_field(name=f"Warp", value=f"```{warp_command_buy}```", inline=False)
        embed.add_field(name="(Sell Shop)", value=f"Y: {sell_coords['y']}", inline=False)
        embed.add_field(name=f"{sell_town_name}", value=f"```\n{coords_command_sell}\n```", inline=False)
        embed.add_field(name=f"Warp", value=f"```{warp_command_sell}```", inline=False)
        await ctx.send(embed=embed)

@bot.command()
async def db(ctx, item_name: str, num_results: int = 1):
    
    api_url = "https://api.shopdb.ecocitycraft.com/api/v3/chest-shops"
    
    try:
        
        params = {
            "material": item_name,
            "hideUnavailable": "true"
        }
        response = requests.get(api_url, params=params)
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while fetching data: {e}")
        return
    
    # Filter shops with available stock
    available_shops = [shop for shop in response_json["results"] if shop["quantityAvailable"] > 0]
    
    if not available_shops:
        await ctx.send("No shops have available stock for that item.")
        return
    
    # Filter shops with "Buy Sign" equals "Yes" and "Sell Sign" equals "No"
    buy_only_shops = [shop for shop in available_shops if shop["buySign"] and not shop["sellSign"]]
    
    # Filter shops with "Sell Sign" equals "Yes" and "Buy Sign" equals "No"
    sell_only_shops = [shop for shop in available_shops if shop["sellSign"] and not shop["buySign"]]
    
    if buy_only_shops and not sell_only_shops:
        # Only buy offers available
        for shop in buy_only_shops[:num_results]:
            total_price = shop['buyPrice']
            price_per_count = shop['buyPriceEach']
            server_name = shop['server']

            if server_name == "main":
                embed_color = discord.Color.red()  # Red color for Main server
            elif server_name == "main-north":
                embed_color = discord.Color.blue()  # Blue color for MainNorth server
            else:
                embed_color = discord.Color.green()
            
            embed = discord.Embed(title=f"Best Price Shop for Buying {item_name}", color=embed_color)
            embed.add_field(name="Quantity Available", value=shop["quantityAvailable"])
            embed.add_field(name="Item", value=shop["material"])
            item_image_url = get_item_image_url(item_name.lower())
            if item_image_url:
                embed.set_thumbnail(url=item_image_url)
            embed.add_field(name="Buy Price", value=f"${total_price}")
            embed.add_field(name="Owner's Name", value=shop["owner"]["name"])
            embed.add_field(name="Town Name", value=shop["town"]["name"])
            embed.add_field(name="Price Each", value=f"${price_per_count:.2f}")
            embed.add_field(name="Buy Sign", value="Yes" if shop['buySign'] else "No")
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="Full", value="Yes" if shop['full'] else "No")
            
            coords = shop['location']
            coords_command = f"/tpc {coords['x']} {coords['z']}"
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="Coordinates", value=f"X: {coords['x']}, Y: {shop['location']['y']}, Z: {coords['z']}\n```\n{coords_command}\n```", inline=False)
            embed.add_field(name="Server", value=server_name)
            
            await ctx.send(embed=embed)
    elif sell_only_shops and not buy_only_shops:
        # Only sell offers available
        for shop in sell_only_shops[:num_results]:
            total_price = shop['sellPrice']
            price_per_count = shop['sellPriceEach']
            server_name = shop['server']
            if server_name == "main":
                embed_color = discord.Color.red()  # Red color for Main server
            elif server_name == "main-north":
                embed_color = discord.Color.blue()  # Blue color for MainNorth server
            else:
                embed_color = discord.Color.green()
            
            embed = discord.Embed(title=f"Best Price Shop for Selling {item_name}", color=embed_color)
            embed.add_field(name="Quantity Available", value=shop["quantityAvailable"])
            embed.add_field(name="Item", value=shop["material"])
            item_image_url = get_item_image_url(item_name)
            if item_image_url:
                embed.set_thumbnail(url=item_image_url)
            embed.add_field(name="Sell Price", value=f"${total_price}")
            embed.add_field(name="Owner's Name", value=shop["owner"]["name"])
            embed.add_field(name="Town Name", value=shop["town"]["name"])
            embed.add_field(name="Price Per Count", value=f"${price_per_count:.2f}")
            embed.add_field(name="Sell Sign", value="Yes" if shop['sellSign'] else "No")
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="Full", value="Yes" if shop['full'] else "No")
            
            coords = shop['location']
            coords_command = f"/tpc {coords['x']} {coords['z']}"
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="Coordinates", value=f"X: {coords['x']}, Y: {shop['location']['y']}, Z: {coords['z']}\n```\n{coords_command}\n```", inline=False)
            embed.add_field(name="Server", value=server_name)
            
            await ctx.send(embed=embed)
    else:
        # Both buy and sell offers available, run the command normally
        # Sort available shops by buy price
        sorted_shops = sorted(available_shops, key=lambda shop: shop["buyPriceEach"])
        
        # Take the first num_results shops (best prices)
        best_price_shops = sorted_shops[:num_results]
        
        for shop in best_price_shops:
            total_price = shop['buyPrice']
            price_per_count = shop['buyPriceEach']
            server_name = shop['server']

            if server_name == "main":
                embed_color = discord.Color.red()  # Red color for Main server
            elif server_name == "main-north":
                embed_color = discord.Color.blue()  # Blue color for MainNorth server
            else:
                embed_color = discord.Color.green()
        
            
            embed = discord.Embed(title=f"Best Price Shop for {item_name}", color=embed_color)
            embed.add_field(name="Quantity Available", value=shop["quantityAvailable"])
            embed.add_field(name="Item", value=shop["material"])
            item_image_url = get_item_image_url(item_name.lower())
            if item_image_url:
                embed.set_thumbnail(url=item_image_url)
            embed.add_field(name="Buy Price", value=f"${total_price}")
            embed.add_field(name="Price Per Count", value=f"${price_per_count:.2f}")
            embed.add_field(name="Owner's Name", value=shop["owner"]["name"])
            embed.add_field(name="Town Name", value=shop["town"]["name"])
            embed.add_field(name="Sell Price", value=f"${shop['sellPrice']}")
            embed.add_field(name="Sell Price Each", value=f"${shop['sellPriceEach']}")
            embed.add_field(name="Buy Sign", value="Yes" if shop['buySign'] else "No")
            embed.add_field(name="Sell Sign", value="Yes" if shop['sellSign'] else "No")
            embed.add_field(name="Full", value="Yes" if shop['full'] else "No")
            
            coords = shop['location']
            coords_command = f"/tpc {coords['x']} {coords['z']}"
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="Coordinates", value=f"X: {coords['x']}, Y: {shop['location']['y']}, Z: {coords['z']}\n```\n{coords_command}\n```", inline=False)
            embed.add_field(name="Server", value=server_name)
            
            await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, item_name: str, num_results: int = 1):
    api_url = "https://api.shopdb.ecocitycraft.com/api/v3/chest-shops"
    
    # Check for known abbreviations and synonyms
    if item_name == "nstar":
        item_name = "nether star"
    elif item_name == "diamondm1pick":
        item_name = "diamonpickaxe#9h"
    elif item_name == "diamond m2 pick":
        item_name = "diamonpickaxe#ju"
    elif item_name == "diamond m3 pick":
        item_name = "diamonpickaxe#9h"
    elif item_name == "netherite m1 pick":
        item_name = "netheripickax#9h"
    elif item_name == "netherite m2 pick":
        item_name = "netheripickax#jv"
    elif item_name == "netherite m3 pick":
        item_name = "netheripickax#jw"
    elif item_name == "raffle ticket":
        item_name = "paper#9x"
    elif item_name == "raffle":
        item_name = "paper#9x"
    elif item_name == "redstone dust":
        item_name = "redstone"
    
    try:
        params = {
            "material": item_name,
            "hideUnavailable": "true"
        }
        response = requests.get(api_url, params=params)
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while fetching data: {e}")
        return
    
    # Load the item names from the JSON response
    item_names = [shop["material"] for shop in response_json["results"]]
    
    # Use fuzzywuzzy to find the closest match to the item name
    best_match = max(item_names, key=lambda name: fuzz.token_set_ratio(name, item_name))
    
    try:
        params = {
            "material": best_match,  # Use the best matched item name
            "hideUnavailable": "true"
        }
        response = requests.get(api_url, params=params)
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while fetching data: {e}")
        return
    
    # Filter shops with available stock and "Buy Sign" equals "Yes"
    available_buy_shops = [shop for shop in response_json["results"] if shop["quantityAvailable"] > 0 and shop["buySign"]]
    
    if not available_buy_shops:
        # Check if there are sell offers
        available_sell_shops = [shop for shop in response_json["results"] if shop["quantityAvailable"] > 0 and shop["sellSign"]]
        if available_sell_shops:
            await ctx.send(f"No buy offers available for {item_name}, but you can use `sell {item_name}` instead.")
        else:
            await ctx.send("No shops available for buying that item.")
        return
    
    # Sort available shops by buy price
    sorted_shops = sorted(available_buy_shops, key=lambda shop: shop["buyPriceEach"])
    
    # Take the first num_results shops (best prices)
    best_price_buy_shops = sorted_shops[:num_results]
    
    for shop in best_price_buy_shops:
        total_price = shop['buyPrice']
        price_per_count = shop['buyPriceEach']
        server_name = shop['server']
        if server_name == "main":
            embed_color = discord.Color.red()  # Red color for Main server
        elif server_name == "main-north":
            embed_color = discord.Color.blue()  # Blue color for MainNorth server
        else:
            embed_color = discord.Color.green()
    
        
        embed = discord.Embed(title=f"Best Price Shop for Buying {item_name}", color=embed_color)
        embed.add_field(name="Seller", value=shop["owner"]["name"])
        embed.add_field(name="Item", value=shop["material"])
        embed.add_field(name="Stock", value=shop["quantityAvailable"])
        item_image_url = get_item_image_url(item_name)
        if item_image_url:
            embed.set_thumbnail(url=item_image_url)
        total_cost = shop['buyPriceEach'] * shop['quantityAvailable']
        formatted_total_cost = "${:,.2f}".format(total_cost)
        embed.add_field(name="Price Each", value=f"${price_per_count:.2f}")
        embed.add_field(name="Buy Price", value=f"${total_price}")
        embed.add_field(name="Total", value=formatted_total_cost)
        embed.add_field(name="Server", value=server_name)
        embed.add_field(name="Sell Sign", value="Yes" if shop['sellSign'] else "No")
        embed.add_field(name="Full", value="Yes" if shop['full'] else "No")
        
        coords = shop['location']
        coords_command = f"/tpc {coords['x']} {coords['z']}"
        warp_command = f"/warp {shop['town']['name']}"
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=f"{shop['town']['name']}", value=f" Y: {shop['location']['y']}\n```\n{coords_command}\n```", inline=False)
        embed.add_field(name=f"Warp", value=f"```{warp_command}```", inline=False)
        
        await ctx.send(embed=embed)

@bot.command()
async def sell(ctx, item_name: str, num_results: int = 1):
    
    api_url = "https://api.shopdb.ecocitycraft.com/api/v3/chest-shops"
    
    # Check for known abbreviations and synonyms
    if item_name == "nstar":
        item_name = "nether star"
    elif item_name == "diamondm1pick":
        item_name = "diamonpickaxe#9h"
    elif item_name == "diamond m2 pick":
        item_name = "diamonpickaxe#ju"
    elif item_name == "diamond m3 pick":
        item_name = "diamonpickaxe#9h"
    elif item_name == "netherite m1 pick":
        item_name = "netheripickax#9h"
    elif item_name == "netherite m2 pick":
        item_name = "netheripickax#jv"
    elif item_name == "netherite m3 pick":
        item_name = "netheripickax#jw"
    elif item_name == "raffle ticket":
        item_name = "paper#9x"
    elif item_name == "raffle":
        item_name = "paper#9x"
    
    try:
        # Construct the API URL with the necessary query parameters
        params = {
            "material": item_name,
            "hideUnavailable": "true"
        }
        response = requests.get(api_url, params=params)
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while fetching data: {e}")
        return
    
    # Filter shops with available stock and "Sell Sign" equals "Yes"
    available_sell_shops = [shop for shop in response_json["results"] if shop["quantityAvailable"] > 0 and shop["sellSign"]]
    
    if not available_sell_shops:
        # Check if there are buy offers
        available_buy_shops = [shop for shop in response_json["results"] if shop["quantityAvailable"] > 0 and shop["buySign"]]
        if available_buy_shops:
            await ctx.send(f"No sell offers available for {item_name}, but you can use `buy {item_name}` instead.")
        else:
            await ctx.send("No shops available for selling that item.")
        return
    
    # Sort available shops by sell price per count (highest to lowest)
    sorted_shops = sorted(available_sell_shops, key=lambda shop: shop["sellPriceEach"], reverse=True)
    
    # Take the first num_results shops (best prices)
    best_price_sell_shops = sorted_shops[:num_results]
    
    for shop in best_price_sell_shops:
        total_price = shop['sellPrice']
        price_per_count = shop['sellPriceEach']
        server_name = shop['server']
        if server_name == "main":
            embed_color = discord.Color.red()  # Red color for Main server
        elif server_name == "main-north":
            embed_color = discord.Color.blue()  # Blue color for MainNorth server
        else:
            embed_color = discord.Color.green()
        
        space = 3456 - shop['quantityAvailable']
        embed = discord.Embed(title=f"Best Price Shop for Selling {item_name}", color=embed_color)
        embed.add_field(name="Buyer", value=shop["owner"]["name"])
        embed.add_field(name="Item", value=shop["material"])
        embed.add_field(name="Can Buy", value=space)
        item_image_url = get_item_image_url(item_name)
        if item_image_url:
            embed.set_thumbnail(url=item_image_url)
        total_gain = price_per_count * space  
        formatted_total_gain = "${:,.2f}".format(total_gain)
        rounded_price_per_count = round(price_per_count, 2)
        embed.add_field(name="Price Each", value=f"${rounded_price_per_count:.2f}")
        embed.add_field(name="Sell Price", value=f"${total_price:.2f}")
        embed.add_field(name="Total", value=formatted_total_gain)
        embed.add_field(name="Server", value=server_name)
        embed.add_field(name="Buy Sign", value="Yes" if shop['buySign'] else "No")
        embed.add_field(name="Full", value="Yes" if shop['full'] else "No")
        
        coords = shop['location']
        coords_command = f"/tpc {coords['x']} {coords['z']}"
        warp_command = f"/warp {shop['town']['name']}"
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=shop['town']['name'], value=f"Y: {shop['location']['y']}\n```\n{coords_command}\n```", inline=False)
        embed.add_field(name="Warp", value=f"```{warp_command}```", inline=False)
        await ctx.send(embed=embed)

# command to delete x amount of messages
@bot.command()
@commands.has_any_role("ADMIN", "DEV", "Owner")
async def clear(ctx, amount=5 + 1):
    await ctx.channel.purge(limit=amount + 1)

# command to kick a user
@bot.command()
@commands.check(is_allowed)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)

# command to ban a user
@bot.command()
@commands.check(is_allowed)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member.mention}")

# command to unban a user
@bot.command()
@commands.check(is_allowed)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {user.mention}")
            return

# command to mute a user
@bot.command()
@commands.check(is_allowed)
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(role)
    await ctx.send(f"Muted {member.mention}")

# command to unmute a user
@bot.command()
@commands.check(is_allowed)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(role)
    await ctx.send(f"Unmuted {member.mention}")

# command to add a role to a user
@bot.command()
async def addrole(ctx, *, role_name):
    member = ctx.author  # The member who invoked the command

    # Check if the role is in the list of allowed roles
    allowed_roles = ['Runescape', 'CS:GO', 'Rust', 'GTA', 'Minecraft', 'Apex', 'GIM', 'laser league', 'WoW', 'Valheim']  # Example allowed roles

    if role_name in allowed_roles:
        role = discord.utils.get(ctx.guild.roles, name=role_name)  # Get the role object
        await member.add_roles(role)
        await ctx.send(f"Added {role.mention} to {member.mention} Noob")
    else:
        allowed_roles_list = ', '.join(allowed_roles)
        await ctx.send(f"The role you are trying to assign is not available Noob. You can assign the following roles: {allowed_roles_list}")

# command to remove a role from a user
@bot.command()
async def removerole(ctx, role: discord.Role):
    member = ctx.author  # The member who invoked the command

    # Check if the role is in the list of allowed roles
    allowed_roles = ["Runescape", "CS:GO", "Rust", "GTA", "Minecraft", "Apex", "GIM", "laser league", "WoW", 'Valheim']  # Example allowed roles

    if role.name in allowed_roles:
        await member.remove_roles(role)
        await ctx.send(f"Removed {role.mention} from {member.mention}")
    else:
        await ctx.send(f"You are not allowed to remove that role. You can remove the following roles: {allowed_roles}")

# command to create a role
@bot.command()
@commands.has_any_role("ADMIN", "DEV", "Owner")
async def createrole(ctx, role_name):
    guild = ctx.guild
    await guild.create_role(name=role_name)
    await ctx.send(f"Created role {role_name}")

# command to delete a role
@bot.command()
@commands.has_any_role("ADMIN", "DEV", "Owner")
async def deleterole(ctx, role_name):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    await role.delete()
    await ctx.send(f"Deleted role {role_name}")

# command to create a channel
@bot.command()
@commands.has_any_role("ADMIN", "DEV", "Owner")
async def createchannel(ctx, channel_name):
    guild = ctx.guild
    await guild.create_text_channel(channel_name)
    await ctx.send(f"Created channel {channel_name}")

# command to delete a channel
@bot.command()
@commands.has_any_role("ADMIN", "DEV", "Owner")
async def deletechannel(ctx, channel_name):
    guild = ctx.guild
    channel = discord.utils.get(guild.channels, name=channel_name)
    await channel.delete()
    await ctx.send(f"Deleted channel {channel_name}")

# command to send a message to a channel
@bot.command()
async def send(ctx, channel_name, *, message):
    guild = ctx.guild
    channel = discord.utils.get(guild.channels, name=channel_name)
    await channel.send(message)
    await ctx.send(f"Sent message to {channel_name}")

# command to send a message to a user
@bot.command()
async def dm(ctx, user_name, *, message):
    guild = ctx.guild
    user = discord.utils.get(guild.members, name=user_name)
    await user.send(message)
    await ctx.send(f"Sent message to {user_name}")

# command to search rs3 wiki
@bot.command()
async def wiki(ctx, *, search):
    search = search.replace(" ", "_")
    await ctx.send(f"https://runescape.wiki/w/{search}")

# Global list to store the queue
queue = []

@bot.command()
async def play(ctx, *, query):
    # Check if the bot is already in a voice channel
    if ctx.voice_client is not None:
        # The bot is already in a voice channel
        vc = ctx.voice_client
    else:
        # Join the voice channel
        voice_channel = ctx.author.voice.channel
        if voice_channel is not None:
            vc = await voice_channel.connect()
        else:
            await ctx.send('You are not in a voice channel noob.')
            return

    # Search YouTube for the query
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f'ytsearch1:{query}', download=False)
        url = info['entries'][0]['url']

    # Create an AudioSource object from the YouTube URL
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url))

    # Check if the bot is already playing a song
    if vc.is_playing():
        # The bot is already playing a song, add the song to the queue
        queue.append(source)
        await ctx.send(f'Added {query} to the queue Noob.')
    else:
        # Play the song
        vc.play(source)
        await ctx.send(f'Playing {query} Noob.')
    
    # Check if the queue is not empty
    while queue:
        # Wait for the current song to end
        while vc.is_playing():
            await asyncio.sleep(1)
        # Get the next song in the queue
        next_song = queue.pop(0)
        # Play the next song
        vc.play(next_song)
        await ctx.send(f'Playing {next_song.title} Noob.')

# command to stop music
@bot.command()
async def stop(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("I am not in a voice channel Noob.")

# command to pause music
@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed pause")
        await ctx.send("Music not playing failed pause")

# command to resume music
@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")

@bot.command()
async def own(ctx, member : discord.Member):
    trash_talk = ["I own everyone.","I own you.","You're a noob at everything!","Noob","N00B","n0OOo0b","You couldn't beat me at arm wrestling with both hands tied behind your back!","You couldn't beat me at a game of tag if You were tied to a tree!","You couldn't beat me at a game of Red Light Green Light if I were standing right in front of you!","You're such a noob, you couldn't defeat a baby goblin!","You're so bad at Runescape, you couldn't even beat a chicken in a duel!","You're so terrible at Runescape, you couldn't even catch a mackerel with a net!"]
    # Pick a random trash talk from the list and send it as a message
    message = random.choice(trash_talk)
    await ctx.send(message)

if __name__ == '__main__':
    import threading
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8089})
    flask_thread.start()
    
    bot.run("")
