from math import sqrt, log
import copy
import time
import numpy as np

MOVES = {"n": (-1,0), "s": (1,0), "e": (0, 1), "w": (0, -1), "se": (1, 1), "nw": (-1, -1), "ne": (-1, 1), "sw": (1, -1)}

class State:
    def __init__(self, grid, player):
        self.grid = copy.deepcopy(grid)
        self.maxrc = len(grid)-1
        self.player = player
        self.reward = [0,0]
        self.pre_move = (-1, -1)
        self.children = []
        self.grid_count = 19
        self.parent = None

    # one player win or fully expanded
    def terminal_state(self):
        return self.check_win() or self.full_expand()

    def full_expand(self):
        return len(self.get_options(self.grid)) == 0

    # check one player win
    def check_win(self):
        if(self.pre_move == (-1,-1)):
            return False
        r = self.pre_move[0]
        c = self.pre_move[1]
        n_count = self.get_continuous_count(r, c, MOVES["n"])
        s_count = self.get_continuous_count(r, c, MOVES["s"])
        e_count = self.get_continuous_count(r, c, MOVES["e"])
        w_count = self.get_continuous_count(r, c, MOVES["w"])
        se_count = self.get_continuous_count(r, c, MOVES["se"])
        nw_count = self.get_continuous_count(r, c, MOVES["nw"])
        ne_count = self.get_continuous_count(r, c, MOVES["ne"])
        sw_count = self.get_continuous_count(r, c, MOVES["sw"])
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            self.winner = self.grid[r][c]
            return True
        return False

    # get continuous count in one direction
    def get_continuous_count(self, r, c, move):
        piece = self.player
        result = 0
        i = 1
        dr = move[0]
        dc = move[1]
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    # get continuous count in one direction and check the blocked cond 
    def get_neighbor_continuous_count(self, option, direction):
        piece = self.player
        if self.player == 'b':
            opponent = 'w'
        else:
            opponent = 'b'
        result = 0
        i = 1
        r = option[0]
        c = option[1]
        dr = direction[0]
        dc = direction[1]
        blocked = False
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                elif self.grid[new_r][new_c] == opponent:
                    blocked = True
                    break
                else:
                    break
            else:
                blocked = True
                break
            i += 1
        return (result, blocked)
    
    # get continuous opponent count and check if blocked
    def get_neighbor_opponent_count(self, option, direction):
        if self.player == 'b':
            piece = 'w'
        else:
            piece = 'b'
        result = 0
        i = 1
        r = option[0]
        c = option[1]
        dr = direction[0]
        dc = direction[1]
        blocked = False
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                elif self.grid[new_r][new_c] == self.player:
                    blocked = True
                    break
                else:
                    break
            else:
                blocked = True
                break
            i += 1
        return (result, blocked)

    # o.oo cond for free three
    def get_next_neighbor_continuous_count(self, option, direction):
        piece = self.player
        if self.player == 'b':
            opponent = 'w'
        else:
            opponent = 'b'
        result = 0
        i = 1
        r = option[0]
        c = option[1]
        dr = direction[0]
        dc = direction[1]
        new_r = r + dr * i
        new_c = c + dc * i
        if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
            if self.grid[new_r][new_c] == piece:
                return (result, False)
            elif self.grid[new_r][new_c] == opponent:
                return (result, True)
            else:
                r = new_r
                c = new_c
        blocked = False
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                elif self.grid[new_r][new_c] == opponent:
                    blocked = True
                    break
                else:
                    break
            else:
                blocked = True
                break
            i += 1
        return (result, blocked)
    
    # o.oo cond for opponent free three
    def get_next_neighbor_opponent_count(self, option, direction):
        if self.player == 'b':
            piece = 'w'
        else:
            piece = 'b'
        result = 0
        i = 1
        r = option[0]
        c = option[1]
        dr = direction[0]
        dc = direction[1]
        new_r = r + dr * i
        new_c = c + dc * i
        if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
            if self.grid[new_r][new_c] == piece:
                return (result, False)
            elif self.grid[new_r][new_c] == self.player:
                return (result, True)
            else:
                r = new_r
                c = new_c
        blocked = False
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                elif self.grid[new_r][new_c] == self.player:
                    blocked = True
                    break
                else:
                    break
            else:
                blocked = True
                break
            i += 1
        return (result, blocked)
    
    # oo.o cond for free three
    def get_neighbor_space_continuous_count(self, option, direction):
        piece = self.player
        if self.player == 'b':
            opponent = 'w'
        else:
            opponent = 'b'
        result = 0
        i = 1
        r = option[0]
        c = option[1]
        dr = direction[0]
        dc = direction[1]
        new_r = r + dr * i
        new_c = c + dc * i
        if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
            if self.grid[new_r][new_c] == piece:
                r = new_r
                c = new_c
            elif self.grid[new_r][new_c] == opponent:
                return (result, True)
            else:
                return (result, False)
        count, blocked = self.get_next_neighbor_continuous_count((r,c), (dr,dc))
        if count:
            result = 1+count
        return (result, blocked)

    # oo.o cond for opponent free three
    def get_neighbor_space_opponent_count(self, option, direction):
        if self.player == 'b':
            piece = 'w'
        else:
            piece = 'b'
        result = 0
        i = 1
        r = option[0]
        c = option[1]
        dr = direction[0]
        dc = direction[1]
        new_r = r + dr * i
        new_c = c + dc * i
        if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
            if self.grid[new_r][new_c] == piece:
                r = new_r
                c = new_c
            elif self.grid[new_r][new_c] == self.player:
                return (result, True)
            else:
                return (result, False)
        count, blocked = self.get_next_neighbor_opponent_count((r,c), (dr,dc))
        if count:
            result = 1+count
        return (result, blocked)

    def get_options(self, grid):
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc/2, self.maxrc/2)]
        #Reasonable moves should be close to where the current pieces are
        #min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-2)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+2)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-2)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+2)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i,j))
        return options

    def get_neighbor_continuous_counts(self, option):
        return {move: self.get_neighbor_continuous_count(option, direction) for move, direction in MOVES.iteritems()}
    
    def get_next_neighbor_continuous_counts(self, option):
        return {move: self.get_next_neighbor_continuous_count(option, direction) for move, direction in MOVES.iteritems()}
    
    def get_neighbor_opponent_counts(self, option):
        return {move: self.get_neighbor_opponent_count(option, direction) for move, direction in MOVES.iteritems()}
    
    def get_next_neighbor_opponent_counts(self, option):
        return {move: self.get_next_neighbor_opponent_count(option, direction) for move, direction in MOVES.iteritems()}

    def get_neighbor_space_continuous_counts(self, option):
        return {move: self.get_neighbor_space_continuous_count(option, direction) for move, direction in MOVES.iteritems()}
    
    def get_neighbor_space_opponent_counts(self, option):
        return {move: self.get_neighbor_space_opponent_count(option, direction) for move, direction in MOVES.iteritems()}

    def get_moves(self):
        options = self.get_options(self.grid)
        option_dict = {option: 0 for option in options}

        for option in options:
            n_cc = self.get_neighbor_continuous_counts(option)
            nn_cc = self.get_next_neighbor_continuous_counts(option)
            n_oc = self.get_neighbor_opponent_counts(option)
            nn_oc = self.get_next_neighbor_opponent_counts(option)
            np_cc = self.get_neighbor_space_continuous_counts(option)
            np_oc = self.get_neighbor_space_opponent_counts(option)

            n_count, n_blocked = n_cc["n"]
            s_count, s_blocked = n_cc["s"]
            w_count, w_blocked = n_cc["w"]
            e_count, e_blocked = n_cc["e"]
            se_count, se_blocked = n_cc["se"]
            nw_count, nw_blocked = n_cc["nw"]
            ne_count, ne_blocked = n_cc["ne"]
            sw_count, sw_blocked = n_cc["sw"]

            n_op_count, n_op_blocked = n_oc["n"]
            s_op_count, s_op_blocked = n_oc["s"]
            w_op_count, w_op_blocked = n_oc["w"]
            e_op_count, e_op_blocked = n_oc["e"]
            se_op_count, se_op_blocked = n_oc["se"]
            nw_op_count, nw_op_blocked = n_oc["nw"]
            ne_op_count, ne_op_blocked = n_oc["ne"]
            sw_op_count, sw_op_blocked = n_oc["sw"]

            n_nn_count, n_nn_blocked = nn_cc["n"]
            s_nn_count, s_nn_blocked = nn_cc["s"]
            w_nn_count, w_nn_blocked = nn_cc["w"]
            e_nn_count, e_nn_blocked = nn_cc["e"]
            se_nn_count, se_nn_blocked = nn_cc["se"]
            nw_nn_count, nw_nn_blocked = nn_cc["nw"]
            ne_nn_count, ne_nn_blocked = nn_cc["ne"]
            sw_nn_count, sw_nn_blocked = nn_cc["sw"]

            n_nn_op_count, n_nn_op_blocked = nn_oc["n"]
            s_nn_op_count, s_nn_op_blocked = nn_oc["s"]
            w_nn_op_count, w_nn_op_blocked = nn_oc["w"]
            e_nn_op_count, e_nn_op_blocked = nn_oc["e"]
            se_nn_op_count, se_nn_op_blocked = nn_oc["se"]
            nw_nn_op_count, nw_nn_op_blocked = nn_oc["nw"]
            ne_nn_op_count, ne_nn_op_blocked = nn_oc["ne"]
            sw_nn_op_count, sw_nn_op_blocked = nn_oc["sw"]

            n_np_count, n_np_blocked = np_cc["n"]
            s_np_count, s_np_blocked = np_cc["s"]
            w_np_count, w_np_blocked = np_cc["w"]
            e_np_count, e_np_blocked = np_cc["e"]
            se_np_count, se_np_blocked = np_cc["se"]
            nw_np_count, nw_np_blocked = np_cc["nw"]
            ne_np_count, ne_np_blocked = np_cc["ne"]
            sw_np_count, sw_np_blocked = np_cc["sw"]

            n_np_op_count, n_np_op_blocked = np_oc["n"]
            s_np_op_count, s_np_op_blocked = np_oc["s"]
            w_np_op_count, w_np_op_blocked = np_oc["w"]
            e_np_op_count, e_np_op_blocked = np_oc["e"]
            se_np_op_count, se_np_op_blocked = np_oc["se"]
            nw_np_op_count, nw_np_op_blocked = np_oc["nw"]
            ne_np_op_count, ne_np_op_blocked = np_oc["ne"]
            sw_np_op_count, sw_np_op_blocked = np_oc["sw"]


            # form five, kill move
            if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
                option_dict[option] += 1000000
            # form four
            elif (n_count + s_count + 1 == 4 and not n_blocked and not s_blocked) or (e_count + w_count + 1 == 4 and not e_blocked and not w_blocked) or \
                (se_count + nw_count + 1 == 4 and not se_blocked and not nw_blocked) or (ne_count + sw_count + 1 == 4 and not ne_blocked and not sw_blocked):
                option_dict[option] += 100000
            # form double threes
            elif (((n_count + s_count + 1 >= 3 and not n_blocked and not s_blocked or n_count + s_count + 1 >= 4 and (n_blocked or s_blocked) and n_blocked != s_blocked) or \
                (w_count + e_count + 1 >= 3 and not w_blocked and not e_blocked or e_count + w_count + 1 >= 4 and (e_blocked or w_blocked) and e_blocked != w_blocked) or \
                (n_count + s_nn_count + 1 >= 3 and not n_blocked and not s_nn_blocked or n_count + s_nn_count + 1 >= 4 and (n_blocked or s_nn_blocked) and n_blocked != s_nn_blocked) or \
                (n_nn_count + s_count + 1 >= 3 and not n_nn_blocked and not s_blocked or n_nn_count + s_count + 1 >= 4 and (n_nn_blocked or s_blocked) and n_nn_blocked != s_blocked) or \
                (w_count + e_nn_count + 1 >= 3 and not w_blocked and not e_nn_blocked or e_nn_count + w_count + 1 >= 4 and (e_nn_blocked or w_blocked) and e_nn_blocked != w_blocked) or \
                (w_nn_count + e_count + 1 >= 3 and not w_nn_blocked and not e_blocked or e_count + w_nn_count + 1 >= 4 and (e_blocked or w_nn_blocked) and e_blocked != w_nn_blocked) or \
                (n_np_count + s_np_count + 1 >= 3 and not n_np_blocked and not s_np_blocked or n_np_count + s_np_count + 1 >= 4 and (n_np_blocked or s_np_blocked) and n_np_blocked != s_np_blocked) or \
                (w_np_count + e_np_count + 1 >= 3 and not w_np_blocked and not e_np_blocked or w_np_count + e_np_count + 1 >= 4 and (w_np_blocked or e_np_blocked) and w_np_blocked != e_np_blocked)) and \
                ((ne_count + sw_count + 1 >= 3 and not ne_blocked and not sw_blocked or ne_count + sw_count + 1 >= 4 and (ne_blocked or sw_blocked) and ne_blocked != sw_blocked) or \
                (nw_count + se_count + 1 >= 3 and not nw_blocked and not se_blocked or se_count + nw_count + 1 >= 4 and (se_blocked or nw_blocked) and se_blocked != nw_blocked) or \
                (ne_count + sw_nn_count + 1 >= 3 and not ne_blocked and not sw_nn_blocked or ne_count + sw_nn_count + 1 >= 4 and (ne_blocked or sw_nn_blocked) and ne_blocked != sw_nn_blocked) or \
                (nw_nn_count + se_count + 1 >= 3 and not nw_nn_blocked and not se_blocked or se_count + nw_nn_count + 1 >= 4 and (se_blocked or nw_nn_blocked) and se_blocked != nw_nn_blocked) or \
                (ne_nn_count + sw_count + 1 >= 3 and not ne_nn_blocked and not sw_blocked or ne_nn_count + sw_count + 1 >= 4 and (ne_nn_blocked or sw_blocked) and ne_nn_blocked != sw_blocked) or \
                (nw_count + se_nn_count + 1 >= 3 and not nw_blocked and not se_nn_blocked or se_nn_count + nw_count + 1 >= 4 and (se_nn_blocked or nw_blocked) and se_nn_blocked != nw_blocked) or \
                (ne_np_count + sw_np_count + 1 >= 3 and not ne_np_blocked and not sw_np_blocked or ne_np_count + sw_np_count + 1 >= 4 and (ne_np_blocked or sw_np_blocked) and ne_np_blocked != sw_np_blocked) or \
                (nw_np_count + se_np_count + 1 >= 3 and not nw_np_blocked and not se_np_blocked or se_np_count + nw_np_count + 1 >= 4 and (se_np_blocked or nw_np_blocked) and se_np_blocked != nw_np_blocked) )) or \
                (((n_count + s_count + 1 >= 3 and not n_blocked and not s_blocked or n_count + s_count + 1 >= 4 and (n_blocked or s_blocked) and n_blocked != s_blocked) or \
                (n_count + s_nn_count + 1 >= 3 and not n_blocked and not s_nn_blocked or n_count + s_nn_count + 1 >= 4 and (n_blocked or s_nn_blocked) and n_blocked != s_nn_blocked) or \
                (n_nn_count + s_count + 1 >= 3 and not n_nn_blocked and not s_blocked or n_nn_count + s_count + 1 >= 4 and (n_nn_blocked or s_blocked) and n_nn_blocked != s_blocked) or \
                (n_np_count + s_np_count + 1 >= 3 and not n_np_blocked and not s_np_blocked or n_np_count + s_np_count + 1 >= 4 and (n_np_blocked or s_np_blocked) and n_np_blocked != s_np_blocked)) and \
                ((w_count + e_count + 1 >= 3 and not w_blocked and not e_blocked or e_count + w_count + 1 >= 4 and (e_blocked or w_blocked) and e_blocked != w_blocked) or \
                (w_count + e_nn_count + 1 >= 3 and not w_blocked and not e_nn_blocked or e_nn_count + w_count + 1 >= 4 and (e_nn_blocked or w_blocked) and e_nn_blocked != w_blocked) or \
                (w_nn_count + e_count + 1 >= 3 and not w_nn_blocked and not e_blocked or e_count + w_nn_count + 1 >= 4 and (e_blocked or w_nn_blocked) and e_blocked != w_nn_blocked) or \
                (w_np_count + e_np_count + 1 >= 3 and not w_np_blocked and not e_np_blocked or e_np_count + w_np_count + 1 >= 4 and (e_np_blocked or w_np_blocked) and e_np_blocked != w_np_blocked))) or \
                (((ne_count + sw_count + 1 >= 3 and not ne_blocked and not sw_blocked or ne_count + sw_count + 1 >= 4 and (ne_blocked or sw_blocked) and ne_blocked != sw_blocked) or \
                (ne_count + sw_nn_count + 1 >= 3 and not ne_blocked and not sw_nn_blocked or ne_count + sw_nn_count + 1 >= 4 and (ne_blocked or sw_nn_blocked) and ne_blocked != sw_nn_blocked) or \
                (ne_nn_count + sw_count + 1 >= 3 and not ne_nn_blocked and not sw_blocked or ne_nn_count + sw_count + 1 >= 4 and (ne_nn_blocked or sw_blocked) and ne_nn_blocked != sw_blocked) or \
                (ne_np_count + sw_np_count + 1 >= 3 and not ne_np_blocked and not sw_np_blocked or ne_np_count + sw_np_count + 1 >= 4 and (ne_np_blocked or sw_np_blocked) and ne_np_blocked != sw_np_blocked)) and \
                ((nw_count + se_count + 1 >= 3 and not nw_blocked and not se_blocked or se_count + nw_count + 1 >= 4 and (se_blocked or nw_blocked) and se_blocked != nw_blocked) or \
                (nw_count + se_nn_count + 1 >= 3 and not nw_blocked and not se_nn_blocked or se_nn_count + nw_count + 1 >= 4 and (se_nn_blocked or nw_blocked) and se_nn_blocked != nw_blocked) or \
                (nw_nn_count + se_count + 1 >= 3 and not nw_nn_blocked and not se_blocked or se_count + nw_nn_count + 1 >= 4 and (se_blocked or nw_nn_blocked) and se_blocked != nw_nn_blocked) or \
                (nw_np_count + se_np_count + 1 >= 3 and not nw_np_blocked and not se_np_blocked or se_np_count + nw_np_count + 1 >= 4 and (se_np_blocked or nw_np_blocked) and se_np_blocked != nw_np_blocked))):
                option_dict[option] += 20000
            # form three
            elif (n_count + s_count + 1 == 3 and not n_blocked and not s_blocked) or (e_count + w_count + 1 == 3 and not e_blocked and not w_blocked) or \
                (se_count + nw_count + 1 == 3 and not se_blocked and not nw_blocked) or (ne_count + sw_count + 1 == 3 and not ne_blocked and not sw_blocked):
                option_dict[option] += 10000
            # form three with one space
            elif (n_count + s_nn_count + 1 == 3 and not n_blocked and not s_nn_blocked) or (n_nn_count + s_count + 1 == 3 and not n_nn_blocked and not s_blocked) or \
                (e_count + w_nn_count + 1 == 3 and not e_blocked and not w_nn_blocked) or (e_nn_count + w_count + 1 == 3 and not e_nn_blocked and not w_blocked) or \
                (se_count + nw_nn_count + 1 == 3 and not se_blocked and not nw_nn_blocked) or (ne_count + sw_nn_count + 1 == 3 and not ne_blocked and not sw_nn_blocked) or \
                (se_nn_count + nw_count + 1 == 3 and not se_nn_blocked and not nw_blocked) or (ne_nn_count + sw_count + 1 == 3 and not ne_nn_blocked and not sw_blocked):
                option_dict[option] += 8000
            # form blocked four
            elif (n_count + s_count + 1 >= 4 and (n_blocked or s_blocked) and n_blocked != s_blocked) or (e_count + w_count + 1 >= 4 and (e_blocked or w_blocked) and e_blocked != w_blocked) or \
                (se_count + nw_count + 1 >= 4 and (se_blocked or nw_blocked) and se_blocked != nw_blocked) or (ne_count + sw_count + 1 >= 4 and (ne_blocked or sw_blocked) and ne_blocked != sw_blocked):
                option_dict[option] += 10000
            # form blocked four with one space
            elif (n_count + s_nn_count + 1 >= 4 and (n_blocked or s_nn_blocked) and n_blocked != s_nn_blocked) or (n_nn_count + s_count + 1 >= 4 and (n_nn_blocked or s_blocked) and n_nn_blocked != s_blocked) or \
                (e_count + w_nn_count + 1 >= 4 and (e_blocked or w_nn_blocked) and e_blocked != w_nn_blocked) or (e_nn_count + w_count + 1 >= 4 and (e_nn_blocked or w_blocked) and e_nn_blocked != w_blocked) or \
                (se_count + nw_nn_count + 1 >= 4 and (se_blocked or nw_nn_blocked) and se_blocked != nw_nn_blocked) or (ne_count + sw_nn_count + 1 >= 4 and (ne_blocked or sw_nn_blocked) and ne_blocked != sw_nn_blocked) or \
                (se_nn_count + nw_count + 1 >= 4 and (se_nn_blocked or nw_blocked) and se_nn_blocked != nw_blocked) or (ne_nn_count + sw_count + 1 >= 4 and (ne_nn_blocked or sw_blocked) and ne_nn_blocked != sw_blocked):
                option_dict[option] += 8000
            # form double twos
            elif (((n_count >= 1 and not n_blocked and not s_blocked) or (s_count >= 1 and not s_blocked and not n_blocked) or (e_count >= 1 and not e_blocked and not w_blocked) or (w_count >= 1 and not w_blocked and not e_blocked)) and \
                ((ne_count >= 1 and not ne_blocked and not sw_blocked) or (nw_count >= 1 and not nw_blocked and not se_blocked) or (se_count >= 1 and not se_blocked and not nw_blocked) or (sw_count >= 1 and not sw_blocked and not ne_blocked) )) or \
                (((n_count >= 1 and not n_blocked and not s_blocked) or (s_count >= 1 and not s_blocked and not n_blocked)) and ((e_count >= 1 and not e_blocked and not w_blocked) or (w_count >= 1 and not w_blocked and not e_blocked) )) or \
                (((nw_count >= 1 and not nw_blocked and not se_blocked) or (se_count >= 1 and not se_blocked and not nw_blocked)) and ((ne_count >= 1 and not ne_blocked and not sw_blocked) or (sw_count >= 1 and not sw_blocked and not ne_blocked) )):
                option_dict[option] += 200
            # form two
            elif (n_count + s_count + 1 == 2 and not n_blocked and not s_blocked) or (e_count + w_count + 1 == 2 and not e_blocked and not w_blocked) or \
                (se_count + nw_count + 1 == 2 and not se_blocked and not nw_blocked) or (ne_count + sw_count + 1 == 2 and not ne_blocked and not sw_blocked):
                option_dict[option] += 100
            # free one
            elif (not n_blocked and not s_blocked) or (not e_blocked and not w_blocked) or (not sw_blocked and not ne_blocked) or (not se_blocked and not nw_blocked):
                option_dict[option] += 10
            else:
                option_dict[option] += 0

            # block five, better than from four and double threes
            if (n_op_count + s_op_count + 1 >= 5) or (e_op_count + w_op_count + 1 >= 5) or \
                (se_op_count + nw_op_count + 1 >= 5) or (ne_op_count + sw_op_count + 1 >= 5):
                option_dict[option] += 150000
            # block double threes, better than form three, worse than double threes
            elif (((n_op_count + s_op_count + 1 >= 3 and not n_op_blocked and not s_op_blocked or n_op_count + s_op_count + 1 >= 4 and (n_op_blocked or s_op_blocked) and n_op_blocked != s_op_blocked) or \
                (w_op_count + e_op_count + 1 >= 3 and not w_op_blocked and not e_op_blocked or e_op_count + w_op_count + 1 >= 4 and (e_op_blocked or w_op_blocked) and e_op_blocked != w_op_blocked) or \
                (n_op_count + s_nn_op_count + 1 >= 3 and not n_op_blocked and not s_nn_op_blocked or n_op_count + s_nn_op_count + 1 >= 4 and (n_op_blocked or s_nn_op_blocked) and n_op_blocked != s_nn_op_blocked) or \
                (n_nn_op_count + s_op_count + 1 >= 3 and not n_nn_op_blocked and not s_op_blocked or n_nn_op_count + s_op_count + 1 >= 4 and (n_nn_op_blocked or s_op_blocked) and n_nn_op_blocked != s_op_blocked) or \
                (w_op_count + e_nn_op_count + 1 >= 3 and not w_op_blocked and not e_nn_op_blocked or e_nn_op_count + w_op_count + 1 >= 4 and (e_nn_op_blocked or w_op_blocked) and e_nn_op_blocked != w_op_blocked) or \
                (w_nn_op_count + e_op_count + 1 >= 3 and not w_nn_op_blocked and not e_op_blocked or e_op_count + w_nn_op_count + 1 >= 4 and (e_op_blocked or w_nn_op_blocked) and e_op_blocked != w_nn_op_blocked) or \
                (n_np_op_count + s_np_op_count + 1 >= 3 and not n_np_op_blocked and not s_np_op_blocked or n_np_op_count + s_np_op_count + 1 >= 4 and (n_np_op_blocked or s_np_op_blocked) and n_np_op_blocked != s_np_op_blocked) or \
                (w_np_op_count + e_np_op_count + 1 >= 3 and not w_np_op_blocked and not e_np_op_blocked or w_np_op_count + e_np_op_count + 1 >= 4 and (w_np_op_blocked or e_np_op_blocked) and w_np_op_blocked != e_np_op_blocked)) and \
                ((ne_op_count + sw_op_count + 1 >= 3 and not ne_op_blocked and not sw_op_blocked or ne_op_count + sw_op_count + 1 >= 4 and (ne_op_blocked or sw_op_blocked) and ne_op_blocked != sw_op_blocked) or \
                (nw_op_count + se_op_count + 1 >= 3 and not nw_op_blocked and not se_op_blocked or se_op_count + nw_op_count + 1 >= 4 and (se_op_blocked or nw_op_blocked) and se_op_blocked != nw_op_blocked) or \
                (ne_op_count + sw_nn_op_count + 1 >= 3 and not ne_op_blocked and not sw_nn_op_blocked or ne_op_count + sw_nn_op_count + 1 >= 4 and (ne_op_blocked or sw_nn_op_blocked) and ne_op_blocked != sw_nn_op_blocked) or \
                (nw_nn_op_count + se_op_count + 1 >= 3 and not nw_nn_op_blocked and not se_op_blocked or se_op_count + nw_nn_op_count + 1 >= 4 and (se_op_blocked or nw_nn_op_blocked) and se_op_blocked != nw_nn_op_blocked) or \
                (ne_nn_op_count + sw_op_count + 1 >= 3 and not ne_nn_op_blocked and not sw_op_blocked or ne_nn_op_count + sw_op_count + 1 >= 4 and (ne_nn_op_blocked or sw_op_blocked) and ne_nn_op_blocked != sw_op_blocked) or \
                (nw_op_count + se_nn_op_count + 1 >= 3 and not nw_op_blocked and not se_nn_op_blocked or se_nn_op_count + nw_op_count + 1 >= 4 and (se_nn_op_blocked or nw_op_blocked) and se_nn_op_blocked != nw_op_blocked) or \
                (ne_np_op_count + sw_np_op_count + 1 >= 3 and not ne_np_op_blocked and not sw_np_op_blocked or ne_np_op_count + sw_np_op_count + 1 >= 4 and (ne_np_op_blocked or sw_np_op_blocked) and ne_np_op_blocked != sw_np_op_blocked) or \
                (nw_np_op_count + se_np_op_count + 1 >= 3 and not nw_np_op_blocked and not se_np_op_blocked or se_np_op_count + nw_np_op_count + 1 >= 4 and (se_np_op_blocked or nw_np_op_blocked) and se_np_op_blocked != nw_np_op_blocked))) or \
                (((n_op_count + s_op_count + 1 >= 3 and not n_op_blocked and not s_op_blocked or n_op_count + s_op_count + 1 >= 4 and (n_op_blocked or s_op_blocked) and n_op_blocked != s_op_blocked) or \
                (n_op_count + s_nn_op_count + 1 >= 3 and not n_op_blocked and not s_nn_op_blocked or n_op_count + s_nn_op_count + 1 >= 4 and (n_op_blocked or s_nn_op_blocked) and n_op_blocked != s_nn_op_blocked) or \
                (n_nn_op_count + s_op_count + 1 >= 3 and not n_nn_op_blocked and not s_op_blocked or n_nn_op_count + s_op_count + 1 >= 4 and (n_nn_op_blocked or s_op_blocked) and n_nn_op_blocked != s_op_blocked) or \
                (n_np_op_count + s_np_op_count + 1 >= 3 and not n_np_op_blocked and not s_np_op_blocked or n_np_op_count + s_np_op_count + 1 >= 4 and (n_np_op_blocked or s_np_op_blocked) and n_np_op_blocked != s_np_op_blocked)) and \
                ((w_op_count + e_op_count + 1 >= 3 and not w_op_blocked and not e_op_blocked or e_op_count + w_op_count + 1 >= 4 and (e_op_blocked or w_op_blocked) and e_op_blocked != w_op_blocked) or \
                (w_op_count + e_nn_op_count + 1 >= 3 and not w_op_blocked and not e_nn_op_blocked or e_nn_op_count + w_op_count + 1 >= 4 and (e_nn_op_blocked or w_op_blocked) and e_nn_op_blocked != w_op_blocked) or \
                (w_nn_op_count + e_op_count + 1 >= 3 and not w_nn_op_blocked and not e_op_blocked or e_op_count + w_nn_op_count + 1 >= 4 and (e_op_blocked or w_nn_op_blocked) and e_op_blocked != w_nn_op_blocked) or \
                (w_np_op_count + e_np_op_count + 1 >= 3 and not w_np_op_blocked and not e_np_op_blocked or e_np_op_count + w_np_op_count + 1 >= 4 and (e_np_op_blocked or w_np_op_blocked) and e_np_op_blocked != w_np_op_blocked))) or \
                (((ne_op_count + sw_op_count + 1 >= 3 and not ne_op_blocked and not sw_op_blocked or ne_op_count + sw_op_count + 1 >= 4 and (ne_op_blocked or sw_op_blocked) and ne_op_blocked != sw_op_blocked) or \
                (ne_op_count + sw_nn_op_count + 1 >= 3 and not ne_op_blocked and not sw_nn_op_blocked or ne_op_count + sw_nn_op_count + 1 >= 4 and (ne_op_blocked or sw_nn_op_blocked) and ne_op_blocked != sw_nn_op_blocked) or \
                (ne_nn_op_count + sw_op_count + 1 >= 3 and not ne_nn_op_blocked and not sw_op_blocked or ne_nn_op_count + sw_op_count + 1 >= 4 and (ne_nn_op_blocked or sw_op_blocked) and ne_nn_op_blocked != sw_op_blocked) or \
                (ne_np_op_count + sw_np_op_count + 1 >= 3 and not ne_np_op_blocked and not sw_np_op_blocked or ne_np_op_count + sw_np_op_count + 1 >= 4 and (ne_np_op_blocked or sw_np_op_blocked) and ne_np_op_blocked != sw_np_op_blocked)) and \
                ((nw_op_count + se_op_count + 1 >= 3 and not nw_op_blocked and not se_op_blocked or se_op_count + nw_op_count + 1 >= 4 and (se_op_blocked or nw_op_blocked) and se_op_blocked != nw_op_blocked) or \
                (nw_op_count + se_nn_op_count + 1 >= 3 and not nw_op_blocked and not se_nn_op_blocked or se_nn_op_count + nw_op_count + 1 >= 4 and (se_nn_op_blocked or nw_op_blocked) and se_nn_op_blocked != nw_op_blocked) or \
                (nw_nn_op_count + se_op_count + 1 >= 3 and not nw_nn_op_blocked and not se_op_blocked or se_op_count + nw_nn_op_count + 1 >= 4 and (se_op_blocked or nw_nn_op_blocked) and se_op_blocked != nw_nn_op_blocked) or \
                (nw_np_op_count + se_np_op_count + 1 >= 3 and not nw_np_op_blocked and not se_np_op_blocked or se_np_op_count + nw_np_op_count + 1 >= 4 and (se_np_op_blocked or nw_np_op_blocked) and se_np_op_blocked != nw_np_op_blocked))):
                option_dict[option] += 50000
            # block four, better than form three and double threes
            elif (n_op_count + s_op_count + 1 == 4 and not n_op_blocked and not s_op_blocked) or (e_op_count + w_op_count + 1 == 4 and not e_op_blocked and not w_op_blocked) or \
                (se_op_count + nw_op_count + 1 == 4 and not se_op_blocked and not nw_op_blocked) or (ne_op_count + sw_op_count + 1 == 4 and not ne_op_blocked and not sw_op_blocked):
                option_dict[option] += 30000
            # block three, not urgent than unblocked three and form unblocked two
            elif (n_op_count + s_op_count + 1 == 3 and not n_op_blocked and not s_op_blocked) or (e_op_count + w_op_count + 1 == 3 and not e_op_blocked and not w_op_blocked) or \
                (se_op_count + nw_op_count + 1 == 3 and not se_op_blocked and not nw_op_blocked) or (ne_op_count + sw_op_count + 1 == 3 and not ne_op_blocked and not sw_op_blocked):
                option_dict[option] += 50
            # block double twos, not urgent then unblocked double twos and unblocked two
            elif (((n_op_count >= 1 and not n_op_blocked and not s_op_blocked) or (s_op_count >= 1 and not s_op_blocked and not n_op_blocked) or (e_op_count >= 1 and not e_op_blocked and not w_op_blocked) or (w_op_count >= 1 and not w_op_blocked and not e_op_blocked)) and \
                ((ne_op_count >= 1 and not ne_op_blocked and not sw_op_blocked) or (nw_op_count >= 1 and not nw_op_blocked and not se_op_blocked) or (se_op_count >= 1 and not se_op_blocked and not nw_op_blocked) or (sw_op_count >= 1 and not sw_op_blocked and not ne_op_blocked) )) or \
                (((n_op_count >= 1 and not n_op_blocked and not s_op_blocked) or (s_op_count >= 1 and not s_op_blocked and not n_op_blocked)) and ((e_op_count >= 1 and not e_op_blocked and not w_op_blocked) or (w_op_count >= 1 and not w_op_blocked and not e_op_blocked))) or \
                (((nw_op_count >= 1 and not nw_op_blocked and not se_op_blocked) or (se_op_count >= 1 and not se_op_blocked and not nw_op_blocked)) and ((ne_op_count >= 1 and not ne_op_blocked and not sw_op_blocked) or (sw_op_count >= 1 and not sw_op_blocked and not ne_op_blocked) )):
                option_dict[option] += 30
            # block two, not urgent then form a two, better than free one
            elif (n_op_count + s_op_count + 1 == 2 and not n_op_blocked and not s_op_blocked) or (e_op_count + w_op_count + 1 == 2 and not e_op_blocked and not w_op_blocked) or \
                (se_op_count + nw_op_count + 1 == 2 and not se_op_blocked and not nw_op_blocked) or (ne_op_count + sw_op_count + 1 == 2 and not ne_op_blocked and not sw_op_blocked):
                option_dict[option] += 15
            else:
                option_dict[option] += 0
            
        return option_dict

    def make_move(self):
        moves = self.get_moves()
        sort_moves = sorted(moves.iteritems(), key=lambda x: x[1], reverse=True)
        return sort_moves[0]

