GW2 Wiki Discord Bot
A helpful Discord bot that provides detailed information about Guild Wars 2 items by scraping the official Guild Wars 2 Wiki and other community resources.

Demo
Here is an example of the bot looking up the "Mystic Coin" item:

User: @GW2_Item_Lookup Mystic Coin

GW2_Item_Lookup:

Mystic Coin
Mystic Coin is a crafting material used in crafting of the legendary equipment and in various Mystic Forge recipes, both directly and through its related crafting material Mystic Clover.

Crafting Calculator on GW2Efficiency

Rarity

Type

Req. Level

Rare

Trophy

N/A

Sell Price
1g 93s 97c

Buy Price
1g 82s 13c

Features
Detailed Item Information: Fetches item rarity, type, required level, and description.

Trading Post Prices: Scrapes live buy and sell order prices from GW2TP.

Recipe Display: Shows the crafting recipe for an item if one is available on the wiki.

GW2Efficiency Integration: Provides a direct link to an item's crafting calculator page on gw2efficiency.com.

Smart Search: Automatically handles wiki disambiguation pages (e.g., a search for "Bifrost" correctly finds "The Bifrost").

Flexible Usage: Responds to direct messages or @mentions in a server channel.

Setup & Installation
Follow these steps to get your own instance of the bot running.

1. Prerequisites
Python 3.9+

A Discord Bot Application

2. Clone the Repository
Clone this project to your local machine:

git clone <your-repository-url>
cd <your-repository-directory>

3. Install Dependencies
It's recommended to use a virtual environment.

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required libraries
pip install -r requirements.txt

Note: If you don't have a requirements.txt file, you can create one with the necessary libraries:

discord.py
requests
beautifulsoup4
python-dotenv

Then run pip install -r requirements.txt.

4. Configure Your Bot Token
Create a new file in the main project directory named .env.

Open the .env file and add your Discord bot token in the following format:

DISCORD_TOKEN="YourSecretBotTokenGoesHere"

5. Configure Discord Permissions
For the bot to read messages, you must enable the Message Content Intent on the Discord Developer Portal.

Go to the Discord Developer Portal.

Select your application.

Navigate to the Bot tab.

Scroll down to Privileged Gateway Intents.

Turn on the MESSAGE CONTENT INTENT toggle.

Click "Save Changes".

6. Run the Bot
Once everything is configured, you can start the bot by running the main.py script:

python main.py

Usage
In a Server: Mention the bot followed by an item name.

@GW2_Item_Lookup The Bifrost

In a Direct Message: Simply send the item name to the bot.

Mjölnir

Project Structure
.
├── .env                  # Stores secret tokens (not committed to Git)
├── .gitignore            # Specifies files for Git to ignore
├── bot.py                # Main bot class with all scraping and Discord logic
├── main.py               # Entry point to run the bot
├── README.md             # This file
├── requirements.txt      # List of Python dependencies
└── responses.py          # Stores predefined string responses for the bot

Technologies Used
discord.py: A modern, easy-to-use, feature-rich, and async-ready API wrapper for Discord.

Requests: A simple, yet elegant, HTTP library.

Beautiful Soup: A Python library for pulling data out of HTML and XML files.

python-dotenv: Reads key-value pairs from a .env file and can set them as environment variables.

License
This project is licensed under the MIT License. See the LICENSE file for details.
