from __future__ import print_function
import copy
import random
MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
ACTIONS = [(0, -1), (-1, 0), (0, 1), (1, 0)]

class State:
	# the tile matrix, player's turn, score, previous move
	def __init__(self, matrix, player, score, pre_move):
		self.tileMatrix = copy.deepcopy(matrix)
		self.player = player
		self.score = score
		self.pre_move = pre_move
	# override comparation operator
	def __eq__(self, other):
		return self.tileMatrix == other.tileMatrix and self.player == other.player and self.score == other.score and self.pre_move == other.pre_move
	# compute the largest tile in the grid
	def highest_tile(self):
		self.max_tile = 0
		for row in self.tileMatrix:
			for tile in row:
				self.max_tile = max(self.max_tile, tile)
		return self.max_tile
	# compute the summation of difference between each pair of neighbor
	def penalty(self):
		penalty = 0
		for i in range(0, len(self.tileMatrix)):
			for j in range(0, len(self.tileMatrix)):
				for m, n in ACTIONS:
					neighbor = (i+m, j+n)
					if 0 <= neighbor[0] < len(self.tileMatrix) and 0 <= neighbor[1] < len(self.tileMatrix):
						penalty += abs(self.tileMatrix[i][j] - self.tileMatrix[neighbor[0]][neighbor[1]])
		return penalty
	# compute the number of empty tile
	def empty_tile(self):
		count = 0
		for row in self.tileMatrix:
			for tile in row:
				if not tile:
					count += 1
		return count
	def heuristic_function(self):
		return self.score + 2*self.highest_tile() - self.penalty() + 2*self.empty_tile()
	

# Node class for game tree
class Node:
	def __init__(self, state, depth):
		self.state = copy.deepcopy(state)
		self.children = []
		self.reward = 0
		self.depth = depth
	def __eq__(self, other):
		return self.state == other.state and self.children == other.children

# class for virtual stack
class Snapshot:
	def __init__(self, value, node, returnVal, returnTo):
		self.value = value
		self.node = copy.deepcopy(node)
		self.returnVal = returnVal
		self.returnTo = returnTo
		self.checkedchildren = 0
		self.childindex = 0

class Gametree:
	"""main class for the AI"""
	# Hint: Two operations are important. Grow a game tree, and then compute minimax score.
	# Hint: To grow a tree, you need to simulate the game one step.
	# Hint: Think about the difference between your move and the computer's move.
	def __init__(self, root, depth, score): #root node
		self.maxdepth = depth # max depth of tree
		self.nodes = [] # nodes in tree
		self.root = Node(State(root, True, score, 4), 0) # root node
		self.nodes.append(self.root)
		self.frontier = []
	def traverse(self):
		for node in reversed(self.nodes):
			print("depth: ", node.depth)
			print("reward: ", node.reward)
	# grow the tree one level deeper
	def grow_once(self, state, depth):
		# find current node
		curr = self.find_node(state)
		# max player
		if(state.player):
			# simulate each move
			for direction in MOVES:
				si = Simulator(state.tileMatrix, state.score)
				si.move(direction)
				# check to see difference
				if(si.tileMatrix == state.tileMatrix):
					continue
				child = Node(State(si.tileMatrix, False, si.total_points, direction), depth)
				curr.children.append(child)
			# put children in nodes
			self.nodes.extend(curr.children)
		# chance player
		elif not state.player:
			tempMatrix = copy.deepcopy(state.tileMatrix)
			# compute all possible random tile 2
			for i in range(len(tempMatrix)):
				for j in range(len(tempMatrix[i])):
					if(tempMatrix[i][j] == 0):
						tempMatrix[i][j] = 2
						child = Node(State(tempMatrix, True, state.score, 4), depth)
						tempMatrix[i][j] = 0
						curr.children.append(child)
			# put children in nodes
			self.nodes.extend(curr.children)
		return curr
	# grow the tree from root
	def grow(self, height):
		curr_height = 0
		curr = self.root
		stack = [curr]
		# grow the tree by depth
		while(curr_height < height):
			# print("frontier: ", len(self.frontier))
			stack.extend(self.frontier)
			self.frontier = []
			# print("stack: ", len(stack))
			while stack:
				curr = stack.pop()
				curr = self.grow_once(curr.state, curr_height+1)
				self.frontier.extend(curr.children)
			curr_height += 1
		# print("frontier: ", len(self.frontier))
	# expectimax for computing best move
	def minimax(self, state):
		"""Compute minimax values on the three"""

		"""
		depth-5 algorithm incomplete

		curr = self.find_node(state)
		value = float('-inf')
		main = Snapshot(value, curr, 0, -1)
		stack = [main]
		while stack:
			length = len(stack)
			currsnapshot = stack[length-1]
			curr = self.find_node(currsnapshot.node.state)
			if not curr.children:
				curr.reward = curr.state.score + 2*curr.state.highest_tile() - curr.state.penalty() + 2*curr.state.empty_tile()
				currsnapshot.returnVal = curr.reward
				returnsnapshot = stack[currsnapshot.returnTo]
				if returnsnapshot.node.state.player:
					stack[currsnapshot.returnTo].value = max(stack[currsnapshot.returnTo].value, curr.reward)
				elif not returnsnapshot.node.state.player:
					stack[currsnapshot.returnTo].value += curr.reward/len(curr.node.children)
				stack.pop()
			elif curr.state.player:
				value = 0
				for child in curr.children:
					stack.append(Snapshot(value, child, 0, length-1))
			elif not curr.state.player:
				value = float('-inf')
				for child in curr.children:
					stack.append(Snapshot(value, child, 0, length-1))
		"""

		# get current node
		curr = self.find_node(state)

		# terminal node
		if not curr.children:
			curr.reward = curr.state.heuristic_function()
			# print("terminal: ",curr.reward)
		# max player
		elif(curr.state.player):
			value = float('-inf')
			# find the maximum
			for child in curr.children:
				reward = self.minimax(child.state)
				value = max(value, reward)
				# print("max child reward: ", reward)
			curr.reward = value
		# chance player computer
		elif not curr.state.player:
			value = 0
			# compute expectation value of next state
			for child in curr.children:
				reward = self.minimax(child.state)/len(curr.children)
				value = value + reward
				# print("chance child reward: ",reward)
			curr.reward = value
		else:
			raise ValueError
		print("reward: ",curr.reward)
		return curr.reward

	# function to return best decision to game
	def compute_decision(self):
		"""Derive a decision"""
		# Replace the following decision with what you compute
		self.grow(self.maxdepth)

		# Should also print the minimax value at the root
		maxvalue = self.minimax(self.root.state)
		# self.traverse()
		decision = 4
		# find the corresponding decision
		for child in self.root.children:
			if (maxvalue == child.reward):
				decision = child.state.pre_move
				break
		print(MOVES[decision])
		return decision
	def find_node(self, state):
		for i in range(len(self.nodes)):
			if(self.nodes[i].state == state):
				return self.nodes[i]

