from enum import Enum
import random

class Cell(Enum):
	EMPTY = 0
	X = 1
	O = 2

	def __str__(self):
		return {
			0: "_",
			1: "X",
			2: "O"
		}[self.value]

class Board():
	def __init__(self, side = 3):
		self.side = side
		self.board = [[Cell.EMPTY for _ in range(side)] for _ in range(side)]

	def __repr__(self):
		return "\n".join(" ".join(str(c) for c in row) for row in self.board)

	def __setitem__(self, index, value):
		i, j = index // self.side, index % self.side
		self.board[i][j] = value

	def __getitem__(self, index):
		i, j = index // self.side, index % self.side
		return self.board[i][j]

	def __len__(self):
		return self.side ** 2

	def __hash__(self):
		return hash(tuple(cell.value for row in self.board for cell in row))

	def __eq__(self, other):
		return self.board == other.board 

	def free(self):
		return [index for index in range(len(self)) if self[index] == Cell.EMPTY]

	def Xs(self):
		return sum(1 for row in self.board for cell in row if cell == Cell.X)    

	def Os(self):
		return sum(1 for row in self.board for cell in row if cell == Cell.O)    

	def draw(self):
		return self.free() == [] and not self.win(Cell.X) and not self.win(Cell.O)

	def status(self):
		if self.draw(): return "draw"
		if self.win(Cell.X): return "X wins"
		if self.win(Cell.O): return "O wins"
		if self.free() != 0: return "ongoing"
		raise ValueError("Unknown board status")

	def win(self, symbol = Cell.X):
		if any(set(self.board[i]) == {symbol} for i in range(self.side)):
			return True # rows
		
		if any(set(self.board[i][j] for i in range(self.side)) == {symbol} for j in range(self.side)):
			return True # cols

		if set(self[self.side * i + i] for i in range(0, self.side)) == {symbol}:
			return True # desc diag

		if set(self[self.side * i + (self.side - i - 1)] for i in range(0, self.side)) == {symbol}:
			return True # inc diag

		return False

# Policies

class Policy():
	def update(Q): pass
	def next_move(board): pass

class StochasticPolicy(Policy):
	def __init__(self):
		self.Q = None

	def update(self, Q):
		self.Q = Q
	
	def next_move(self, board): pass
		# usa Q[board] come distribuzione (?)
		# return self.Q[board]

class GreedyPolicy(Policy):
	def __init__(self, Q):
		self.Q = Q

	def update(self, Q):
		self.Q = Q

	def next_move(self, board):
		# Return the move with the highest value
		return max(self.Q[board], key=self.Q[board].get)

class RandomPolicy(Policy):
	def next_move(self, board):
		moves = board.free()
		return random.choice(moves) if moves != [] else None

# class RandomPlayer():
# 	def __init__(self, board, symbol):
# 		self.board = board
# 		self.symbol = symbol

# 	def update(self, board):
# 		self.board = board

# 	def play(self):
# 		index = random.choice(self.board.free())
# 		self.board[index] = self.symbol
# 		return self.board
		

# defaultdict does not accept a parametrized lambda to initialize keys, WHY?
from collections import defaultdict

class DefaultDict(defaultdict):
    def __missing__(self, key):
		# Don't, or the dict will explode in size
        # self[key] = self.default_factory(key)
        return self.default_factory(key)
