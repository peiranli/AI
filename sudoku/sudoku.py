from __future__ import print_function
import random
import copy
import time
import sys
from subprocess import call

# libraries for benchmark
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Grid:
    def __init__(self, problem):
        self.spots = [(i, j) for i in range(1, 10) for j in range(1, 10)]
        self.domains = {}
        # Need a dictionary that maps each spot to its related spots
        self.peers = {}
        self.rows = {}
        self.columns = {}
        self.squares = {}
        self.parse(problem)

    def parse(self, problem):
        for i in range(0, 9):
            for j in range(0, 9):
                c = problem[i*9+j]
                if c == '.':
                    self.domains[(i+1, j+1)] = range(1, 10)
                else:
                    self.domains[(i+1, j+1)] = [ord(c)-48]
                # compute peers in same row, column, square
                row = [(i+1, m+1) for m in range(0, 9) if m != j]
                column = [(n+1, j+1) for n in range(0, 9) if n != i]
                row_start = (i/3)*3
                row_end = (i/3+1)*3
                column_start = (j/3)*3
                column_end = (j/3+1)*3
                square = [(p+1, q+1) for p in range(row_start, row_end)
                          for q in range(column_start, column_end) if (p, q) != (i, j)]
                peers = []
                peers.extend(row)
                peers.extend(column)
                peers.extend(square)
                peer_set = set(peers)
                self.peers[(i+1, j+1)] = list(peer_set)
                self.rows[(i+1, j+1)] = row
                self.columns[(i+1, j+1)] = column
                self.squares[(i+1, j+1)] = square

    def display(self):
        for i in range(0, 9):
            for j in range(0, 9):
                d = self.domains[(i+1, j+1)]
                if len(d) == 1:
                    print(d[0], end='')
                else:
                    print('.', end='')
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            if i == 2 or i == 5:
                print("---------------")