class MCTS:
    def __init__(self, grid, player):
        self.root_state = State(grid, player)

    def uct_search(self):
        t0 = time.time()
        while (time.time()-t0 <= 3):
            node_expand = self.tree_policy(self.root_state)
            expand_root = self.default_policy(node_expand)
            self.backup(node_expand, expand_root)
        return self.best_child(self.root_state, 0).pre_move

    def tree_policy(self, state):
        #print("selection")
        curr = state
        while not curr.terminal_state():
            if not curr.full_expand():
                return self.expand(curr)
            else:
                curr = self.best_child(curr, 2)
        return curr

    def expand(self, state):
        #print("expand")
        action, value = state.make_move()
        player = '.'
        new_grid = copy.deepcopy(state.grid)
        if state.player == 'b':
            player = 'w'
            new_grid[action[0]][action[1]] = 'b'
        else:
            player = 'b'
            new_grid[action[0]][action[1]] = 'w'
        child = State(new_grid, player)
        child.pre_move = action
        child.parent = state
        state.children.append(child)
        return child

    def best_child(self, state, c):
        rewards = []
        for child in state.children:
            reward = float(child.reward[0])/float(child.reward[1]) + c*sqrt( 2*log(len(state.reward[1]))/float(child.reward[1]))
            rewards.append(reward) 
        return state.children[np.argmax(rewards)]

    def default_policy(self, state):
        #print("simulate game")
        curr = copy.deepcopy(state)
        while not curr.terminal_state():
            action, value = curr.make_move()
            if curr.player == 'w':
                curr.player = 'b'
                curr.grid[action[0]][action[1]] = 'w'
                curr.pre_move = action
            else:
                curr.player = 'w'
                curr.grid[action[0]][action[1]] = 'b'
                curr.pre_move = action
        return curr.player

    def backup(self, node_expand, expand_root):
        #print("backing up")
        curr = node_expand
        while curr:
            curr.reward[1] += 1
            if curr.player == expand_root:
                curr.reward[0] += 0
            else:
                curr.reward[0] += 1
            curr = curr.parent