from __future__ import print_function
#Use priority queues from Python libraries, don't waste time implementing your own
#Check https://docs.python.org/2/library/heapq.html
from heapq import *
import math
                       
class Agent:
    def __init__(self, grid, start, goal, type):
        self.actions = [(0,-1),(-1,0),(0,1),(1,0)]
        self.grid = grid
        self.came_from = {}
        self.checked = []
        self.start = start
        self.grid.nodes[start[0]][start[1]].start = True
        self.goal = goal
        self.grid.nodes[goal[0]][goal[1]].goal = True
        self.g_cost = {}
        self.f_cost = {}
        self.new_plan(type)
    def new_plan(self, type):
        self.finished = False
        self.failed = False
        self.type = type
        if self.goal == self.start:
            self.finished = True
            print("final cost: ", 0)
            return
        if self.type == "dfs" :
            self.frontier = [self.start]
            self.checked = []
        elif self.type == "bfs":
            self.frontier = [self.start]
            self.checked = []
        elif self.type == "ucs":
            self.frontier = []
            heappush(self.frontier, (0, self.start))
            self.checked = []
            self.g_cost[self.start] = 0
        elif self.type == "astar":
            self.frontier = []
            heappush(self.frontier, (0 + self.heuristic_function(self.start), self.start))
            self.checked = []
            self.g_cost[self.start] = 0
            self.f_cost[self.start] = 0 + self.heuristic_function(self.start)
    def show_result(self):
        current = self.goal
        while not current == self.start:
            current = self.came_from[current]
            self.grid.nodes[current[0]][current[1]].in_path = True
    def make_step(self):
        if self.type == "dfs":
            self.dfs_step()
        elif self.type == "bfs":
            self.bfs_step()
        elif self.type == "ucs":
            self.ucs_step()
        elif self.type == "astar":
            self.astar_step()
    def dfs_step(self):
        #check if frontier is empty
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.pop()
        print("popped: ", current)
        #mark current node as checked
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)
        #for each child, explore
        for i, j in self.actions:
            #position for nextstep
            nextstep = (current[0]+i, current[1]+j)
            #check to avoid repetition
            if nextstep in self.checked or nextstep in self.frontier:
                print("expanded before: ", nextstep)
                continue
            #check if nextstep is within the grid
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    #check if nextstep is puddle
                    if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                        if nextstep == self.goal:
                            self.finished = True
                        #append nextstep to frontier
                        self.frontier.append(nextstep)
                        #set nextstep frontier to true
                        self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                        #update previous pointer
                        self.came_from[nextstep] = current
                        print("pushed: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of column range: ", nextstep)
            else:
                print("out of row range: ", nextstep)
    def bfs_step(self):
        #check if frontier is empty
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.pop(0)
        print("popped: ", current)
        #mark current node as checked
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)
        #for each child, explore
        for i, j in self.actions:
            #position for nextstep
            nextstep = (current[0]+i, current[1]+j)
            #check to avoid repetition
            if nextstep in self.checked or nextstep in self.frontier:
                print("expanded before: ", nextstep)
                continue
            #check if nextstep is within the grid
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    #check if nextstep is puddle
                    if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                        if nextstep == self.goal:
                            self.finished = True
                        #append nextstep to frontier
                        self.frontier.append(nextstep)
                        #set nextstep frontier to true
                        self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                        #update previous pointer
                        self.came_from[nextstep] = current
                        print("pushed: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of column range: ", nextstep)
            else:
                print("out of row range: ", nextstep)
    def ucs_step(self):
        #check if frontier is empty
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current_cost, current = heappop(self.frontier)
        print("popped: ", current)
        print("cost: ", current_cost)
        #mark current node as checked
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)
        #for each child, explore
        for i, j in self.actions:
            #position for nextstep
            nextstep = (current[0]+i, current[1]+j)
            #check if nextstep is within the grid
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    #check to avoid repetition
                    if nextstep in self.checked or self.grid.nodes[nextstep[0]][nextstep[1]].frontier == True:
                        print("expanded before: ", nextstep)
                        continue
                    #check if nextstep is puddle
                    if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                        total_cost = current_cost + self.grid.nodes[nextstep[0]][nextstep[1]].cost()
                        if nextstep == self.goal:
                            self.finished = True
                            print("final cost: ", total_cost)
                            self.came_from[nextstep] = current
                            return
                        #push nextstep and total cost to frontier
                        heappush(self.frontier, (total_cost, nextstep))
                        self.g_cost[nextstep] = total_cost
                        #set nextstep frontier to true
                        self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                        #update previous pointer
                        self.came_from[nextstep] = current
                        print("pushed: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of column range: ", nextstep)
            else:
                print("out of row range: ", nextstep)
    def astar_step(self):
        #check if frontier is empty
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current_f_cost, current = heappop(self.frontier)
        print("popped: ", current)
        print("cost: ", current_f_cost)
        #mark current node as checked
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)
        #for each child, explore
        for i, j in self.actions:
            #position for nextstep
            nextstep = (current[0]+i, current[1]+j)
            #check if nextstep is within the grid
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    #check to avoid repetition
                    if nextstep in self.checked or self.grid.nodes[nextstep[0]][nextstep[1]].frontier == True:
                        print("expanded before: ", nextstep)
                        continue
                    #check if nextstep is puddle
                    if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                        #calculate g cost
                        next_g_cost = self.g_cost[current]+self.grid.nodes[nextstep[0]][nextstep[1]].cost()
                        #calculate g cost and heuristic cost
                        next_f_cost = next_g_cost + self.heuristic_function(nextstep)
                        if nextstep == self.goal:
                            self.finished = True
                            print("final cost: ", next_f_cost)
                            self.came_from[nextstep] = current
                            return
                        #push nextstep and total f cost to frontier
                        heappush(self.frontier, (next_f_cost, nextstep))
                        self.g_cost[nextstep] = next_g_cost
                        #set nextstep frontier to true
                        self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                        #update previous pointer
                        self.came_from[nextstep] = current
                        print("pushed: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of column range: ", nextstep)
            else:
                print("out of row range: ", nextstep)
    def heuristic_function(self, node):
        return 2*(math.fabs(node[0] - self.goal[0]) + math.fabs(node[1] - self.goal[1]))