class Solver:
    def __init__(self, grid):
        # sigma is the assignment function
        self.sigma = {}
        self.grid = grid

    def solve(self, sigma):
        for spot in self.grid.spots:
            if spot not in sigma and len(self.grid.domains[spot]) != 1:
                return False
        return True

    def search(self):
        sigma, s_failure = self.backtracking({})
        if not s_failure:
            self.sigma = sigma
            return True
        else:
            return False

    def backtracking(self, sigma):
        if self.solve(sigma):
            return sigma, False
        next_var = self.select_next_variable(sigma)
        for value in self.grid.domains[next_var]:
            inferences = {}
            i_failure = False
            s_failure = False
            if self.consistent(next_var, value, sigma):
                sigma[next_var] = value
                inferences, i_failure = self.infer(sigma)
                if not i_failure:
                    for e in inferences:
                        sigma[e] = inferences[e]
                    result, s_failure = self.backtracking(sigma)
                    if not s_failure:
                        return result, False
            for e in inferences:
                sigma.pop(e)
            if i_failure or s_failure:
                sigma.pop(next_var)
        return {}, True

    def consistent(self, spot, value, sigma):
        peers = self.grid.peers[spot]
        for e in peers:
            d = self.grid.domains[e]
            if (len(d) == 1 and value == d[0]) or (e in sigma and value == sigma[e]):
                return False
        return True

    def infer(self, sigma):
        inferences = {}
        for spot in self.grid.spots:
            if spot in sigma or len(self.grid.domains[spot]) == 1:
                pass
            else:
                # when only one space left, make inference
                row = self.grid.rows[spot]
                column = self.grid.columns[spot]
                square = self.grid.squares[spot]
                count_row = 0
                for e in row:
                    d = self.grid.domains[e]
                    if len(d) != 1 and e not in sigma:
                        count_row += 1
                count_column = 0
                for e in column:
                    d = self.grid.domains[e]
                    if len(d) != 1 and e not in sigma:
                        count_column += 1
                count_square = 0
                for e in square:
                    d = self.grid.domains[e]
                    if len(d) != 1 and e not in sigma:
                        count_square += 1
                if count_row == 0 or count_column == 0 or count_square == 0:
                    i_failure = True
                    for value in self.grid.domains[spot]:
                        if self.consistent(spot, value, sigma):
                            inferences[spot] = value
                            i_failure = False
                            break
                    if i_failure:
                        return {}, True
                else:
                    continue
        return (inferences, False)

    def select_next_variable(self, sigma):
        num = 10
        next = None
        for spot in self.grid.spots:
            if spot not in sigma and len(self.grid.domains[spot]) > 1:
                if len(self.grid.domains[spot]) < num:
                    num = len(self.grid.domains[spot])
                    next = spot
        return next

    def display(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if (i+1, j+1) in self.sigma:
                    print(self.sigma[(i+1, j+1)], end='')
                else:
                    print(self.grid.domains[(i+1, j+1)][0], end='')
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            if i == 2 or i == 5:
                print("---------------")


class PruneDomainSolver:
    def __init__(self, grid):
        # sigma is the assignment function
        self.sigma = {}
        self.grid = grid

    def search(self):
        sigma = self.backtracking()
        if sigma:
            self.sigma = sigma
            return True
        else:
            return False

    def backtracking(self):
        domain_stack = []
        domains = copy.deepcopy(self.grid.domains)
        domain_stack.append(domains)
        while domain_stack:
            current_domain = domain_stack.pop()
            if all([self.prune_till_fixed_point(spot, current_domain) for spot in self.grid.spots]):
                to_explore = None
                num = 10
                next = None
                # get next spot to make decision
                for spot in self.grid.spots:
                    if len(current_domain[spot]) > 1:
                        if len(current_domain[spot]) < num:
                            num = len(current_domain[spot])
                            next = spot
                to_explore = next
                if to_explore:
                    new_value = current_domain[to_explore].pop()
                    domain_stack.append(copy.deepcopy(current_domain))
                    current_domain[to_explore] = [new_value]
                    domain_stack.append(copy.deepcopy(current_domain))
                else:
                    return current_domain
        return {}

    def consistent(self, spot, value, domain):
        peers = self.grid.peers[spot]
        for e in peers:
            d = domain[e]
            if (len(d) == 1 and value == d[0]):
                return False
        return True

    def prune_till_fixed_point(self, spot, domain):
        # force arc-consistency
        for value in domain[spot]:
            if not self.consistent(spot, value, domain):
				removed = False
				if value in domain[spot]:
					domain[spot].remove(value)
					removed = True
				if removed:
                    # check if there is only one space left for value
					row_places = [s for s in self.grid.rows[spot] if value in domain[s]]
					if len(row_places) == 0:
						return {}
					elif len(row_places) == 1:
						domain[row_places[0]] = [value]
					column_places = [s for s in self.grid.columns[spot] if value in domain[s]]
					if len(column_places) == 0:
						return {}
					elif len(column_places) == 1:
						domain[column_places[0]] = [value]
					square_places = [s for s in self.grid.squares[spot] if value in domain[s]]
					if len(square_places) == 0:
						return {}
					elif len(square_places) == 1:
						domain[square_places[0]] = [value]

        # reduce to empty, conflict
        if not domain[spot]:
            return {}
        # a square reduced to one value
        elif len(domain[spot]) == 1:
            peers = self.grid.peers[spot]
            for peer in peers:
                if domain[spot][0] in domain[peer]:
                    if not self.prune_till_fixed_point(peer, domain):
                        return {}
        # prune
        for value in domain[spot]:
            row_places = [row for row in self.grid.rows[spot]
                          if value in domain[row]]
            column_places = [
                column for column in self.grid.columns[spot] if value in domain[column]]
            square_places = [
                square for square in self.grid.squares[spot] if value in domain[square]]
            if any([not row_places, not column_places, not square_places]):
                domain[spot] = [value]
                peers = self.grid.peers[spot]
                for peer in peers:
                    if value in domain[peer]:
                        if not self.prune_till_fixed_point(peer, domain):
                            return {}
                break
        return domain

    def display(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if (i+1, j+1) in self.sigma:
                    print(self.sigma[(i+1, j+1)][0], end='')
                else:
                    print(self.grid.domains[(i+1, j+1)][0], end='')
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            if i == 2 or i == 5:
                print("---------------")

class SATSolver:
    def __init__(self, grid):
        self.sigma = {}
        self.grid = grid
        self.vars = {}
    def init_vars(self):
        index = 1
        for spot in self.grid.spots:
            for value in range(1,10):
                self.vars[(spot,value)] = index
                index += 1
    def parse_cnf(self):
        num_fix = 0
        for spot in self.grid.spots:
            if len(self.grid.domains[spot]) == 1:
                num_fix += 1
        num_var = 9*9*9
        num_clause = num_fix + 81 + 81*20*9
        with open("./cnf/game.cnf", "w") as game_file:
            game_file.write("p cnf %i %i \n" % (num_var, num_clause))
            # value 1-9
            for spot in self.grid.spots:
                s = ""
                for value in range(1,10):
                    s+=str(self.vars[(spot, value)])
                    s+=" "
                s+=str(0)
                game_file.write(s+"\n")
            # grid
            for spot in self.grid.spots:
                d = self.grid.domains[spot]
                if len(d) == 1:
                    s = "" + str(self.vars[(spot, d[0])]) + " " + str(0)
                    game_file.write(s+"\n")
            # consistency
            for spot in self.grid.spots:
                peers = self.grid.peers[spot]
                for peer in peers:
                    for value in range(1,10):
                        s = "-" + str(self.vars[(spot, value)]) + " -" + str(self.vars[(peer, value)]) + " " + str(0)
                        game_file.write(s+"\n")

    def solve(self):
        self.init_vars()
        self.parse_cnf()
        # redirect output
        call("./picosat/picosat ./cnf/game.cnf > result",shell=True)
        call("rm ./cnf/game.cnf", shell=True)
        result = []
        solved = None
        # parse output
        with open("result", "r") as result_file:
            solved = result_file.readline()
            result = result_file.readlines()
        firstline = solved.split()
        done = False
        # parse firstline
        for word in firstline:
            if word == "SATISFIABLE":
                done = True
        words = []
        for line in result:
            words.extend(line.split(" "))
        for word in words:
            if word[0] == '-' or word[0] == 's' or word[0] == 'v' or word[0] == 'S' or word[0] == '0':
                pass
            else:
                spot, value = self.vars.keys()[self.vars.values().index(int(word))]
                self.sigma[spot] = [value]
        call("rm result", shell=True)
        return done

    def display(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if (i+1, j+1) in self.sigma:
                    print(self.sigma[(i+1, j+1)][0], end='')
                else:
                    print(self.grid.domains[(i+1, j+1)][0], end='')
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            if i == 2 or i == 5:
                print("---------------")

easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
        "2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3"]

hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
        "52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]

print("====Problem====")
g = Grid(hard[0])
# Display the original problem
g.display()
s = Solver(g)
#s_done = s.search()
ps = PruneDomainSolver(g)
t0 = time.time()
ps_done = ps.search()
t1 = time.time()
print("Performance time: ", t1-t0)
if ps_done:
    print("====Solution===")
    # Display the solution
    # Feel free to call other functions to display
    ps.display()
else:
    print("==No solution==")

print()
print("SAT solver")
sat = SATSolver(g)
t0 = time.time()
sat_done = sat.solve()
t1 = time.time()
print("Performance time: ", t1-t0)
if sat_done:
    print("====Solution===")
    # Display the solution
    # Feel free to call other functions to display
    sat.display()
else:
    print("==No solution==")


