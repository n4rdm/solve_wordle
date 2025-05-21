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

    def start(self):
        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self.page.goto("https://wordleunlimited.org/")
        
        try:
            self.page.mouse.click(400, 400)
        except Exception as e:
            print(f"Error injecting CSS: {e}")

    def read_board(self):
        board_div = self.page.query_selector("div#board")
        
        if board_div:
            row_index = 0
            rows = board_div.query_selector_all("div.row")
            for row in rows:
                row_index += 1
                row_data = []
                game_tile = row.query_selector_all("game-tile")
                for tile in game_tile:
                    letter = tile.get_attribute("letter")
                    state = tile.get_attribute("evaluation")
                    if letter and state:
                        row_data.append({"row_index": row_index, "letter": letter, "state": state})
                if row_data:
                    self.board.add_row(row_data)
        

    def type_word(self, word: str):
        self.page.keyboard.type(word)
        self.page.keyboard.press("Enter")
        time.sleep(1.8)

    def close(self):
        if self.browser:
            self.browser.close()

game = WordleGame()
game.start()
game.type_word("CRANE")
game.read_board()
game.board.display()
game.type_word("HELLO")
game.read_board()
game.board.display()
# game.close()