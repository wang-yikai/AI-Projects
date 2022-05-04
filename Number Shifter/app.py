# Yikai Wang
from queue import PriorityQueue
from copy import deepcopy
import sys

# Given filename, opens the file and returns the initial and goal state
def parse(input):
    init_state = []
    goal_state = []

    i = 0
    for line in open(input, "r").readlines():
        # initial state is in lines 0 - 2
        if i < 3:
            init_state.append([ int(i) for i in line.split() ])
        # goal state is in lines 4 - 6
        elif i > 3 and i < 7:
            goal_state.append([ int(i) for i in line.split() ])
        i += 1

    return init_state, goal_state

# Gets the state in list form and converts it to a dictionary
# ex: dictionary[ 2 ] = [0, 1] means 2 is in row 0 column 1
# this makes it easier to compute the Manhattan distances and linear conflicts
def list_to_dict(state):
    d = dict()
    for r in range(len(state)):
        for c in range(len(state[r])):
            d[state[r][c]] = [r, c]
    return d

# Gets the state in dictionary form and converts it back to a list
# This makes it easier to debug (displaying the board) and to move the blank space
def dict_to_list(state):
    # Since there are 9 keys in the dictionary (0 - 8), each row is sqrt(length of dictionary) = 3
    l = [[0 for i in range(int(len(state) ** 0.5))] for i in range(int(len(state) ** 0.5))]
    for num in state:
        r, c = state[num][0], state[num][1]
        l[r][c] = num
    return l

# Helps display the board in an easier and more readable form
# Ex:
# 1 2 3
# 4 5 6
# 7 8 0
def output_puzzle(l):
    s = []
    for r in range(len(l)):
        for c in range(len(l[r])):
            s.append(str(l[r][c]) + " ")
        s.append("\n")
    return "".join(s)

# Given board in dictionary form, returns the sum of Manhattan distances
def sum_manhattan(state, goal):
    total = 0

    for num in range(1, len(state)):
        # Gets the row and column of the number in current state
        init_r, init_c = state[num][0], state[num][1]
        # Gets the row and column of the number in goal state
        goal_r, goal_c = goal[num][0], goal[num][1]
        total += abs(goal_r - init_r) + abs(goal_c - init_c)

    return total

# Given board in dictionary form, returns the number of linear conflicts
def num_linear_conflicts(state, goal):
    total = 0

    # First get the t_k
    for t_k in range(1, len(state)):
        # Gets the row and column of the t_k
        tk_r, tk_c = state[t_k][0], state[t_k][1]
        # Then get the t_j
        for t_j in range(1, len(state)):
            tj_r, tj_c = state[t_j][0], state[t_j][1]
            # Check if t_k and t_j are on the same row or column and t_j is to the right of t_k
            on_row_init = (tj_r == tk_r and tj_c > tk_c)
            on_col_init = (tj_c == tk_c and tj_r > tk_r)
            if on_row_init or on_col_init:
                # Gets the row and column of t_k and t_j in goal state
                goal_tj_r, goal_tj_c = goal[t_j][0], goal[t_j][1]
                goal_tk_r, goal_tk_c = goal[t_k][0], goal[t_k][1]
                # Check if t_k and t_j are on the same row or column and t_j is to the left of t_k and in the same row or column as current state
                on_row_goal = (goal_tj_r == goal_tk_r and goal_tj_c < goal_tk_c) and (tj_r == goal_tj_r)
                on_col_goal = (goal_tj_c == goal_tk_c and goal_tj_r < goal_tk_r) and (tj_c == goal_tj_c)
                if on_row_goal or on_col_goal:
                    # print(t_k, t_j)
                    total += 1

    return total

class Node:
    def __init__(self, state, goal, move = None, parent = None, option = 1):
        # What is the node's parent? Root node's parent is None
        self.parent = parent
        # Child node's depth is 1 more than parent's
        self.depth = 0 if parent is None else parent.depth + 1
        # States are in dictionary form to easily calculate cost
        self.state = state
        # Moves are U, D, L, R
        self.move = move
        self.cost = self.cost_function(goal, option)

    # Cost function is f(n) = g(n) + h(n)
    def cost_function(self, goal, option):
        #       g(n)      +     h(n)
        cost = self.depth + sum_manhattan(self.state, goal)
        # if linear conflicts are also chosen, just add that to cost
        if option == 2:
            cost += 2 * num_linear_conflicts(self.state, goal)
        return cost

    # For node == other node
    def __eq__(self, other):
        return self.cost == other.cost

    # For node < other node
    def __lt__(self, other):
        return self.cost < other.cost

    # For node > other node
    def __gt__(self, other):
        return self.cost > other.cost

    # For node <= other node
    def __le__(self, other):
        return self < other or self == other

    # For node >= other node
    def __ge__(self, other):
        return self > other or self == other

    # For node != other node
    def __ne__(self, other):
        return not (self == other)

