# Tic-tac-toe using RL

# states: board configurations
# actions: free cells on the board
# value function: probability of winning

#  X | X | _
# -----------
#  _ | O | _
# -----------
#  _ | O | _

# If the board is 9x9 and each cell can contain either nothing, a X or a O, the
# possibilities amount to 3^9, but we know that the players alternate, so it's
# impossible for a board to have only Xs, or more in general, the number of Xs
# must be equal to the number of Os. We are assuming that Xs start.

# There can be up to 4 Xs on the board, likewise for Os, a state is X-playable
# if the number of Xs is equal to the number of Os, we are interested only in
# those configurations. We can ignore the possibility of having 5 Xs because
# it's the last move, and we can define it as winning 100% of the time.

# Having fixed the number of Xs and Os on the board to N, we can compute the
# number of possible boards as the number of subsequences without repetition and
# ignoring permutations of N elements from 9 total for the Xs and the same for
# the Os but instead of 9 we can pick only from 9 - N cells, hence:
# sum from n = 0 to 4, (9 choose n) * ((9 - n) choose n) = 3139

# Note that computing all the possible boards is not mandatory, but it's fun and
# handy in centain cases.

from copy import deepcopy
from tqdm import trange
from board import *
	
def board_configurations(board, boards, index = 0):
	# Backtracking

	if index > len(board):
		return True

	for _index in range(index, 9):
		if board[_index] == Cell.EMPTY:

			# X
			board[_index] = Cell.X
			if board.Xs() == board.Os():
				boards += [deepcopy(board)]
			if board_configurations(board, boards, _index):
				return True
			
			# O
			board[_index] = Cell.O
			if board.Xs() == board.Os():
				boards += [deepcopy(board)]
			if board_configurations(board, boards, _index):
				return True
			
			board[_index] = Cell.EMPTY

	return False

def play_game(policy1, policy2):
	board = Board()

	while board.status() == "ongoing":
		move = policy1.next_move(board)
		board[move] = Cell.X

		if board.status() != "ongoing": break

		move = policy2.next_move(board)
		board[move] = Cell.O

	return board.status()

def q_learning(rounds, init_board, learning):
	# Learn from the random policy, for lack of a better alternative
	policy = RandomPolicy()
	Q = DefaultDict(lambda board: { m: 0 for m in board.free() })

	for round in trange(rounds):
		current_board = deepcopy(init_board)
		history = []

		while True:
			if current_board.status() != "ongoing": break
	
			move = policy.next_move(current_board)
			history.append((deepcopy(current_board), move))
			current_board[move] = Cell.X
	
			if current_board.status() != "ongoing": break

			# Use the same random policy for the environment
			move = policy.next_move(current_board)
			current_board[move] = Cell.O

		if current_board.status() == "X wins":
			# We found a winning combination!
			winning_board, winning_move = history[-1]
			Q[winning_board] = Q[winning_board] | { winning_move: 1 }

			# Distribute reward to the boards which led to a win
			for time in range(len(history) - 2, -1, -1):
				board, move = history[time]
				next_board, next_move = history[time + 1]

				Q[board][move] = (1 - learning(round)) * Q[board][move] \
					+ learning(round) * (1 + Q[next_board][next_move])

			# q-learning is off-policy, so no update!
			# policy.update(Q)

	return Q
			
if __name__ == "__main__":
	for rounds in [10, 100, 1000, 10000, 100000]:
		learning = lambda round: 1 / (round + 1)
		Q = q_learning(rounds, Board(), learning)

		# From Q we can build a greey policy
		best = GreedyPolicy(Q)

		# Let's make it play against a random policy
		random = RandomPolicy()

		wins = 0
		for _ in trange(10000):
			outcome = play_game(best, random)
			wins += int(outcome == "X wins")

		print(f"{len(Q.keys())} boards discovered ({int(len(Q.keys()) / 3139 * 100)}%)")
		print(f"{wins} wins ({int(wins / 10000 * 100)}%)")
