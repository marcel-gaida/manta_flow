# bot.py

import discord
import requests
from bs4 import BeautifulSoup
import os
import re  # Import the regular expressions module
from dotenv import load_dotenv
from responses import responses

load_dotenv()


class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.wiki_url = "https://wiki.guildwars2.com/wiki/"
        self.TOKEN = os.getenv('DISCORD_TOKEN')

    async def on_ready(self):
        print(f"Logged in as {self.user.name} ({self.user.id})")
        print("Bot is ready to receive commands.")

    async def on_message(self, message):
        if message.author == self.user:
            return
        should_respond = False
        if message.guild:
            if self.user in message.mentions:
                should_respond = True
        else:
            should_respond = True
        if not should_respond:
            return

        item_name = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()
        if not item_name:
            await message.channel.send(responses["item_not_provided"])
            return

        item_url = self.wiki_url + item_name.replace(" ", "_").title()

        try:
            response = requests.get(item_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching URL {item_url}: {e}")
            await message.channel.send(responses["wiki_connection_failed"])
            return

        if "There is currently no text in this page." in response.text:
            await message.channel.send(responses["item_not_found_on_wiki"].format(item_name=item_name))
            return

        soup = BeautifulSoup(response.content, "html.parser")

        disambig_div = soup.select_one("div.disambig, #disambigbox")
        if disambig_div:
            print(f"Disambiguation page found for '{item_name}'. Trying to find the primary link.")
            first_link = soup.select_one("#mw-content-text .mw-parser-output > ul > li > a")
            if first_link and first_link.has_attr('href'):
                new_url = "https://wiki.guildwars2.com" + first_link['href']
                print(f"Following link to: {new_url}")
                try:
                    response = requests.get(new_url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")
                    item_url = new_url
                except requests.RequestException as e:
                    print(f"Error fetching disambiguation link {new_url}: {e}")
                    await message.channel.send(responses["wiki_connection_failed"])
                    return
            else:
                await message.channel.send(
                    f"I found a disambiguation page for `{item_name}`, but couldn't determine the correct item page.")
                return

        item_data, recipe_data = self.extract_item_data(soup, item_url, item_name)

        if not item_data:
            await message.channel.send(responses["infobox_not_found"].format(item_name=item_name))
            return

        embed = self.create_item_embed(item_data, recipe_data)
        await message.channel.send(embed=embed)

    def extract_item_data(self, soup, item_url, item_name):
        infobox = soup.select_one("div.infobox")
        if not infobox:
            return None, None

        item_data = {"wiki_url": item_url}
        recipe_data = {}

        def get_field(field_name):
            try:
                return infobox.find("dt",
                                    string=lambda t: t and t.strip().lower() == field_name.lower()).find_next_sibling(
                    "dd").text.strip()
            except AttributeError:
                return None

        item_data['name'] = infobox.select_one(".heading").text.strip() if infobox.select_one(".heading") else item_name

        try:
            icon_tag = infobox.select_one(".infobox-icon img")
            if icon_tag and icon_tag.has_attr('src'):
                item_data["icon_url"] = f"https://wiki.guildwars2.com{icon_tag['src']}"
        except AttributeError:
            pass

        try:
            description_paragraph = soup.select_one("#mw-content-text .mw-parser-output > p")
            description_text = description_paragraph.text.strip()
            unwanted_suffix = "— In-game description"
            item_data["description"] = description_text.removesuffix(unwanted_suffix).strip()
        except AttributeError:
            item_data["description"] = "No description available."

        rarity_text = get_field("Rarity")
        if rarity_text and len(rarity_text) > 1:
            item_data['rarity'] = rarity_text[1:]
        else:
            item_data['rarity'] = rarity_text

        item_data['type'] = get_field("Item type") or get_field("Type")
        item_data['req_level'] = get_field("Req. level")
        item_data['binding'] = get_field("Binding")

        if infobox and infobox.has_attr('data-id'):
            item_data['api_id'] = infobox['data-id']
        else:
            try:
                api_link = soup.find('a', href=re.compile(r'api\.guildwars2\.com/v2/items\?ids='))
                item_id_str = api_link['href'].split('ids=')[1].split('&')[0]
                item_data['api_id'] = item_id_str
            except AttributeError:
                print(f"No API ID found for {item_name}")

        if item_data.get('api_id'):
            print(f"Found API ID: {item_data['api_id']}")

        try:
            gw2tp_link = soup.find("a", string="GW2TP")
            if gw2tp_link:
                tp_url = gw2tp_link['href']
                tp_response = requests.get(tp_url, timeout=10)
                tp_soup = BeautifulSoup(tp_response.content, "html.parser")
                buy_price_raw = tp_soup.select_one("#buy-price").get('data-price', 0)
                sell_price_raw = tp_soup.select_one("#sell-price").get('data-price', 0)

                def format_price(price_in_copper):
                    price = int(price_in_copper)
                    if price == 0: return None
                    gold, silver = divmod(price, 10000)
                    silver, copper = divmod(silver, 100)
                    parts = []
                    if gold > 0: parts.append(f"{gold}g")
                    if silver > 0: parts.append(f"{silver}s")
                    if copper > 0 or not parts: parts.append(f"{copper}c")
                    return " ".join(parts)

                item_data['buy_price'] = format_price(buy_price_raw)
                item_data['sell_price'] = format_price(sell_price_raw)
        except Exception as e:
            print(f"Could not fetch trading post prices: {e}")

        recipe_box = soup.find('div', {'class': 'recipe-box'})
        if recipe_box:
            try:
                recipe_data["output_qty"] = recipe_box.find('dt', string='Output qty.').find_next_sibling(
                    'dd').text.strip()
                ingredients_section = recipe_box.find('div', {'class': 'ingredients'})
                if ingredients_section:
                    ingredients = ingredients_section.find_all('dd')
                    recipe_data["ingredients_list"] = [
                        f"{ing.find_previous_sibling('dt').text.strip()} {ing.text.strip()}" for ing in ingredients]
            except AttributeError:
                pass

        return item_data, recipe_data

    def create_item_embed(self, item_data, recipe_data):
        description_text = item_data.get('description') or "No description available."
        if item_data.get('api_id'):
            #
            # --- FIX: Appending "!e~0" to the URL as requested ---
            #
            gw2eff_url = f"https://gw2efficiency.com/crafting/calculator/a~0!b~1!c~0!d~1-{item_data['api_id']}!e~0"
            description_text += f"\n\n[Crafting Calculator on GW2Efficiency]({gw2eff_url})"

        embed = discord.Embed(
            title=item_data.get('name', "Unknown Item"),
            url=item_data.get('wiki_url'),
            description=description_text,
            color=0x00ff00
        )

        if item_data.get('icon_url'):
            embed.set_thumbnail(url=item_data['icon_url'])

        if item_data.get('rarity'):
            embed.add_field(name="Rarity", value=item_data['rarity'], inline=True)
        if item_data.get('type'):
            embed.add_field(name="Type", value=item_data['type'], inline=True)
        if item_data.get('req_level'):
            embed.add_field(name="Req. Level", value=item_data.get('req_level'), inline=True)

        if item_data.get('sell_price'):
            embed.add_field(name="Sell Price", value=item_data['sell_price'], inline=False)
        if item_data.get('buy_price'):
            embed.add_field(name="Buy Price", value=item_data['buy_price'], inline=True)

        if recipe_data.get("ingredients_list"):
            ingredients_value = "\n".join(recipe_data["ingredients_list"])
            embed.add_field(
                name=f"Recipe (Output: {recipe_data.get('output_qty', '1')})",
                value=ingredients_value,
                inline=False
            )

        embed.set_footer(text="Data from the official Guild Wars 2 Wiki. Prices from GW2TP.")
        return embed