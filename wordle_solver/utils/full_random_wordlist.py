import itertools
import string

def generate_wordlist(filename):
    letters = string.ascii_lowercase
    with open(filename, 'w') as f:
        for combo in itertools.product(letters, repeat=5):
            word = ''.join(combo)
            f.write(word + '\n')

if __name__ == "__main__":
    generate_wordlist('utils/all_5_letter_words.txt')