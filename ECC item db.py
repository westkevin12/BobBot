import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import random
import asyncio
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import json
import os
import re





#set intents
intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.presences = True
intents.typing = True
intents.voice_states = True
intents.webhooks = True

#initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="prices"))

# Check if the user has any of the allowed roles
def is_allowed(ctx):
    allowed_roles = ["ADMIN", "DEV", "Owner"]
    return any(role.name in allowed_roles for role in ctx.author.roles)

with open('items_with_images.json', 'r') as json_file:
    items_with_images = json.load(json_file)

def get_item_image_url(item_name):
    best_match, _ = process.extractOne(item_name, items_with_images.keys())
    
    return items_with_images.get(best_match)
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
                                    profitable_trades.append((buy_shop, sell_shop, profit_per))
            
            current_page += 1
            if current_page > response_json["totalPages"]:
                break

    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while fetching data: {e}")
        return
    
    profitable_trades = sorted(profitable_trades, key=lambda trade: trade[2], reverse=True)
    
    if not profitable_trades:
        await ctx.send(f"No profitable trading opportunities found for {item_name}.")
        return
    
    
    
    for buy_shop, sell_shop, profit_per in profitable_trades:
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
        profit_per = (sell_price_each - buy_price_each)
        embed.add_field(name="Profit per", value =f"${profit_per:.2f}")
        embed.add_field(name="Sell Price Each", value=f"${sell_price_each:.2f}")
        embed.add_field(name="Stock", value=stock)
        profit = (profit_per * stock)
        formatted_profit = "{:.2f}".format(profit)
        embed.add_field(name="Profit", value=f"${formatted_profit}")
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="\u200b", value="\u200b")
        
        
        
        coords_command_buy = f"/tpc {buy_coords['x']} {buy_coords['z']}"
        coords_command_sell = f"/tpc {sell_coords['x']} {sell_coords['z']}"
        embed.add_field(name="Coordinates (Buy Shop)", value=f"X: {buy_coords['x']}, Y: {buy_coords['y']}, Z: {buy_coords['z']}", inline=False)
        embed.add_field(name="Copy Command (Buy Shop)", value=f"```\n{coords_command_buy}\n```", inline=False)
        embed.add_field(name="Coordinates (Sell Shop)", value=f"X: {sell_coords['x']}, Y: {sell_coords['y']}, Z: {sell_coords['z']}", inline=False)
        embed.add_field(name="Copy Command (Sell Shop)", value=f"```\n{coords_command_sell}\n```", inline=False)
    
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
        embed.add_field(name="Total", value=formatted_total_cost)
        embed.add_field(name="Buy Price", value=f"${total_price}")
        embed.add_field(name="Price Each", value=f"${price_per_count:.2f}")
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
    
        
        embed = discord.Embed(title=f"Best Price Shop for Selling {item_name}", color=embed_color)
        embed.add_field(name="Buyer", value=shop["owner"]["name"])
        embed.add_field(name="Item", value=shop["material"])
        embed.add_field(name="Can Buy", value=shop["quantityAvailable"])
        item_image_url = get_item_image_url(item_name)
        if item_image_url:
            embed.set_thumbnail(url=item_image_url)
        space = 3456 - shop['quantityAvailable']
        total_gain = shop['sellPriceEach'] * space
        formatted_total_gain = "${:,.2f}".format(total_gain)
        embed.add_field(name="Total", value=formatted_total_gain)
        embed.add_field(name="Sell Price", value=f"${total_price:.2f}")
        embed.add_field(name="Price Each", value=f"${price_per_count:.2f}")
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





# command to create a role
@bot.command()
@commands.has_any_role("SERVERADMIN", "GAMEADMIN", "OWNER")
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






bot.run("")