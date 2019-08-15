'''
    This class measures the distance between 2 words in 1 language
'''
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

    def match_string(self, input_str, threshold):
        '''
            Compare input_str with words in the dictionary
        '''
        suggested_words = []
        for word in self.words:
            edit_distance_score = self.min_edit_distance(word, input_str)
            if edit_distance_score <= threshold:
                suggested_words.append((word, edit_distance_score))

        return suggested_words

def main():
    words = ["hello", "hi", "English", "halo"]
    input_str = "hallo"
    string_matcher = StringMatcher(words)

    threshold = 2
    corrected_words = string_matcher.match_string(input_str, threshold)
    print(corrected_words)

    
if __name__ == '__main__':
    main()