class Puzzle:
    def __init__(self, initial_state, goal):
        # Uses Priority Queue to quickly get the next node with lowest cost
        self.frontier = PriorityQueue()
        # Graph Search, so store visited states
        self.explored = []
        # Store initial and goal states as dictionary form
        self.state = list_to_dict(initial_state)
        self.goal = list_to_dict(goal)
        # Total number of nodes generated
        self.nodes_gen = 0

    # Test to see if the state of the node is the goal state
    def goal_test(self, node_state):
        for num in node_state:
            if node_state[num][0] != self.goal[num][0] or node_state[num][1] != self.goal[num][1]:
                return False
        return True

    # For each possible move, check if we can add the new state to the frontier
    def add_child(self, l, parent, move, option):
        # Generates child node of parent
        child = Node(list_to_dict(l), self.goal, move, parent, option)
        # Check if we visited this state before
        if l not in self.explored:
            # print(child.cost, child)
            # print(self.frontier.queue)
            self.frontier.put(child)
            self.nodes_gen += 1

    # Given a node, determine the next, best state to go
    def next_state(self, node, option):
        l = dict_to_list(node.state)
        # Add the state to explored set
        self.explored.append(deepcopy(l))
        # Get the position of the blank space
        row, col = node.state[0][0], node.state[0][1]
        # Check for all available moves
        if row > 0:
            move = "U"
            l[row][col], l[row - 1][col] = l[row - 1][col], l[row][col]
            self.add_child(l, node, move, option)
            l = deepcopy(self.explored[-1])
        if row < (len(l) - 1):
            move = "D"
            l[row][col], l[row + 1][col] = l[row + 1][col], l[row][col]
            self.add_child(l, node, move, option)
            l = deepcopy(self.explored[-1])
        if col > 0:
            move = "L"
            l[row][col], l[row][col - 1] = l[row][col - 1], l[row][col]
            self.add_child(l, node, move, option)
            l = deepcopy(self.explored[-1])
        if col < (len(l) - 1):
            move = "R"
            l[row][col], l[row][col + 1] = l[row][col + 1], l[row][col]
            self.add_child(l, node, move, option)
            l = deepcopy(self.explored[-1])
        # Out of all available states, move to state with cheapest cost
        return self.frontier.get()

    # A* search for puzzle
    def search(self, option = 1):
        # Create root node for Graph Search
        node = Node(self.state, self.goal, None, None, option)
        self.nodes_gen += 1
        # If this state is not the goal state
        while not self.goal_test(node.state):
            node = self.next_state(node, option)
        return node

def main(user_input):
    # Gets initial and goal state from input file
    init_state, goal_state = parse(user_input[0])
    # Create output string
    output = [output_puzzle(init_state), "\n", output_puzzle(goal_state), "\n"]
    #Solve the puzzle
    puzzle = Puzzle(init_state, goal_state)
    goal_node = puzzle.search(user_input[1])
    # Addes the depth and nodes generated to output string
    output.append(str(goal_node.depth) + "\n" + str(puzzle.nodes_gen) + "\n")
    moves = []
    costs = []
    # Goes from the leaf to the root node
    node = goal_node
    while node is not None:
        # print(output_puzzle(dict_to_list(node.state)))
        # Gets the move of the node
        if node.move is not None:
            moves.append(node.move + " ")
        # Gets the cost of the node
        costs.append(str(node.cost) + " ")
        node = node.parent

    output.append("".join(moves[::-1]) + "\n")
    output.append("".join(costs[::-1]))
    output = "".join(output)
    print(output)
    return output

user_input = []
if len(sys.argv) < 2:
    user_input.append(input("Please enter the name of input file:\n"))
else:
    user_input.append(sys.argv[1])

if len(sys.argv) < 3:
    val = 0
    while not val or val > 2:
         val = int(input("Select:\n 1: Sum of Manhattan distances\n 2: Sum of Manhattan distances + 2 x # linear conflicts\n"))
    print()
    user_input.append(val)
else:
    user_input.append(int(sys.argv[2]))

output = main(user_input)

# Given name of the input file, create the correct filename of output file
filename = user_input[0].split(".")
if "input" in filename[0].lower():
    num = filename[0].lower().split("input")[1]
    letter = "A" if user_input[1] == 1 else "B"
    filename[0] = "Output" + num + "_" + letter

open(".".join(filename), "w").write(output)
