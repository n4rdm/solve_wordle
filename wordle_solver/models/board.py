from models.tile import Tile
from uuid import uuid4

class Board:
    def __init__(self):
        self.rows = []
        self.current_row = 0 
        self.max_rows = 6 # Later make this dynamic based on the amount of tries allowed
        self.max_cols = 5 # Later make this dynamic based on the word length
        self.uuid = uuid4()

    def add_row(self, row_data):
        """
        Adds a new row to the board.
        :param row_data: List of Tile objects representing the row.
        """
        row = [Tile(tile["row_index"], tile["letter"], tile["state"]) for tile in row_data]
        self.rows.append(row)

    def display(self):
        """
        Displays the current state of the board.
        """
        print(f"Board {self.uuid} Current State:")
        for row in self.rows:
            print(f"Row {row[0].row_index}:")
            print(' '.join(f"{tile.letter}({tile.state})" for tile in row))
        print("\n")
        
        
