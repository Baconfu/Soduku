#auto sudoku

import tkinter
import time

r1 = [0,0,0,0,1,0,0,0,0]
r2 = [0,0,0,7,0,0,0,0,2]
r3 = [0,7,0,9,0,0,5,1,0]
r4 = [0,2,0,0,0,9,0,0,0]
r5 = [0,3,1,0,0,0,0,4,0]
r6 = [0,0,9,8,0,0,0,7,0]
r7 = [4,0,0,0,5,0,0,0,3]
r8 = [0,0,8,0,0,6,0,0,0]
r9 = [0,0,0,0,0,4,0,6,9]
"""
r1 = [5,0,0,0,0,2,8,0,0]
r2 = [0,0,0,0,0,7,0,0,4]
r3 = [0,0,6,5,4,0,3,0,0]
r4 = [7,0,0,8,9,0,0,0,3]
r5 = [0,1,0,0,0,0,6,0,0]
r6 = [0,0,0,0,0,4,0,0,0]
r7 = [8,0,0,3,5,0,0,0,9]
r8 = [0,0,7,0,0,0,0,8,0]
r9 = [0,0,0,2,0,0,0,0,0]
"""

class Cell:
    def __init__(self,value):
        self.position = (0,0)
        self.possible = []
        self.impossible = []
        self.value = value
        self.assumption_level = 0
        self.marking = []
        self.error = False
