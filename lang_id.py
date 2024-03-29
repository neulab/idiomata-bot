import numpy as np
import iso639
from collections import defaultdict

all_langs = ('cay', 'dan', 'deu', 'eng', 'fra', 'kwk', 'see', 'swe')

codelang = [('cay', 'Cayuga'), ('see', 'Seneca'), ('other', 'Other')]
code2lang_dict = {c:l for (c,l) in codelang}
lang2code_dict = {l:c for (c,l) in codelang}

def code2lang(code):
  if code in code2lang_dict:
    return code2lang_dict[code]
  elif code in iso639.languages.terminology:
    return iso639.languages.terminology[code].inverted
  else:
    return None

def lang2code(lang):
  if lang in lang2code_dict:
    return lang2code_dict[lang]
  elif lang in iso639.languages.inverted:
    return iso639.languages.inverted[lang].terminology
  else:
    return None

class LanguageID(object):

  def __init__(self, langs=all_langs):
    """
    Create a language identifier for the specified languages.

    Args:
      langs: The ISO-639 lexographic language codes for each language.
             Defaults to all_langs.
    """
    self.langs = langs
    raise NotImplementedError('Need to implement in a subclass')

  def predict_word(word):
    """
    Calculate the log probability of a word belonging to a particular language specified in `langs`. If `langs` is not specified, it will use `all_langs`.

    Args:
      word: A single word string

    Returns:
      A numpy array with the log probability of each language
    """
    raise NotImplementedError('Need to implement in a subclass')

  def predict_words(self, words):
    """
    Calculate the log probability of words in a sentence belonging to a particular language specified in `langs`. If `langs` is not specified, it will use `all_langs`.

    Args:
      words: A tokenized list of word strings
      langs: A list of three-letter language codes

    Returns:
      A numpy array with the log probability of each word (rows) for each language or other (columns)
    """
    ret = np.zeros( (len(words), len(self.langs)+1) )
    for i, word in enumerate(words):
      ret[i] = self.predict_word(word)
    return ret

  def id_words(self, words, id_type='pos'):
    ret = list(np.argmax(self.predict_words(words), axis=1))
    if id_type == 'pos': return ret
    ret = ['other' if pos == len(self.langs) else self.langs[pos] for pos in ret]
    if id_type == 'code': return ret
    ret = [code2lang(code) for code in ret]
    return ret


class WordCountBasedLanguageID(LanguageID):

  def __init__(self, langs=all_langs, other_alpha=1.0e-9, lang_alpha=1.0e-10):
    self.langs = langs
    self.other_alpha = other_alpha
    self.lang_alpha = lang_alpha
    self.counts = [self.load_counts(lang) for lang in langs]

  def load_counts(self, lang):
    counts = {}
    with open(f'data/word_counts/{lang}.txt', 'r') as f:
      for line in f:
        word, count = line.strip().split()
        counts[word.lower()] = int(count)
    my_sum = float(sum(counts.values()))
    counts = {word: count/my_sum for (word, count) in counts.items()}
    return counts

  def predict_word(self, word):
    my_counts = np.zeros(len(self.langs)+1)
    my_counts[len(self.langs)] = self.other_alpha
    for i, counts in enumerate(self.counts):
      my_counts[i] = counts.get(word.lower(), self.lang_alpha)
    return np.log(my_counts/np.sum(my_counts))

class WordClassifierLanguageID(LanguageID):

  def __init__(self, langs=all_langs, alpha=0.5, ns=(3,4,5), other_bias=1):
    self.langs = langs
    self.alpha = alpha
    self.other_bias = other_bias
    self.ns = ns
    self.ngram_probs = defaultdict(lambda: np.zeros(len(langs)+1) + alpha)
    for i, lang in enumerate(langs):
      with open(f'data/word_counts/{lang}.txt', 'r') as f:
        for line in f:
          word, count = line.strip().split()
          for ngram in self.get_ngrams(word):
            self.ngram_probs[ngram][i] += 1
    for k, v in self.ngram_probs.items():
      self.ngram_probs[k] = np.log(v/np.sum(v))

  def predict_word(self, word):
    my_counts = np.zeros(len(self.langs)+1)
    my_counts[len(self.langs)] = self.other_bias
    for ngram in self.get_ngrams(word):
      if ngram in self.ngram_probs:
        my_counts += self.ngram_probs[ngram]
    my_counts -= np.max(my_counts)
    my_counts -= np.log(np.sum(np.exp(my_counts)))
    print(my_counts)
    return my_counts

  def get_ngrams(self, word):
    word = word.lower()
    for n in self.ns:
      for i in range(len(word)-n+1):
        yield word[i:i+n]

if __name__ == "__main__":
  my_lid = WordClassifierLanguageID()
  words = 'Danke , Bonjour'.split()
  print(' '.join([str(x) for x in my_lid.id_words(words, id_type='name')]))