class Simulator:
	"""Simulation of the game"""
	# Hint: You basically need to copy all the code from the game engine itself.
	# Hint: The GUI code from the game engine should be removed.
	# Hint: Be very careful not to mess with the real game states.
	def __init__(self, matrix, score):
		self.tileMatrix = copy.deepcopy(matrix)
		self.total_points = score
		self.board_size = 4
	def move(self, direction):
		for i in range(0, direction):
			self.rotateMatrixClockwise()
		if self.canMove():
			self.moveTiles()
			self.mergeTiles()
		for j in range(0, (4 - direction) % 4):
			self.rotateMatrixClockwise()
	def moveTiles(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
					for k in range(j, self.board_size - 1):
						tm[i][k] = tm[i][k + 1]
					tm[i][self.board_size - 1] = 0
	def mergeTiles(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for k in range(0, self.board_size - 1):
				if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
					tm[i][k] = tm[i][k] * 2
					tm[i][k + 1] = 0
					self.total_points += tm[i][k]
					self.moveTiles()
	def checkIfCanGo(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size ** 2):
			if tm[int(i / self.board_size)][i % self.board_size] == 0:
				return True
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				if tm[i][j] == tm[i][j + 1]:
					return True
				elif tm[j][i] == tm[j + 1][i]:
					return True
		return False
	def canMove(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for j in range(1, self.board_size):
				if tm[i][j-1] == 0 and tm[i][j] > 0:
					return True
				elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
					return True
		return False
	def rotateMatrixClockwise(self):
		tm = self.tileMatrix
		for i in range(0, int(self.board_size/2)):
			for k in range(i, self.board_size- i - 1):
				temp1 = tm[i][k]
				temp2 = tm[self.board_size - 1 - k][i]
				temp3 = tm[self.board_size - 1 - i][self.board_size - 1 - k]
				temp4 = tm[k][self.board_size - 1 - i]
				tm[self.board_size - 1 - k][i] = temp1
				tm[self.board_size - 1 - i][self.board_size - 1 - k] = temp2
				tm[k][self.board_size - 1 - i] = temp3
				tm[i][k] = temp4
	def convertToLinearMatrix(self):
		m = []
		for i in range(0, self.board_size ** 2):
			m.append(self.tileMatrix[int(i / self.board_size)][i % self.board_size])
		m.append(self.total_points)
		return m
