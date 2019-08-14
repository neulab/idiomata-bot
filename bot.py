#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import logging
import telegram
import re
import sys
import user_stats
import mielke_tokenizer as tok
import lang_id
from telegram.error import NetworkError, Unauthorized
from time import sleep
from collections import defaultdict

update_id = None

lang_ider = lang_id.WordCountBasedLanguageID()
translation_dicts = {}
partial_dicts = {}
for lang in ('cay',):
  my_dict = {}
  my_partial = defaultdict(lambda: [])
  with open(f'data/translation_dicts/{lang}.txt', 'r') as f:
    for line in f:
      line = line.strip()
      cols = line.split('\t')
      if len(cols) == 2:
        left, right = cols
        my_dict[left] = right
        my_dict[right] = left
        for word in left.split() + right.split():
          my_partial[word].append(line)
      else:
        print(f'bad line in translation dictionary {line}', file=sys.stderr)
  translation_dicts[lang] = my_dict
  partial_dicts[lang] = my_partial




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
        # ---------- my score
        if '@IdiomataBot my score' in text:
          words_in_lang = user_stats.get_words_in_lang(user.id)
          my_sum = float(sum(words_in_lang.values()))
          my_cnts = [(cnt/my_sum, word) for (word, cnt) in words_in_lang.items() if cnt/my_sum > 0.01]
          my_cnts.sort(reverse=True)
          words_in_lang_string = ', '.join([f'{cnt*100:.1f}% in {lang}' for (cnt, lang) in my_cnts])
          update.message.reply_text(f'{user.first_name} has written {words_in_lang_string}')
        # ---------- my language
        elif '@IdiomataBot my language' in text:
          m = re.search('@IdiomataBot my language (.*)', text)
          if not m:
            update.message.reply_text('Write "@IdiomataBot my language" followed by the language you want to use, e.g. "@IdiomataBot my language French"')
          else:
            my_lang = m.group(1)
            try:
              user_stats.set_language(user.id, my_lang)
              update.message.reply_text(f'Your language was set to {my_lang}')
            except:
              update.message.reply_text(f'Sorry, I could not find the language {my_lang}')
        # ---------- translate
        elif '@IdiomataBot translate' in text:
          m = re.search('@IdiomataBot translate (.*)', text)
          lang_code, language = user_stats.get_language(user.id)
          if not m:
            update.message.reply_text('Write "@IdiomataBot translate" followed by the word you want to translate')
          elif lang_code is None:
            update.message.reply_text('Before you can translate, you need to specify your language.'+
                                      ' Please write "@IdiomataBot my language", followed by the language you want to use.')
          elif lang_code not in translation_dicts:
            update.message.reply_text('Sorry, I don\'t have a dictionary for {language}')
          else:
            word = m.group(1)
            if word in translation_dicts[lang_code]:
              trans = translation_dicts[lang_code][word]
              update.message.reply_text(trans)
            elif word in partial_dicts[lang_code]:
              mess = '\n'.join(['Found several possible translations:'] + partial_dicts[lang_code][word][:5])
              update.message.reply_text(mess)
            else:
              update.message.reply_text('Sorry, I don\'t have a dictionary entry in {language} or English for {word}')
        # ---------- (unknown command)
        else:
          update.message.reply_text('Sorry, I couldn\'t recognize that command. You can write '+
                                    '"@IdiomataBot my score", "@IdiomataBot my language [Language]", "@IdiomataBot translate [word]')

      # Parse normal messages
      else:
        tokenized_message = tok.tokenize(str(text)).split()
        word_langs = lang_ider.id_words(tokenized_message, id_type='name')
        words_in_lang = defaultdict(lambda: 0)
        for word_lang in word_langs:
          words_in_lang[word_lang] += 1
        user_stats.add_words_in_lang(user.id, words_in_lang)

if __name__ == '__main__':
  main()