class Grid:
    def __init__(self,grid,main):
        self.main = main
        
        self.grid = [[0 for i in range(9)] for j in range(9)]
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                c = Cell(grid[y][x])
                c.position = (x,y)
                self.grid[y][x] = c
        
        self.assumption_record = []

        self.filling = True
        self.contradicted = False
        self.calculate_possible()
    def iterate(self):
        if self.contradicted:
            self.rollback()
            self.calculate_possible()
            self.contradicted = False
            return

        if self.filling:
            self.calculate_possible()
            if not self.is_contradiction():
                self.filling = self.fill_certain()
                self.calculate_possible()
                self.update_markings()
                return
            else:
                self.filling = False
        if self.is_contradiction():
            self.contradicted = True
            
        else:
            self.make_assumption()
            self.update_markings()
            self.filling = True

        return False
    
    def rollback(self):
        for y in range(9):
            for x in range(9):
                cell = self.grid[y][x]
                if len(cell.possible) == 0 and cell.value == 0:
                    cell.value = 0
                    cell.impossible = []
                    cell.assumption_level = 0
        
        last_assumption = self.assumption_record[-1]
        assumed_cell = self.grid[last_assumption[1]][last_assumption[0]]
        assumed_cell.impossible.append(assumed_cell.value)
        assumed_cell.value = 0
        assumption_level = len(self.assumption_record)
        for y in range(9):
            for x in range(9):
                cell = self.grid[y][x]
                if cell.value == 0:
                    continue
                        
                if cell.assumption_level >= assumption_level:
                    cell.value = 0
                    cell.impossible = []
                    cell.assumption_level = 0
        self.assumption_record.pop(-1)

        
    def make_assumption(self):
        cells = []
        for y in range(9):
            for x in range(9):
                cell = self.grid[y][x]
                if cell.value != 0: continue
                cells.append(self.grid[y][x])
        
        if len(cells) == 0:
            for y in range(9):
                row = ""
                for x in range(9):
                    cell = self.grid[y][x]
                    row += str(cell.value) + " "
                print(row)
        options = [(len(cell.possible),cell.position[0],cell.position[1]) for cell in cells]
        options = sorted(options)
        
        cell = self.grid[options[0][2]][options[0][1]]
        pset = cell.possible
        pset = [(self.is_unique(cell.position[0],cell.position[1],pset[i]),pset[i]) for i in range(len(pset))]
        pset = sorted(pset)
        possibility = pset[0][1]
        cell.value = possibility
        
        self.assumption_record.append((cell.position[0],cell.position[1],possibility))
        cell.assumption_level = len(self.assumption_record)
        
    def is_contradiction(self):
        for y in range(9):
            for x in range(9):
                cell = self.grid[y][x]
                if cell.value != 0:
                    continue
                if len(cell.possible) == 0:
                    cell.error = True
                    return True
                certain_count = 0
                for n in cell.possible:
                    duplicates = self.is_unique(x,y,n)
                    if duplicates == 0:
                        certain_count += 1
                if certain_count > 1:
                    cell.error = True
                    return True
        return False
    def clear_errors(self):
        for y in range(9):
            for x in range(9):
                cell = self.grid[y][x]
                if cell.error:
                    cell.error = False
    
    def calculate_possible(self):
        for y in range(9):
            row = self.grid[y]
            for x in range(9):
                cell = row[x]
                if cell.value == 0:
                    cell.possible = self.get_possible(x,y)
                else:
                    cell.possible = []

        for y in range(9):
            for x in range(9):
                cell = self.grid[y][x]
                for n in cell.impossible:
                    if n in cell.possible:
                        cell.possible.remove(n)
                    
        for y in range(9):
            row_mem = []
            for x in range(9):
                cell = self.grid[y][x]
                if cell.value == 0:
                    row_mem.append(cell.possible)
            while len(row_mem)>0:
                pset = row_mem[0][:]
                count = row_mem.count(pset)
                if count == len(pset):
                    for x in range(9):
                        cell = self.grid[y][x]
                        if cell.possible == pset:
                            continue
                        for i in range(len(pset)):
                            if pset[i] in cell.possible: 
                                cell.possible.remove(pset[i])

                while pset in row_mem:
                    row_mem.remove(pset)
        for x in range(9):
            col_mem = []
            for y in range(9):
                cell = self.grid[y][x]
                if cell.value == 0:
                    col_mem.append(cell.possible)
            while len(col_mem)>0:
                pset = col_mem[0][:]
                if pset == [1,5]: flag = True
                count = col_mem.count(pset)
                if count == len(pset):
                    for y in range(9):
                        cell = self.grid[y][x]
                        if cell.possible == pset:
                            continue
                        for i in range(len(pset)):
                            if pset[i] in cell.possible: 
                                cell.possible.remove(pset[i])

                while pset in col_mem:
                    col_mem.remove(pset)
        for by in range(3):
            for bx in range(3):
                box_mem = []
                for y in range(3):
                    for x in range(3):
                        cell = self.grid[by*3 + y][bx*3 + x]
                        if cell.value == 0:
                            box_mem.append(cell.possible)
                while len(box_mem) > 0:
                    pset = box_mem[0][:]
                    count = col_mem.count(pset)
                    if count == len(pset):
                        for y in range(3):
                            for x in range(3):
                                cell = self.grid[by*3 + y][bx*3 + x]
                                if cell.possible == pset:
                                    continue
                                for i in range(len(pset)):
                                    if pset[i] in cell.possible:
                                        cell.possible.remove(pset[i])

                    while pset in box_mem:
                        box_mem.remove(pset)
    def fill_certain(self):
        for y in range(9):
            for x in range(9):
                cell = self.grid[y][x]
                if cell.value != 0:
                    continue
                possible_count = len(cell.possible)
                if possible_count == 1:
                    cell.value = cell.possible[0]
                    cell.assumption_level = len(self.assumption_record)
                    return True
                for n in cell.possible:
                    
                    duplicates = self.is_unique(x,y,n)
                    if duplicates == 0:
                        cell.value = n
                        cell.assumption_level = len(self.assumption_record)
                        return True
        
        return False
                    
    def update_markings(self):
        for y in range(9):
            for x in range(9):
                cell = self.grid[y][x]
                if cell.value != 0:
                    cell.marking = []
                else:
                    cell.marking = []
                    if len(cell.possible) == 2:
                        cell.marking = cell.possible[:]
                    for n in cell.possible:
                        b = self.is_unique(x,y,n)
                        if b == 1 and not n in cell.marking:
                            cell.marking.append(n)
                        
        
                        
    def is_unique(self,x,y,n):
        flag = False
        if x == 6 and y == 5 and n == 2:
            flag = True
            #print(self.grid[y][x].possible)
        row_duplicates = 0
        for i in range(9):
            if i!=x:
                #if flag: print(self.grid[y][i].possible)
                if n in self.grid[y][i].possible:
                    row_duplicates += 1
                    if row_duplicates > 1:
                        break

        if row_duplicates == 0: return 0
        
        column_duplicates = 0
        for i in range(9):
            if i!=y:
                if n in self.grid[i][x].possible:
                    column_duplicates += 1
                    if column_duplicates > 1:
                        break
        if column_duplicates == 0: return 0
        
        box_duplicates = 0
        for i in range((y//3) * 3, (y//3 + 1) * 3):
            for j in range((x//3) * 3,(x//3 + 1) * 3):
                if i!=y or j!=x:
                    
                    cell = self.grid[i][j]
                    #if flag: print(cell.possible,"cell:",cell.value)
                    if n in cell.possible:
                        box_duplicates += 1
                        if box_duplicates > 1:
                            break
            if box_duplicates > 1: break
        #if flag: print(box_duplicates)
        
        if box_duplicates == 0: return 0
        
        if row_duplicates == 1 or column_duplicates == 1 or box_duplicates == 1:
            return 1
        else:
            return 2
    def get_possible(self,x,y):
        possible = [i for i in range(1,10)]

        for i in range(0,9):
            if i != x:
                num = self.grid[y][i].value
                if num in possible:
                    possible.remove(num)
               
            if i != y:
                num2 = self.grid[i][x].value
                if num2 in possible:
                    possible.remove(num2)
               
            

        for i in range((y//3) * 3, (y//3 + 1) * 3):
            for j in range((x//3) * 3,(x//3 + 1) * 3):
                num = self.grid[i][j].value
                if num in possible:
                    possible.remove(num)
        return possible
    def check_completion(self):
        for y in range(9):
            for x in range(9):
                if self.grid[y][x].value == 0:
                    return False
        return True

class Board:
    def __init__(self):
        root = tkinter.Tk()
        root.minsize(width=600,height=600)

        
        
        self.grid = Grid([r1,r2,r3,r4,r5,r6,r7,r8,r9],self)
        self.display = tkinter.Canvas(root,width=600,height=600)
        self.display.place(x=0,y=0)
        for i in range(0,9):
            if i%3 == 0:
                self.display.create_line(75,75 + i*50,525,75 + i*50,width=2,tags="bg")
                self.display.create_line(75 + i*50,75,75 + i*50,525,width=2,tags="bg")
            else:
                self.display.create_line(75,75 + i*50,525,75 + i*50,width=1,fill="grey",tags="bg")
                self.display.create_line(75 + i*50,75,75 + i*50,525,width=1,fill="grey",tags="bg")
            self.display.create_line(75,525,525,525,width=2,tags="bg")
            self.display.create_line(525,75,525,525,width=2,tags="bg")   

        self.next_step = tkinter.Button(root,text = "Next",command = self.next)
        self.next_step.place(x=300,y=540)

        self.root = root
        self.generate_grid(self.grid)

        #self.run()

        
    def generate_grid(self,grid_object):
        self.display.delete("num")
        self.display.delete("mark")
        grid = grid_object.grid
        for i in range(len(grid)):
            row = grid[i]
            for j in range(len(row)):
                cell = row[j]
                if cell.error:
                    self.display.create_rectangle(50*j + 75,50*i + 75,50*(j+1) + 75,50*(i+1) + 75,fill="red",tags="num")
                    continue
                if cell.value != 0:
                    if cell.assumption_level > 0:
                        col = "blue"
                    else:
                        col = "black"
                    self.display.create_text(50 * j + 100,50 * i + 97,text = str(cell.value),font = ('Segoe UI','24'),fill=col,tags="num")
                else:
                    for z in range(len(cell.marking)):
                        marking = cell.marking[z] - 1
                        self.display.create_text(50 * j + 88 + (marking%3) * 13,50 * i + 87 + (marking//3) * 13,text = str(marking+1),font = ('Segoe UI','10'),tags = "mark")
        self.display.update()
    def next(self):
        self.grid.clear_errors()
        result = self.grid.iterate()
            
        self.grid.update_markings()
        self.generate_grid(self.grid)
    def run(self):
        count = 0
        while True:
            result = self.grid.iterate()
            
            self.grid.update_markings()
            self.generate_grid(self.grid)
            if self.grid.check_completion():
                break
            time.sleep(1)
            self.grid.clear_errors()
            count+=1
            if count > 2000: break
            #if result == False: break
            

board = Board()
