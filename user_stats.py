
import lang_id
import os
import pickle

if not os.path.exists('db/user/'):
    os.makedirs('db/user/')

class UserStats(object):

  def __init__(self, id):
    self.id = id
    self.words_in_lang = {}
    self.lang_code = None
    self.language = None

def load_user(id):
  idf = f'db/user/{id}'
  if os.path.isfile(idf):
    with open(idf, 'rb') as f:
      return pickle.load(f)
  return UserStats(id)

def save_user(id, user):
  idf = f'db/user/{id}'
  with open(idf, 'wb') as f:
    pickle.dump(user, f)

def get_words_in_lang(id):
  return load_user(id).words_in_lang

def add_words_in_lang(id, my_words):
  user = load_user(id)
  for k, v in my_words.items():
    user.words_in_lang[k] = user.words_in_lang.get(k, 0) + v
  save_user(id, user)

def set_language(id, my_lang):
  my_code = lang_id.lang2code(my_lang)
  if my_code:
    user = load_user(id)
    user.lang_code = my_code
    user.language = my_lang
    save_user(id, user)
  else:
    raise ValueError(f'Could not find {my_lang}')

def get_language(id):
  user = load_user(id)
  return user.lang_code, user.language
