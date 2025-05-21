from browser.wordle_game import WordleGame

game = WordleGame()
game.start()
game.type_word("CRANE")
game.read_board()
game.board.display()
game.close()
