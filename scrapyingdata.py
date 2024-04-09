# -*- coding: utf-8 -*-
"""scrapyingdata.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xl5QtC1QobWtC4Z7h-a9EjoUMwr4t99l
"""

!pip install discord

import requests
from bs4 import BeautifulSoup
import discord
import re

# Define the Home Depot URL
HOME_DEPOT_URL = "https://www.homedepot.com"

# Discord bot token (replace 'YOUR_DISCORD_TOKEN' with your actual token)
DISCORD_TOKEN = 'f62313437db7e1c38cce4ce379bc79e3e57324bbb7f25b5195db2550bc18ddea'

# Discord channel IDs for each discount range
DISCORD_CHANNELS = {
    '90-100%': 'channel_id_90_100',
    '80-89%': 'channel_id_80_89',
    '70-79%': 'channel_id_70_79',
    '1-69%': 'channel_id_1_69',
    'BOGO': 'channel_id_bogo',
    'Multi-Buy Deals': 'channel_id_multi_buy'
}

def get_page_content(url):
    """
    Fetches the HTML content of a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None

def scrape_and_send_deals(client):
    """
    Scrapes deals from Home Depot and sends to Discord channels based on discount or deal ranges.
    """
    categories = [
        ('Deal of the Day', f"{HOME_DEPOT_URL}/c/deal-of-the-day"),
        ('Online Clearance', f"{HOME_DEPOT_URL}/c/clearance"),
        ('BOGO', f"{HOME_DEPOT_URL}/b/BOGO/N-5yc1vZ1z0vm5f"),
        ('Multi-Buy Deals', "MULTI_BUY_DEALS_URL")
    ]

    for category, url in categories:
        content = get_page_content(url)
        if content:
            soup = BeautifulSoup(content, "html.parser")
            deal_items = soup.find_all("div", class_="product-pod--ie-fix")
            for item in deal_items:
                product_name = item.find("div", class_="pod-plp__description").text.strip()
                price = item.find("span", class_="price").text.strip()
                discount_range = classify_discount(price)
                send_to_discord(client, product_name, price, discount_range)
            print(f"{category} scraped successfully!")
        else:
            print(f"Error fetching {category} content.")


def classify_discount(price):
    """
    Classifies the discount range based on the product price.
    """
    # Extract the numeric part of the price using regular expressions
    numeric_price = re.search(r'\d+\.\d+', price)
    if numeric_price:
        price_value = float(numeric_price.group())
        # Determine the discount range based on the price value
        if price_value >= 90:
            return '90-100%'
        elif 80 <= price_value < 90:
            return '80-89%'
        elif 70 <= price_value < 80:
            return '70-79%'
        elif 1 <= price_value < 70:
            return '1-69%'
        else:
            return 'BOGO'  # For simplicity, assuming products with negative prices or zero price are BOGO
    else:
        return '1-69%'  # If unable to extract numeric price, assume 1-69% discount

def send_to_discord(client, product_name, price, discount_range):
    """
    Sends product information to Discord channels based on discount or deal ranges.
    """
    channel_id = DISCORD_CHANNELS.get(discount_range, 'default_channel_id')
    channel = client.get_channel(channel_id)
    if channel:
        message = f"Product: {product_name}, Price: {price}"
        client.send(channel, message)
    else:
        print("Invalid channel ID.")

# Define your intents
intents = discord.Intents.default()

# Initialize Discord client with intents
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Scrape and send data to Discord channels
    scrape_and_send_deals(client)

# Run the Discord bot
# Run the Discord bot
client.run(DISCORD_TOKEN)