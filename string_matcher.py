import random
import sys
'''
    This class measures the distance between 2 words in 1 language
'''
random.seed(23)
class StringMatcher():

    def __init__(self, words):
        '''
            A list of words from the dictionary
        '''
        self.words = words

    def min_edit_distance(self, s1, s2):
        #code from rosettacode
        if len(s1) > len(s2):
            s1,s2 = s2,s1
        distances = range(len(s1) + 1)
        for index2,char2 in enumerate(s2):
            new_distances = [index2+1]
            for index1,char1 in enumerate(s1):
                if char1 == char2:
                    new_distances.append(distances[index1])
                else:
                    new_distances.append(1 + min((distances[index1],
                                                 distances[index1+1],
                                                 new_distances[-1])))
            distances = new_distances

        return distances[-1]

    def match_string_with_threshold(self, input_str, threshold=2):
        '''
            Compare input_str with words in the dictionary
        '''
        
        suggested_words = {}
        for word, definition in self.words.items():
            edit_distance_score = self.min_edit_distance(word, input_str)
            if edit_distance_score <= threshold:
                suggested_words[word] = edit_distance_score
        top_similar_words = self.rank_word(suggested_words)

        the_new_list = []
        for word, score in top_similar_words:
            the_new_list.append((word, self.words[word]))

        return the_new_list

    def rank_word(self, suggested_words, limit_word = 5):
        sorted_words = sorted(suggested_words.items(), key=lambda x: x[1])
        #to be added: rank words based on phonetic similarity etc
        return sorted_words[:5]

def main():
    my_dict = {}
    with open(f'../data/translation_dicts/cay.txt', 'r') as f:
        for line in f:
          line = line.strip()
          cols = line.split('\t')
          if len(cols) == 2:
            left, right = cols
            my_dict[left] = right
            my_dict[right] = left
          else:
            print(f'bad line in translation dictionary {line}', file=sys.stderr)
          str_matcher = StringMatcher(my_dict)

    input_str = 'aha'
    corrected_words = str_matcher.match_string_with_threshold(input_str)
    print(corrected_words)

    
if __name__ == '__main__':
    main()