#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import logging
import telegram
import mielke_tokenizer as tok
import lang_id
from telegram.error import NetworkError, Unauthorized
from time import sleep
from collections import defaultdict


update_id = None
user_stats = defaultdict(lambda: UserStats())

lang_ider = lang_id.WordCountBasedLanguageID()

class UserStats():

  def __init__(self):
    self.words_written = 0
    self.words_in_lang = defaultdict(lambda: 0)


def main():
  """Run the bot."""
  global update_id
  # Telegram Bot Authorization Token
  with open('token.txt', 'r') as f:
    token = f.readline().strip()
  bot = telegram.Bot(token)

  # get the first pending update_id, this is so we can skip over it in case
  # we get an "Unauthorized" exception.
  try:
    update_id = bot.get_updates()[0].update_id
  except IndexError:
    update_id = None

  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  while True:
    try:
      echo(bot)
    except NetworkError:
      sleep(1)
    except Unauthorized:
      # The user has removed or blocked the bot.
      update_id += 1

def echo(bot):
  """Echo the message the user sent."""
  global update_id
  # Request updates after the last update_id
  for update in bot.get_updates(offset=update_id, timeout=10):
    update_id = update.update_id + 1

    if update.message:  # your bot can receive updates without messages
      # Reply to the message
      user = update.effective_user
      text = update.message.text
      entities = update.message.parse_entities()
      # Parse mentions
      if '@IdiomataBot' in entities.values():
        if 'my score' in text:
          my_sum = float(sum(user_stats[user.id].words_in_lang.values()))
          my_cnts = [(cnt/my_sum, word) for (word, cnt) in user_stats[user.id].words_in_lang.items() if cnt/my_sum > 0.01]
          my_cnts.sort(reverse=True)
          words_in_lang_string = ', '.join([f'{cnt*100:.1f}% words in {lang}' for (cnt, lang) in my_cnts])
          update.message.reply_text(f'{user.first_name} has written {words_in_lang_string}')
      # Parse normal messages
      else:
        tokenized_message = tok.tokenize(str(text)).split()
        user_stats[user.id].words_written += len(tokenized_message)
        words = user_stats[user.id].words_written
        word_langs = lang_ider.id_words(tokenized_message, id_type='name')
        print(tokenized_message)
        print(word_langs)
        for word_lang in word_langs:
          user_stats[user.id].words_in_lang[word_lang] += 1

if __name__ == '__main__':
  main()
