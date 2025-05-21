class Tile:
    """
    Represents a tile in the Wordle game.
    Each tile has a letter and a status indicating its correctness.
    """
    def __init__(self, row_index: int, col_index: int, letter: str, state: str):
        self.row_index = row_index
        self.col_index = col_index
        self.letter = letter.upper()
        self.state = state

    def __repr__(self):
        return f"{self.letter} -> status='{self.state}' -> index={self.row_index};{self.col_index}"