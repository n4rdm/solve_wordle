"""
First solver for Wordle.
Uses simple logic to filter the word list based on the current board state.
Simply removes words who would not be valid guesses based on the current board state.
"""

import random
import os
import sys
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress_bar import ProgressBar
from rich.panel import Panel
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser.wordle_game import WordleGame
import math

class algoSolverV1:
    def __init__(self, word_list_path, headless=True):
        self.word_list_path = word_list_path
        self.word_list = self.load_word_list()
        self.word_list_length = len(self.word_list)
        self.headless = headless
        self.game = WordleGame(headless=self.headless)
        self.absent = []
        self.present = {}
        self.correct = {}
        self.win_rate = None


    def load_word_list(self):
        """
        Loads the word list from the specified file.
        :return: List of words.
        """
        with open(self.word_list_path, 'r') as file:
            words = [line.strip().upper() for line in file.readlines()]
        return words

    def update_letters(self, game: WordleGame):
        if len(game.board.rows) > 0:
            last_row = game.board.rows[-1]
            for tile in last_row:
                if tile.state == 'present':
                    self.present[tile.letter] = tile.col_index
                elif tile.state == 'correct':
                    self.correct[tile.letter] = tile.col_index
                elif tile.state == 'absent' and tile.letter not in self.present and tile.letter not in self.correct:
                    self.absent.append(tile.letter)
        else:
            pass
    

    def make_guess(self, game: WordleGame, win_conf = 0):
        """
        Makes a guess in the Wordle game based on the current board state.
        :param game: The WordleGame object.
        """
        # The 3 first guesses are preset:
        preset_guesses = ['SLATE', 'BRICK', 'JUMPY', 'VOZHD', 'FUNGI', 'WRECK']
        # preset_guesses = ['JUMPY', 'VEXIL', 'CHORD', 'BANGS', 'TWERK']
        # preset_guesses = ['JUMPY', 'VEXIL', 'CHORD', 'BANGS']
        # preset_guesses = ['HATES', 'ROUND', 'CLIMB']
        # preset_guesses = ['FRAUD', 'MELON', 'SIGHT']
        # preset_guesses = ['CONES', 'TRIAL']
        # preset_guesses = ['TALES']
        # preset_guesses = []
        global guess
        if len(game.board.rows) < len(preset_guesses) and win_conf < 100:
            guess = preset_guesses[len(game.board.rows)]
        else:
            guess = random.choice(self.word_list)
        console.print(Align.center(Panel(f"Guessing: {guess}", expand=False)))
        if guess in self.word_list:
            self.word_list.remove(guess)
        game.type_word(guess)
        

    def solve(self, game: WordleGame):
        """
        Solves the Wordle game by making guesses based on the current board state.
        """
        # Get the current board state
        iteration = 0
        removed_words = []
        while game.game_state == 'running':
            # At the start of each guess do the following:
            self.update_letters(game)
            self.filter_word_list()
            win_conf = display_solver_state(game.board, game.game_state, self.word_list, self.word_list_length, removed_words, self.win_rate)
            
            if self.word_list:
                self.make_guess(game, win_conf=win_conf)
            else:
                console.print(Align.center(Panel("No valid words found. Forcing a loss.")))
                game.type_word('FORCE')
            
            # After each guess, read the board and update the game state.
            game.read_board()
            game.update_game_state()

            # Check if the word went through or not
            if game.game_state == 'running':
                iteration += 1
                if len(game.board.rows) < iteration:
                    self.remove_from_word_list(guess.lower())
                    removed_words.append(guess.lower())
                    iteration -= 1
            
        if game.game_state == 'win':
            display_solver_state(game.board, game.game_state, self.word_list, self.word_list_length, removed_words, self.win_rate)
        
        elif game.game_state == 'lost':
            display_solver_state(game.board, game.game_state, self.word_list, self.word_list_length, removed_words, self.win_rate)
            # If the game is lost, retrieve the correct word from the game.
            toast = game.page.query_selector("game-toast")
            if toast:
                correct_word = toast.get_attribute("text")
                self.add_to_word_list(correct_word.lower())
            else:
                correct_word = None


    def filter_word_list(self):
        """
        Filters the word list based on the current board state.
        :return: List of valid words.
        """
        # Remove all words that contain letters in the 'absent' list
        # Do not remove the letters that are in the 'present' or 'correct' dictionaries
        for letter in set(self.absent):
            if letter not in self.correct and letter not in self.present:
                self.word_list = [word for word in self.word_list if letter not in word]

        # Remove all words that do not contain letters in the 'present' dictionary
        for letter, col_index in self.present.items():
            self.word_list = [word for word in self.word_list if letter in word and word[col_index] != letter]

        # Remove all words that do not contain letters in the 'correct' dictionary
        for letter, col_index in self.correct.items():
            self.word_list = [word for word in self.word_list if word[col_index] == letter]


    def add_to_word_list(self, word):
        """
        Improves the word list file by adding words that are valid guesses if they arent already there.
        """
        with open(self.word_list_path, 'r') as file:
            lines = file.readlines()
            if word + '\n' not in lines:
                with open(self.word_list_path, 'a') as file:
                    file.write(word + '\n')
                    console.print(Align.center(Panel(f"Added {word} to the word list.")))
            else:
                console.print(Align.center(Panel(f"{word} is already in the word list.")))
        
        
    def remove_from_word_list(self, word):
        """
        Improves the word list file by removing words that are not valid guesses.
        """
        with open(self.word_list_path, 'r') as file:
            lines = file.readlines()
        with open(self.word_list_path, 'w') as file:
            for line in lines:
                if line.strip() != word:
                    file.write(line)
        console.print(Align.center(Panel(f"Removed {word} from the word list.")))


    def restart_game(self, game: WordleGame):
        """
        Restarts the game.
        """
        game.page.wait_for_selector("div#statistics", timeout=5000)
        stat_elements = game.page.query_selector_all("div.container div#statistics div.statistic-container div.statistic")
        if stat_elements and len(stat_elements) > 1:
            self.win_rate = stat_elements[1].inner_text()
        else:
            print("Could not find win rate statistic.")
        self.absent = []
        self.present = {}
        self.correct = {}
        self.word_list = self.load_word_list()
        game.restart()
        game.page.add_style_tag(content="""
                .instructions { display: none !important; }
            """)
        

    def start(self):
        """
        Starts the solver and interacts with the Wordle game.
        """
        self.game.start()
        while True:
            self.solve(self.game)
            self.restart_game(self.game)


