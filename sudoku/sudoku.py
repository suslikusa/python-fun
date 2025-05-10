#!/usr/bin/python3 -u

import random
import re
import sys
import time

grid_string_re = re.compile("^[1-9.]{9}$")

class UnsolvableGridError(Exception):
    pass

class InvalidGridError(Exception):
    pass

def gridStringToLines(grid_string):
    """ Convert a simple string for 9x9 sudoku to lines """
    lines = []
    for line in grid_string.split("\n"):
        line.strip()
        if len(line) <= 0:
            continue
        if grid_string_re.match(line) is None:
            raise IOError("Bad grid string: '%s'" % line)
        lines.append(list(line))
    return lines

class Sudoku:
    
    def __init__(self,grid_desc,verbose=False):
        self.lines = []
        self.verbose = verbose
        if type(grid_desc) == type("foo"):
            self.lines = gridStringToLines(grid_desc)
        elif type(grid_desc) == type([]):
            self.lines = [ x[:] for x in grid_desc ] 
        if len(self.lines) != 9:
            raise IOError("Found %d grid rows, not 9" % len(self.lines))
        self.cardinal = 9  # 9 x 9 grid, 3 x 3 squares, numbers 1-9
        self.cardinal_root = 3
        self.original_lines = self.lines[:]
        self.compute_groups()
        if not self.is_valid():
            raise InvalidGridError("Input grid is invalid")

    def __str__(self):
        counter = 0
        ans = ''
        for l in self.lines:
            if counter % self.cardinal_root == 0:
                ans += "  +"
                for i in range(0, self.cardinal_root):
                    ans += "-------+"
                ans += "\n"
            ans += "%d |" % counter
            for i in range(0, self.cardinal_root):
                offset = self.cardinal_root * i
                ans += " %s %s %s |" % (l[offset], l[offset+1], l[offset+2])
            ans +=" \n"
            counter += 1
        ans += "  +"
        for i in range(0, self.cardinal_root):
            ans += "-------+"
        ans += "\n"
        ans += "    0 1 2 | 3 4 5 | 6 7 8\n"
        return ans

    def state_copy(self):
        """ Copy of the critical state """
        return [ l[:] for l in self.lines ]

    def square_from_rowcol(self, row_idx, col_idx):
        """ Which square number does a given row and
        column correspond to? """
        # Work out what square we are in in.
        # For 3 x 3 squares:
        # 0 is top left, 2 is top right,
        # 6 is bottom left, 9 is bottom right
        square_col = int(col_idx / self.cardinal_root)
        square_row = int(row_idx / self.cardinal_root)
        return square_col + (self.cardinal_root * square_row)
        
    def compute_groups(self):
        """ Compile the set of known numbers in rows, columns and squares.
        Does not include unknown values. """
        self.row_nums = []
        self.col_nums = [ set() for i in range(0, self.cardinal) ]
        self.square_nums = [ set() for i in range(0, self.cardinal) ]
        self.empty_cells = []  # row, col, sq
        row_idx = 0
        for l in self.lines:
            ns = [ int(c) for c in l if not c == '.' ]
            self.row_nums.append(set(ns))
            for col_idx in range(0, self.cardinal):
                square_idx = self.square_from_rowcol(row_idx, col_idx)
                try:
                    n = int(l[col_idx])
                except ValueError:
                    # Don't know what this number is yet
                    self.empty_cells.append( (row_idx, col_idx, square_idx) )
                    continue
                self.col_nums[col_idx].add(n)
                self.square_nums[square_idx].add(n)
            row_idx += 1
        # Compute empty squares in rows, cols, idx
        self.row_missing = [ 0 for i in range(0, self.cardinal) ]
        self.col_missing = [ 0 for i in range(0, self.cardinal) ]
        self.square_missing = [ 0 for i in range(0, self.cardinal) ]
        for (r,c,s) in self.empty_cells:
            self.row_missing[r] += 1
            self.col_missing[c] += 1
            self.square_missing[s] += 1

    def start_solving(self):
        self.search_backtracks = []
        self.next_guess = None

    def has_backtracks(self):
        return len(self.search_backtracks) > 0

    def backtrack(self):
        # Pop off last backtrack + guess
        (state, guess_list) = self.search_backtracks[-1]
        self.next_guess = guess_list[0]
        if len(guess_list) > 1:
            self.search_backtracks[-1] = (state, guess_list[1:])
        else:
            self.search_backtracks = self.search_backtracks[0:-1]
        # Restore state to last backtrack point, try again
        if self.verbose:
            print("Restoring state from:")
            print(self)
        self.lines = state
        self.compute_groups()
        if self.verbose:
            print(self)
            print("Restored state, next guess is %s" % str(self.next_guess))

    def solve(self):
        # Any pending guesses?
        if self.next_guess:
            (r, c, n) = self.next_guess
            self.next_guess = None
        else:
            # Look for groups with 1, then 2, then 3 missing
            for max_choose in range(1,4):                
                # We can handle up to 7 missing in parallel
                for max_missing in range(1,8):
                    move = self.solve_at(max_missing, choose_max=max_choose)
                    if move is not None:
                        break
                if move is not None:
                    break
            if move is None:
                raise UnsolvableGridError("Can't find any more moves")
            (r, c, n) = move
        self.add_number(r, c, n)
        return self.is_finished()

    def is_finished(self):
        """ We are finished if we have no empty cells left """
        return len(self.empty_cells) == 0

    def is_valid(self):
        """ If we have any duplicate numbers in a row, square
        or column then our grid is not valid. """
        for r in range(0, self.cardinal):
            ns = len(self.row_nums[r])
            ms = len([1 for (rc,c,s) in self.empty_cells if rc == r])
            if ns + ms < self.cardinal:
                if self.verbose:
                    print("Duplicate numbers in row %d" % r)
                return False
        for c in range(0, self.cardinal):
            ns = len(self.col_nums[c])
            ms = len([1 for (r,cc,s) in self.empty_cells if cc == c])
            if ns + ms < self.cardinal:
                if self.verbose:
                    print("Duplicate numbers in column %d" % c)
                return False
        for s in range(0, self.cardinal):
            ns = len(self.square_nums[s])
            ms = len([1 for (r,c,sc) in self.empty_cells if sc == s])
            if ns + ms < self.cardinal:
                if self.verbose:
                    print("Duplicate numbers in square %d" % s)
                return False
        # All kosher
        return True
        
    def add_number(self, r, c, n):
        if self.verbose:
            print("Add '%d' to row %d, col %d" % (n, r, c))
        self.lines[r][c] = "%d" % n
        self.compute_groups()
    
    def solve_at(self, num_missing, choose_max=1):
        # Do we have any rows, cols, squares with the given
        # number missing?
        move = None
        for row_idx in range(0, self.cardinal):
            if self.row_missing[row_idx] == num_missing:
                if self.verbose:
                    print("Row %d has exactly %d missing" % (row_idx, num_missing))
                move = self.guess_row(row_idx, num_missing, choose_max)
                if move is not None: return move
        for col_idx in range(0, self.cardinal):
            if self.col_missing[col_idx] == num_missing:
                if self.verbose:
                    print("Col %d has exactly %d missing" % (col_idx, num_missing))
                move = self.guess_col(col_idx, num_missing, choose_max)
                if move is not None: return move
        for square_idx in range(0, self.cardinal):
            if self.square_missing[square_idx] == num_missing:
                if self.verbose:
                    print("Square %d has exactly %d missing" % (square_idx, num_missing))
                move = self.guess_square(square_idx, num_missing, choose_max)
                if move is not None: return move
        return None

    def missing_numbers(self, present_set):
        """ The set of numbers not present """
        return set(range(1,(1+self.cardinal))) - present_set

    def guess_row(self, row_idx, num_missing, choose_max):
        # Find the missing numbers from that row, and what col, square they are in
        missing_places = [ (r,c,s) for (r,c,s) in self.empty_cells if r == row_idx ]
        missing_row_numbers = self.missing_numbers(self.row_nums[row_idx])
        return self.guess(missing_row_numbers, missing_places, choose_max)

    def guess_col(self, col_idx, num_missing, choose_max):
        # Find the missing numbers from that col, and what row, square they are in
        missing_places = [ (r,c,s) for (r,c,s) in self.empty_cells if c == col_idx ]
        missing_col_numbers = self.missing_numbers(self.col_nums[col_idx])
        return self.guess(missing_col_numbers, missing_places, choose_max)

    def guess_square(self, square_idx, num_missing, choose_max):
        # Find the missing numbers from that square, and what row, col they are in
        missing_places = [ (r,c,s) for (r,c,s) in self.empty_cells if s == square_idx ]
        missing_square_numbers = self.missing_numbers(self.square_nums[square_idx])
        return self.guess(missing_square_numbers, missing_places, choose_max)

    def guess(self, missing_numbers, missing_places, choose_max):
        for (r,c,s) in missing_places:
            if self.verbose:
                print("(%d,%d) in square %d" % (r,c,s))
            # Can we eliminate any choices because already in col?
            possibles = []
            for n in missing_numbers:
                if self.verbose:
                    print("  trying %d... " % n),
                if n in self.row_nums[r]:
                    if self.verbose:
                        print("already in row %d" % r)
                    continue
                if n in self.col_nums[c]:
                    if self.verbose:
                        print("already in column %d" % c)
                    continue
                if n in self.square_nums[s]:
                    if self.verbose:
                        print("already in square %d" % s)
                    continue
                if self.verbose:
                    print("possible")
                possibles.append(n)
            if len(possibles) == 0:
                continue
            if len(possibles) == 1:
                # We can put N in the cell at row r, col c
                return (r,c, possibles[0])
            if choose_max > 1 and len(possibles) <= choose_max:
                # We're desperate, choose first one, mark others for backtrack
                self.search_backtracks.append(
                    (self.state_copy(), [ (r,c,p) for p in possibles[1:] ])
                    )
                return (r,c, possibles[0])
        return None

    def scramble(self, degree):
        """ Scramble a full Sudoku grid.

        """
        for i in range(0, degree):            
            r = random.randint(1,2)
            offset = random.randint(0, self.cardinal_root - 1)
            offset = offset * self.cardinal_root
            first = random.randint(0, self.cardinal_root - 1)
            second = random.randint(0, self.cardinal_root - 1)
            if first == second:
                continue
            if r == 1:
                if self.verbose:
                    print("Swap rows %d and %d" % (offset+first, offset+second))
                tmp_row = self.lines[offset+first]
                self.lines[offset+first] = self.lines[offset+second]
                self.lines[offset+second] = tmp_row
            else:
                if self.verbose:
                    print("Swap columns %d and %d" % (offset+first, offset+second))
                for l in self.lines:
                    tmp_cell = l[offset+first]
                    l[offset+first] = l[offset+second]
                    l[offset+second] = tmp_cell
        # all done
        self.compute_groups()

    def whiteout(self, percent):
        """ Pass through the grid, whiting out each cell with
        probability percent/100 """
        for l in self.lines:
            for i in range(0, self.cardinal):
                if random.randint(0,100) <= percent:
                    l[i] = "."
        self.compute_groups()

