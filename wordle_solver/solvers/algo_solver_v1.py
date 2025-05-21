import random
import os
import sys
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn
from rich.progress_bar import ProgressBar
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from math import log

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser.wordle_game import WordleGame

class algoSolverV1:
    def __init__(self, word_list_path):
        self.word_list_path = word_list_path
        self.word_list = self.load_word_list()
        self.word_list_length = len(self.word_list)
        self.absent = []
        self.present = {}
        self.correct = {}


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
    

    def make_guess(self, game: WordleGame):
        """
        Makes a guess in the Wordle game based on the current board state.
        :param game: The WordleGame object.
        """    
        guess = random.choice(self.word_list)
        self.word_list.remove(guess)
        game.type_word(guess)
        

    def solve(self, game: WordleGame):
        """
        Solves the Wordle game by making guesses based on the current board state.
        """
        # Get the current board state
        while game.game_state == 'running':
            display_solver_state(game.board, game.game_state, self.word_list, self.word_list_length)
            # At the start of each guess do the following:
            self.update_letters(game)
            self.filter_word_list()
            
            if self.word_list:
                self.make_guess(game)
            else:
                print("No valid words found. Forcing a loss.")
                game.type_word('FORCE')
            
            # After each guess, read the board and update the game state.
            game.read_board()
            game.update_game_state()

        if game.game_state == 'win':
            display_solver_state(game.board, game.game_state, self.word_list, self.word_list_length)
        elif game.game_state == 'lost':
            display_solver_state(game.board, game.game_state, self.word_list, self.word_list_length)


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


    def restart_game(self, game: WordleGame):
        """
        Restarts the game by refreshing the page.
        """
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
        game = WordleGame()
        game.start()
        while True:
            self.solve(game)
            self.restart_game(game)


def display_solver_state(board, game_state, word_list, word_list_length):
    console = Console()
    console.clear()
    table = display_board_rich(board)
    guesses_left = board.max_rows - len(board.rows)
    win_conf = get_win_confidence(word_list, word_list_length, guesses_left)
    state_str = display_game_state(game_state)

    console.print(Align.center(Panel(state_str, expand=False)))
    console.print(Align.center(f"Win Confidence with {len(word_list)+1} words left and {guesses_left} guesses left:"))
    bar_table = Table.grid(padding=(0, 1))
    bar_table.add_row(
        ProgressBar(total=100, completed=win_conf, width=60),
        f"[bold]{win_conf:.0f}%[/bold]"
    )
    console.print(Align.center(bar_table))
    console.print(Align.center(table))

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
    words_left = max(len(word_list)+1, 1)
    if words_left == 1:
        return 100.0
    if guesses_left < words_left:
        return round(guesses_left / words_left * 100, 2)
    return 100.0

def display_game_state(game_state):
    state_colors = {
        "running": "bold cyan",
        "win": "bold green",
        "lost": "bold red"
    }
    state_str = f"[{state_colors.get(game_state, 'white')}] Game State: {game_state.upper()} [/]"
    return state_str

if __name__ == "__main__":
    word_list_path = "wordle_solver/utils/wordle-allowed-guesses.txt"
    solver = algoSolverV1(word_list_path)
    solver.start()