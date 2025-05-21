import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
from models.board import Board
import time

class WordleGame:
    def __init__(self):
        self.browser = None
        self.page = None
        self.board = Board()
        self.game_state = 'ready'

    def start(self):
        """
        Starts the Wordle game by launching a browser navigating to the game page and getting a ready to play status.
        """
        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self.page.goto("https://wordleunlimited.org/")
        try:
            self.page.add_style_tag(content="""
                .instructions { display: none !important; }
            """)
            self.page.mouse.click(400, 400)
            time.sleep(0.3)
            self.game_state = 'running'
        except Exception as e:
            print(f"Error clicking off the overlay: {e}")

    def read_board(self):
        """
        Reads only the latest row from the board on the webpage and adds it to the Board object.
        """
        board_div = self.page.query_selector("div#board")
        if board_div:
            rows = board_div.query_selector_all("div.row")
            # Only process the next unprocessed row
            next_row_index = len(self.board.rows)
            if next_row_index < len(rows):
                row = rows[next_row_index]
                game_tiles = row.query_selector_all("game-tile")
                row_data = []
                col_index = 0
                for tile in game_tiles:
                    letter = tile.get_attribute("letter")
                    state = tile.get_attribute("evaluation")
                    if letter and state:
                        row_data.append({"row_index": next_row_index, "col_index": col_index, "letter": letter, "state": state})
                        col_index += 1
                if row_data:
                    self.board.add_row(row_data)
        
    def type_word(self, word: str, delay_time: float = 1.8):
        """
        Types the specified word into the Wordle game and submits it.

        Args:
            word (str): The word to type into the game.
            delay_time (float): The time to wait after typing the word before proceeding.
        """
        try:
            self.page.keyboard.type(word)
            self.page.keyboard.press("Enter")
        except Exception as e:
            print(f"Error typing word '{word}': {e}")
        time.sleep(delay_time)
        for _ in range(5):
            self.page.keyboard.press("Backspace")

    def restart(self):
        """
        Restarts the game by refreshing the page and scrolls to the top.
        """
        self.board = Board()
        self.page.evaluate("""
            let overlay = document.querySelector('.fc-dialog-overlay');
            if (overlay) overlay.remove();
            let consentRoot = document.querySelector('.fc-consent-root');
            if (consentRoot) consentRoot.remove();
        """)
        self.page.click("button#refresh-button")
        self.game_state = 'running'

    def update_game_state(self):
        """
        Updates the game state based on the board and page.
        """
        self.read_board()
        # Check for win: any row where all states are 'correct'
        for row in self.board.rows:
            if all(tile.state == "correct" for tile in row):
                self.game_state = "win"
                return

        # Check for lose: max rows filled and no win
        if len(self.board.rows) >= self.board.max_rows:
            self.game_state = "lost"
            return

        # Otherwise, game is in progress
        self.game_state = "running"

    def close(self):
        if self.browser:
            self.browser.close()