# Yikai Wang
from copy import deepcopy
import sys

# Given filename, opens the file and returns cells of the puzzle
def parse(input):
    cells = []
    i = 0
    with open(input, "r") as f:
        for line in f.readlines():
            # Gets the first 9 lines
            if i < 9:
                cells.append([ int(i) for i in line.split() ])
                i += 1
    return cells

# A cell contains the number, the row and column number, block number, and most importantly the domain
class Cell:
    def __init__(self, num, row, col, blocknum):
        self.num = num
        self.row = row
        self.col = col
        self.block = blocknum
        self.domain = [ i for i in range(1, 9 + 1) ] if num == 0 else [ num ]

class Sudoku:
    def __init__(self, cells):
        self.failure = False

        # Sudoku contains a list of cells
        self.cells = []

        # Cells that are yet to have a number assigned to them
        self.unassigned = []

        # Cells that are given a number at the start (already filled in)
        self.given = []

        # A dictionary is used for cell blocks so it is easier to obtain all the cells in the block
        self.blocks = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[] }

        # Fills the list with cells
        for r in range(len(cells)):
            cell_row = []
            for c in range(len(cells[r])):
                blocknum = 0
                # Determine which block the cell belongs
                if r < 3:
                    if c < 3:
                        blocknum = 1
                    elif c < 6:
                        blocknum = 2
                    else:
                        blocknum = 3
                elif r < 6:
                    if c < 3:
                        blocknum = 4
                    elif c < 6:
                        blocknum = 5
                    else:
                        blocknum = 6
                else:
                    if c < 3:
                        blocknum = 7
                    elif c < 6:
                        blocknum = 8
                    else:
                        blocknum = 9
                # Creates the appropriate cell
                cell = Cell(cells[r][c], r, c, blocknum)
                cell_row.append(cell)
                # If the cell num is 0 initially, then it's unassigned
                if cell.num == 0:
                    self.unassigned.append(cell)
                else:
                    self.given.append(cell)
                self.blocks[blocknum].append(cell)

            self.cells.append(cell_row)

        # Reduces the domain of unassigned in the beginning
        for i in range(len(self.given)):
            if not self.forward_check(self.given[i]):
                self.failure = True
                return

    # Forward checking algo
    def forward_check(self, cell):
        #Row checking
        for c in range(len(self.cells[cell.row])):
            if self.cells[cell.row][c] is not cell:
                # Removes the value from the domain
                if cell.num in self.cells[cell.row][c].domain:
                    self.cells[cell.row][c].domain.remove(cell.num)
                # If the cell does not have any values left in domain, the solution is invalid
                if len(self.cells[cell.row][c].domain) < 1:
                    return False

        #Column checking
        for r in range(len(self.cells)):
            if self.cells[r][cell.col] is not cell:
                # Removes the value from the domain
                if cell.num in self.cells[r][cell.col].domain:
                    self.cells[r][cell.col].domain.remove(cell.num)
                # If the cell does not have any values left in domain, the solution is invalid
                if len(self.cells[r][cell.col].domain) < 1:
                    return False

        #Block checking
        for i in range(len(self.blocks[cell.block])):
            if self.blocks[cell.block][i] is not cell:
                # Removes the value from the domain
                if cell.num in self.blocks[cell.block][i].domain:
                    self.blocks[cell.block][i].domain.remove(cell.num)
                # If the cell does not have any values left in domain, the solution is invalid
                if len(self.blocks[cell.block][i].domain) < 1:
                    return False

        return True

    # Checks if the value is consistent
    def consistent(self, cell, value):
        #Row checking
        for c in range(len(self.cells[cell.row])):
            # No two cells in the same row can share the same number
            if self.cells[cell.row][c] is not cell:
                if value == self.cells[cell.row][c].num:
                    return False

        #Column checking
        for r in range(len(self.cells)):
            # No two cells in the same column can share the same number
            if self.cells[r][cell.col] is not cell:
                if value == self.cells[r][cell.col].num:
                    return False

        #Block checking
        for i in range(len(self.blocks[cell.block])):
            # No two cells in the same block can share the same number
            if self.blocks[cell.block][i] is not cell:
                if value == self.blocks[cell.block][i].num:
                    return False

        return True

    def undo_assign(self, cell, value):
        cell.num = 0
        self.unassigned.append(cell)

        #Undo edits to row's domain
        for c in range(len(self.cells[cell.row])):
            if self.cells[cell.row][c] is not cell:
                if value not in self.cells[cell.row][c].domain:
                    self.cells[cell.row][c].domain.append(value)

        #Undo edits to column's domain
        for r in range(len(self.cells)):
            if self.cells[r][cell.col] is not cell:
                if value not in self.cells[r][cell.col].domain:
                    self.cells[r][cell.col].domain.append(value)

        #Undo edits to block's domain
        for i in range(len(self.blocks[cell.block])):
            if self.blocks[cell.block][i] is not cell:
                if value not in self.blocks[cell.block][i].domain:
                    self.blocks[cell.block][i].domain.append(value)

    # Degree heuristic function: checks the number of unassigned neighbors
    def num_unassigned_neighbors(self, cell):
        num = 0
        #Tally up num of unassigned neighbors
        # In the row
        for c in range(len(self.cells[cell.row])):
            if self.cells[cell.row][c] is not cell and self.cells[cell.row][c].num == 0:
                num += 1
        # In the column
        for r in range(len(self.cells)):
            if self.cells[r][cell.col] is not cell and self.cells[r][cell.col].num == 0:
                num += 1
        # In the block
        for i in range(len(self.blocks[cell.block])):
            # Extra check at the end to see if the row and column is not the same to avoid double counting
            if self.blocks[cell.block][i] is not cell and self.blocks[cell.block][i].num == 0 and self.blocks[cell.block][i].row != cell.row and self.blocks[cell.block][i].col != cell.col:
                num += 1
        return num

    def MRV(self):
        mrv = self.unassigned[0]
        domain_length = len(mrv.domain)

        # For all of the variables in the unassigned, check if there is a variable with a smaller domain
        for i in range(1, len(self.unassigned)):
            if len(self.unassigned[i].domain) < domain_length:
                mrv = self.unassigned[i]
                domain_length = len(mrv.domain)
            # If there is a tie, use degree heuristic (see which has more unassigned neighbors)
            elif len(self.unassigned[i].domain) == domain_length:
                mrv_num_unassigned = self.num_unassigned_neighbors(mrv)
                other_cell_num_unassigned = self.num_unassigned_neighbors(self.unassigned[i])
                mrv = mrv if mrv_num_unassigned > other_cell_num_unassigned else self.unassigned[i]
                domain_length = len(mrv.domain)
        return mrv

    def backtracking_search(self):
        # If there is a possible solution, find it
        if not self.failure:
            if self.backtrack():
                return True
            self.failure = True
        return False

    def backtrack(self):
        # If no variables left to assign, we are done
        if len(self.unassigned) == 0:
            return True

        # Pick the cell with minimum remaining values
        cell = self.MRV()
        # Create a copy of the domain (actual domain will get modified as we go deeper in the search)
        domain = deepcopy(cell.domain)
        # Order from lowest to largest value
        domain.sort()
        # See if the values in domain gives solution
        for value in domain:
            # If the value is consistent
            if self.consistent(cell, value):
                # Assign the cell the value
                cell.num = value
                self.unassigned.remove(cell)
                # Apply forward checking again to detect early failures
                if self.forward_check(cell):
                    # Apply backtrack again on next cell
                    if self.backtrack():
                        # If successful, return true
                        return True
                # Otherwise, unassign the value and undo any edits made to other cell's domain
                self.undo_assign(cell, value)
        # Return failure if solution not found
        return False

    # String representation of the puzzle
    def __str__(self):
        list_s = []
        for row in self.cells:
            s_row = []
            for cell in row:
                s_row.append(str(cell.num))
            list_s.append(" ".join(s_row) + "\n")
        return "".join(list_s)

def main(user_input):
    sudoku = Sudoku(parse(user_input))
    # If the puzzle can't be solved right from the start
    if sudoku.failure:
        print("This puzzle does not have a solution.")
        return None
    # Otherwise try to find a solution
    if sudoku.backtracking_search():
        print("Solution:\n")
        s = str(sudoku)
        print(s)
        return s
    print("This puzzle does not have a solution.")
    return None

user_input = []
if len(sys.argv) < 2:
    user_input = (input("Please enter the name of input file:\n"))
else:
    user_input = (sys.argv[1])

output = main(user_input)
# If there is a solution, write the solution to a file
if output is not None:
    # Given name of the input file, create the correct filename of output file
    filename = user_input.split(".")
    if "input" in filename[0].lower():
        name = filename[0].lower().split("input")
        num = name[1]
        filename[0] = name[0].upper() + "Output" + num
    else:
        filename[0] += "_output"
    open(".".join(filename), "w").write(output)