def display_solver_state(board, game_state, word_list, word_list_length, removed_words, win_rate):
    global console
    console = Console()
    console.clear()
    table = display_board_rich(board)
    guesses_left = board.max_rows - len(board.rows)
    win_conf = get_win_confidence(word_list, word_list_length, guesses_left)
    state_str = display_game_state(game_state)

    # Display game state and winrate side by side
    panels = [Panel(state_str, expand=True)]
    if win_rate:
        win_rate_val = win_rate.split(" ")[0]
        # Dynamically color winrate: red (low) to green (high)
        try:
            win_rate_num = float(win_rate_val)
        except ValueError:
            win_rate_num = 0
        # Calculate color: 0 = red, 100 = green
        red = int(255 * (1 - win_rate_num / 100))
        green = int(180 * (win_rate_num / 100) + 75)  # keep green visible at low winrate
        color_hex = f"#{red:02x}{green:02x}00"
        panels.append(Panel(f"[bold {color_hex}]Winrate: {win_rate_val}%[/]", expand=True))
    if len(panels) == 2:
        panel_table = Table.grid(expand=False)
        panel_table.add_row(*panels)
        console.print(Align.center(panel_table))
    else:
        console.print(Align.center(panels[0]))
    console.print(Align.center(f"Win Confidence with {len(word_list)} words left and {guesses_left} guesses left:"))
    bar_table = Table.grid(padding=(0, 1))
    bar_table.add_row(
        ProgressBar(total=100, completed=win_conf, width=50),
        f"[bold]{win_conf:.0f}%[/bold]"
    )
    console.print(Align.center(bar_table))
    console.print(Align.center(table))
    if removed_words:
        console.print(Align.center(Panel(f"Removed words: {', '.join(removed_words)}", expand=False)))

    return win_conf

def display_board_rich(board):
    table = Table(show_header=False, box=None, expand=False, padding=(0,1))
    color_map = {
        "correct": "bold white on green3",
        "present": "bold white on yellow3",
        "absent": "white on grey23"
    }
    for row in board.rows:
        row_cells = []
        for tile in row:
            style = color_map.get(tile.state, "white")
            row_cells.append(f"[{style}] {tile.letter} [/]")
        table.add_row(*row_cells)
    return table

def get_win_confidence(word_list, word_list_length, guesses_left):
    words_left = max(len(word_list), 1)
    if words_left == 1:
        return 100.0
    if guesses_left < words_left:
        # Estimate win confidence based on the probability of guessing the correct word in the remaining guesses
        prob = 1 - ((words_left - 1) / words_left) ** guesses_left
        return round(prob * 100, 2)
    return 100.0

def display_game_state(game_state):
    state_colors = {
        "running": "bold green",
        "win": "bold green3",
        "lost": "bold red"
    }
    state_str = f"[{state_colors.get(game_state, 'white')}] Game State: {game_state.upper()} [/]"
    return state_str

if __name__ == "__main__":
    
    word_list_path = "wordle_solver/utils/self_creating_list.txt"
    # word_list_path = "wordle_solver/utils/all_en_5_letter_words.txt"
    # word_list_path = "wordle_solver/utils/all_5_letter_words.txt"
    # word_list_path = "wordle_solver/utils/wordle_allowed_guesses.txt"
    # word_list_path = "wordle_solver/utils/wordle_unlimited_solutionlist.txt"
    while True:
        try:
            solver = algoSolverV1(word_list_path, headless=True)
            solver.start()
        except Exception as e:
            if "Target page, context or browser has been closed" in str(e):
                sys.exit("You closed the game window. Exiting with no game restart...")
            print(f"Error: {e}")
            if solver.game.browser:
                solver.game.close()
            print("Restarting the game...")