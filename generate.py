import sys
#import termcolor
from crossword import *
from queue import Queue

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        res = self.backtrack(dict())
        assert self.consistent(res)
        return res

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            self.domains[var] = set(val for val in self.domains[var] if len(val)==var.length)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        def exists_valid_overlap(value_x, y, index_x, index_y):
            for val_y in self.domains[y]:
                if value_x[index_x] == val_y[index_y] and value_x != val_y:
                    return True
            return False

        revised = False
            
        overlap = self.crossword.overlaps[x, y]
        if overlap:
            index_x, index_y = overlap
            for value_x in self.domains[x].copy():
                if not exists_valid_overlap(value_x, y, index_x, index_y):
                    self.domains[x].remove(value_x)
                    revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            arcs = list(self.crossword.overlaps.keys())
            
        q = Queue()
        for arc in arcs:
            q.put(arc)

        # repeat
        while not q.empty():
            X, Y = q.get()
            if self.revise(X, Y):
                if len(self.domains[X]) == 0:
                    return False
                
                neighbors = set([var for var,curr in arcs if curr == X])
                if Y in neighbors:
                    neighbors.remove(Y)
                if X in neighbors:
                    neighbors.remove(X)
                for Z in neighbors:
                    q.put((Z, X))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        variables = self.crossword.variables
        assigned = assignment.keys()
        return not len(set(variables-assigned))

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # check distinct words
        values_num = len(list(assignment.values()))
        distinct_values_num = len(set(assignment.values()))
        if values_num != distinct_values_num:
            return False
        
        # check words length
        for var in assignment:
            if var.length != len(assignment[var]):
                return False
        
        # check neighbor conflicts
        for X in assignment:
            neighbors = self.crossword.neighbors(X)
            for Y in neighbors:
                if Y in set(assignment.keys()):
                    index_x = self.crossword.overlaps[(X, Y)][0]
                    index_y = self.crossword.overlaps[(X, Y)][1]
                    if assignment[X][index_x] != assignment[Y][index_y]:
                        return False
        return True

    def order_domain_values(self, var, assignment):      
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # does not update anything
        def constraints_removed_by_neighbor(Z, val):
            removed = 0
            if Z not in assignment:
                for z in self.domains[Z]:
                    if z == val:
                        removed += 1
                    elif self.crossword.overlaps[var, Z]:
                        i, j = self.crossword.overlaps[var, Z]
                        if val[i] != z[j]:
                            removed += 1
            return removed
        
        # updates self.domains[var]
        def constraints_removed_by_value(val):
            old_domain = self.domains[var].copy()
            self.domains[var] = set([val])
            constraints_removed = 0
            for Z in set.intersection(self.crossword.neighbors(var), vars_left):
                constraints_removed += constraints_removed_by_neighbor(Z, val)
            self.domains[var] = old_domain
            return constraints_removed

        if not self.domains[var]:
            return []

        # keep a copy of domains to restore them in the end
        init_domain = self.domains.copy()

        # update the domains of the assigned variables
        for assigned in assignment:
            self.domains[assigned] = set([assignment[assigned]])

        vars_left = set(self.crossword.variables - set(assignment.keys()))

        values = sorted(self.domains[var], key = lambda value: constraints_removed_by_value(value))
        
        self.domains = init_domain
        
        return values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        vars_left = list(self.crossword.variables-set(assignment.keys()))
        sorted_vars_left = sorted(vars_left, key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var))))
        return sorted_vars_left[0] if sorted_vars_left else None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        if not self.consistent(assignment):
            return None
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            result = self.backtrack(assignment)
            if result is not None:
                return result
            del assignment[var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()