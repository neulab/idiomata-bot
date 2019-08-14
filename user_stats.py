
import lang_id
from collections import defaultdict

class UserStats():

  def __init__(self):
    self.words_written = 0
    self.words_in_lang = defaultdict(lambda: 0)
    self.lang_code = None
    self.language = None

all_user_stats = defaultdict(lambda: UserStats())

def get_words_in_lang(id):
  return all_user_stats[id].words_in_lang

def add_words_in_lang(id, my_words):
  for k, v in my_words.items():
    all_user_stats[id].words_in_lang[k] += v

def set_language(id, my_lang):
  my_code = lang_id.lang2code(my_lang)
  if my_code:
    all_user_stats[id].lang_code = my_code
    all_user_stats[id].language = my_lang
  else:
    raise ValueError(f'Could not find {my_lang}')

def get_language(id):
  return all_user_stats[id].lang_code, all_user_stats[id].language