import sys
import termcolor
from crossword import *
from queue import Queue
import copy

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
        #termcolor.cprint('VARIABLES:', 'red')
        #termcolor.cprint(self.crossword.variables, 'red')
        
        #termcolor.cprint('INIT DOMAINS:', 'red')
        #termcolor.cprint(self.domains, 'green')
        #termcolor.cprint('OVERLAPS', 'red')
        #termcolor.cprint(self.crossword.overlaps, 'green')
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #termcolor.cprint("- I enforce node consistency", 'red')
        for var in self.domains:
            self.domains[var] = set(val for val in self.domains[var] if len(val)==var.length)
        #termcolor.cprint(' NEW DOMAINS:', 'red')
        #termcolor.cprint(self.domains, 'green')

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

        #termcolor.cprint(f"----I am revise between {x.__str__()} and {y.__str__()}", 'red')
        #termcolor.cprint(f"domain[X]: {self.domains[x]}\ndomain[Y]: {self.domains[y]}", 'red')
        
        revised = False
        #inter = set.intersection(self.domains[x], self.domains[y])
        #if inter:
            #print(f"THEY HAVE {len(inter)} COMMON")
            #print(inter)
        #    pass
        #if len(self.domains[y]) == 1:
        #    #termcolor.cprint("FOUND LONELY", 'red')
        #    value_y = self.domains[y].pop()
        #    if value_y in self.domains[x]:
        #        #termcolor.cprint("FOUND DUPLICATE", 'yellow')
        #        self.domains[x].remove(value_y)
        #        revised = True
        #    self.domains[y].add(value_y)

            
        overlap = self.crossword.overlaps[x, y]
        if overlap:
            index_x, index_y = overlap
            #termcolor.cprint(f"They have an overlap at {overlap}", "red")
            for value_x in self.domains[x].copy():
                if not exists_valid_overlap(value_x, y, index_x, index_y):
                    #termcolor.cprint(f"I remove {value_x} from domain of X", 'yellow')
                    self.domains[x].remove(value_x)
                    revised = True
        #termcolor.cprint(f"----I revised them", 'red')
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        #termcolor.cprint("I am ac3", 'red')
        # queue initialization
        if not arcs:
            #arcs = list(self.crossword.overlaps.keys())
            
            #termcolor.cprint("ARCS", 'yellow')
            #termcolor.cprint(arcs, 'yellow')
            arcs = [(x, y) for x in self.crossword.variables for y in self.crossword.variables if x!=y]
            #termcolor.cprint("ARCS", 'yellow')
            #termcolor.cprint(arcs, 'yellow')

        q = Queue()
        for arc in arcs:
            q.put(arc)

        # repeat
        while not q.empty():
            X, Y = q.get()
            #termcolor.cprint(f"I dequeue the arc ({X}, {Y})")
            old_domain = self.domains[X].copy()        
            if self.revise(X, Y):
                #termcolor.cprint(f"I updated domain of {X}", 'green')
                #print("to:", self.domains[X], sep='\n')
                if len(self.domains[X]) == 0:
                    #termcolor.cprint("I am ac3 and returning TRUE", 'green')
                    return False
                
                neighbors = set([var for var,curr in arcs if curr == X])
                #termcolor.cprint("Neighbors before:", 'red')
                #termcolor.cprint(neighbors, 'red')
                if Y in neighbors:
                    neighbors.remove(Y)
                if X in neighbors:
                    neighbors.remove(X)
                #termcolor.cprint("Neighbors after:", 'red')
                #termcolor.cprint(neighbors, 'red')
                for Z in neighbors:
                    q.put((Z, X))
            #termcolor.cprint(f"I did not update domain of {X}", 'green')
        #termcolor.cprint("I am ac3 and returning TRUE", 'green')
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
        '''for overlap in self.crossword.overlaps:
            X, Y = overlap
            index_x = overlap[(X, Y)][0]
            index_y = overlap[(X, Y)][1]
            if X in assignment and Y in assignment:
                if assignment[X][index_x] != assignment[Y][index_y]:
                    return False
        '''
        for X in assignment:
            neighbors = self.crossword.neighbors(X)
            for Y in set.intersection(neighbors, set(assignment.keys())):
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
        
        def constraints_removed_by_neighbor(Z):
            removed = 0
            #termcolor.cprint(f"From domain ({len(init_domain[Z])}):", 'blue')
            #termcolor.cprint(init_domain[Z], 'yellow')
            if self.revise(Z, var):
                #termcolor.cprint(init_domain[Z], 'yellow')
                removed += len(assign_domain[Z])-len(self.domains[Z])
                #termcolor.cprint(f"To domain ({len(self.domains[Z])}):", 'blue')
                #termcolor.cprint(self.domains[Z], 'yellow')
                #termcolor.cprint(f"I cut {removed} values for this neighbor")
            return removed
        
        def constraints_removed_by_value(val):
            self.domains = copy.deepcopy(assign_domain)
            self.domains[var] = set()
            self.domains[var].add(val)
            constraints_removed = 0
            for Z in set.intersection(self.crossword.neighbors(var), vars_left):
                #termcolor.cprint(f"For neighbor {Z.__str__()}")
                constraints_removed += constraints_removed_by_neighbor(Z)
                self.domains[Z] = copy.deepcopy(assign_domain[Z])
            #termcolor.cprint(f"Value {value} removes {constraints_removed} constraints.", 'blue')
            return constraints_removed

        if not self.domains[var]:
            return []
        
        #termcolor.cprint("ASSIGNMENT", 'yellow')
        #termcolor.cprint(assignment, 'yellow')

        # keep a copy of domains to restore them in the end
        init_init_domain = copy.deepcopy(self.domains)

        # update the domains of the assigned variables
        for assigned in assignment:
            #print('--------------')
            #termcolor.cprint(assignment[var], 'red')
            #termcolor.cprint(self.domains[var], 'yellow')
            #print(assignment[var] in self.domains[var])
            #print('--------------')
            self.domains[assigned] = set()
            self.domains[assigned].add(assignment[assigned])

        #termcolor.cprint(f"I will pick the next value for var: ({var.__str__()}) from domain", 'blue')
        #termcolor.cprint(self.domains[var], 'blue')


        assign_domain = copy.deepcopy(self.domains)

        vars_left = set(self.crossword.variables - set(assignment.keys()))
        values = self.domains[var].copy()

        c = 0
        #for value in values:
            #if c==2 or c==3:
            #    #termcolor.cprint("I initialize the domains to", 'green')
            #    #termcolor.cprint(self.domains, 'green')
            #termcolor.cprint(f"Value {value}:", 'blue')
        #    rem = constraints_removed_by_value(value)

        values2 = sorted(values, key = lambda value: constraints_removed_by_value(value))
        #termcolor.cprint(list(values), 'green')
        #termcolor.cprint(values2, 'red')
        #termcolor.cprint(set.intersection(set(values), set(values2))==set(values), 'yellow' )
        
        self.domains = init_init_domain
        
        #values = list(copy.deepcopy(self.domains[var]))
        #random.shuffle(values)
        
        #termcolor.cprint(values2, 'red')
        #return [value for value in self.domains[var]]

        return values2

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        vars_left = list(self.crossword.variables-set(assignment.keys()))

        # my_vars_left = [my_variable(var, len(self.domains[var]), len(self.crossword.neighbors(var))) for var in vars_left]

        my_vars_left = sorted(vars_left, key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var))))

        return my_vars_left[0] if my_vars_left else None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #termcolor.cprint("I am backtrack", 'green')
        if not self.consistent(assignment):
            return None
        #termcolor.cprint("Ass is consistent", 'green')
        if self.assignment_complete(assignment):
            return assignment
        #termcolor.cprint("Ass is not complete", 'green')
        var = self.select_unassigned_variable(assignment)
        #termcolor.cprint(f"Chose var: {var.__str__()}", 'yellow')
        for value in self.order_domain_values(var, assignment):
            #termcolor.cprint(f"Testing value {value}", 'yellow')
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
