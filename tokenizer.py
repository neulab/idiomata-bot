# Reversible tokenizer from here:
# https://sjmielke.com/papers/tokenize/

import re
import sys
import unicodedata

class SimpleTokenizer(object):

  def __init__(self):
    pass

  def tokenize(self, instring):
    return instring.split()


class MielkeTokenizer(object):

  def __init__(self):
    pass
    self.MERGESYMBOL = ''

  def is_weird(c):
    return not (unicodedata.category(c)[0] in 'LNM' or c.isspace())
    # return not (c.isalnum() or c.isspace())

  def check_for_at(self, instring):
    for match in re.finditer(' ' + self.MERGESYMBOL, instring):
      if match.end() < len(instring) and self.is_weird(instring[match.end()]):
        print("CAUTION: looks like a merge to the detokenizer:", instring[match.start():match.end()+1], " at position", match.start(), file = sys.stderr)
    for match in re.finditer(self.MERGESYMBOL + ' ', instring):
      if match.start() > 0 and self.is_weird(instring[match.start()-1]):
        print("CAUTION: looks like a merge to the detokenizer:", instring[match.start()-1:match.end()], " at position", match.start()-1, file = sys.stderr)

  def tokenize(self, instring):
    # Fix the Kawakami error?
    # instring = instring.replace('\\n\\n', '\n\n')

    # remove non-breaking spaces
    instring = instring.replace(u'\u200d', '')

    # Walk through the string!
    outsequence = []
    for i in range(len(instring)):
      c = instring[i]
      c_p = instring[i-1] if i > 0 else c
      c_n = instring[i+1] if i < len(instring) - 1 else c

      # Is it a letter (i.e. Unicode category starts with 'L')?
      # Or alternatively, is it just whitespace?
      # So if it's not weird, just copy.
      if not self.is_weird(c):
        outsequence.append(c)
      # Otherwise it should be separated!
      else:
        # Was there something non-spacey before?
        # Then we have to introduce a new space and a merge marker.
        if not c_p.isspace():
          outsequence.append(' ' + self.MERGESYMBOL)
        # Copy character itself
        outsequence.append(c)
        # Is there something non-spacey after?
        # Then we have to introduce a new space and a merge marker.
        # If, however the next character would just want to merge left anyway, no need to do it now.
      if not c_n.isspace() and not self.is_weird(c_n):
        outsequence.append(self.MERGESYMBOL + ' ')

    return ''.join(outsequence).split()

if __name__ == "__main__":
  tok = MielkeTokenizer()
  for line in sys.stdin:
    instring = line.strip()
    tok_string = ' '.join(tok.tokenize(instring))
    print(tok_string)
 

