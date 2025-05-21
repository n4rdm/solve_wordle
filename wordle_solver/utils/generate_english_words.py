import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import string
from nltk.corpus import words

def generate_wordlist(filename):
    english_words = set(w.lower() for w in words.words() if len(w) == 5 and w.isalpha())
    with open(filename, 'w') as f:
        for word in sorted(english_words):
            f.write(word + '\n')

if __name__ == "__main__":
    import nltk
    nltk.download('words')
    generate_wordlist('wordle_solver/utils/all_en_5_letter_words.txt')