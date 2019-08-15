# IdiomataBot

This is a Telegram bot for supporting conversations.

## Instructions for Running the Bot

Install requirementes:

    pip install -r requirements.txt

Create a bot according to the [Telegram Bot Instructions](https://core.telegram.org/bots)
Add the token to a file named "token.txt".

Download data for some common languages:

    bash download_data.sh

Run the bot:

    python bot.py


# Instructions for Using the Bot

[Message IdiomataBot](https://t.me/IdiomataBot)
(or whatever other bot name you're using the software with).
Alternatively, add IdiomataBot to a conversation between two people, click on
its name, and then select "promote to administrator" so it can follow along
with the conversation.

Note that this means that the bot will be able to read your conversation. It
does not save any logs, and only keeps track of how many words you spoke in each
language for now.
