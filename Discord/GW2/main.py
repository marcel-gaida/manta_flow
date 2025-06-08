# main.py

from bot import Bot

if __name__ == "__main__":
    # Create an instance of the bot
    bot = Bot()

    # Check that the token was loaded from your .env file
    if not bot.TOKEN:
        print("Error: DISCORD_TOKEN not found in .env file.")
        print("Please create a .env file and add your token to it.")
    else:
        # Start the bot
        print("Starting GW2 Wiki Bot...")
        bot.run(bot.TOKEN)