def fullGrid(verbose):
    """ Return a sudoku grid which is filled
    randomly.
    """
    base_grid = """
123456789
456789123
789123456
234567891
567891234
891234567
345678912
678912345
912345678
"""
    s = Sudoku(base_grid, verbose=verbose)
    assert s.is_finished()
    assert s.is_valid()
    return s


if __name__ == "__main__":
    grid = """
..2.3.546
.945.12..
7....6...
.....76.1
465.2.3.7
..76.3...
.....2..9
.213.478.
3.8.1.4..
"""
    """
    s = Sudoku(grid, verbose=True)
    print s
    finished = False
    try:
        while not finished:
            finished = s.solve()
            print s
    except UnsolvableGridError, err:
            print "Could not solve any more!"
            sys.exit(1)
    print "\nDone!\n"
    assert s.is_valid()
    """

    total_moves = 0
    instances = 10
    tolerance = 50000
    solved = 0
    for i in range(0, instances):
        s2 = fullGrid(verbose=False)
        s2.scramble(degree=25)
        assert s2.is_valid()

        # Now we're going to white it out, with a given percent
        # change of whiting out each cell
        s2.whiteout(percent=70)
        print("\nAnalyzing puzzle:")
        print(s2)
        assert s2.is_valid()

        # And solve it.
        finished = False
        tried_moves = 0
        backtracks = 0
        s2.start_solving()
        while not finished:
            if tried_moves > tolerance:
                print("Giving up after %d moves" % tried_moves)
                break
            try:
                tried_moves +=1
                finished = s2.solve() 
            except UnsolvableGridError as err:
                if s2.has_backtracks():
                    s2.backtrack()
                    backtracks += 1
                else:
                    print("Could not solve any more!\n")
                    finished = True
        assert s2.is_valid()
        if s2.is_finished():
            solved += 1
        print("Executed in %d moves, %d backtracks" % (tried_moves, backtracks))
        print(s2)
        total_moves += tried_moves
    print("Average number of moves to solve = %.1f" % (total_moves / instances))
    print("Solved %d out of %d puzzles" % (solved, instances))    
