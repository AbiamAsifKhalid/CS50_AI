import sys
from crossword import *
from copy import deepcopy
from collections import deque


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
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            removelist = []
            for word in self.domains[variable]:
                if variable.length == len(word):
                    continue
                else: removelist.append(word)
            
            self.domains[variable]= self.domains[variable] - set(removelist)

        # print(self.domains)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revise = False
        overlap = self.crossword.overlaps[x, y]
        if overlap:
            i, j = overlap
            for word_x in self.domains[x].copy():
                overlaps = False
                for word_y in self.domains[y]:
                    if word_x[i] == word_y[j]:
                        overlaps = True
                if not overlaps:
                    self.domains[x].remove(word_x)
                    revise = True 
                    
        return revise 
    
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """      
        if not arcs:
            arcs = []
            for X in self.crossword.variables:
                for neighbor in self.crossword.neighbors(X):
                    arcs.append((X, neighbor))
        else:
            arcs = deque(arcs)

        while arcs:
            X, Y = arcs.pop()
            if self.revise(X ,Y):
                if len(self.domains[X]) == 0:
                    return False
                for Z in self.crossword.neighbors(X) - {Y}:
                    arcs.append((Z, X))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for Variable in self.domains:
            if Variable in assignment.keys():
                continue
            else:
                return False
            
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # print(words)
        for variable in assignment:
            if variable.length != len(assignment[variable]):
                return False
            
            for key, value in assignment.items():
                if variable != key:
                    if assignment[variable]== value:
                        return False

            for neighbour in self.crossword.neighbors(variable):
                if neighbour in assignment.keys():
                    x, y = self.crossword.overlaps[variable, neighbour]
                    if neighbour in assignment:
                        if assignment[variable][x] != assignment[neighbour][y]:
                            return False
                
        return True            

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbours = self.crossword.neighbors(var)
        elimination = {}
        for word in self.domains[var]:
            elim =0
            for neighbour in neighbours:
                if word in self.domains[neighbour]:
                       elim += 1          
            elimination[word] = elim

        ordered = sorted(elimination , key = lambda word : elimination[word])
        # print(ordered)
        return ordered
    
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # print(assignment)
        domains = []
        for variable in self.domains:
            if variable not in assignment:
               domains.append(variable)

        result = domains[0]
        for var in domains:
            if result != var:
                if len(self.domains[result]) > len(self.domains[var]):
                    result = var
                elif len(self.domains[result]) == len(self.domains[var]): 
                    if len(self.crossword.neighbors(result)) <=  len(self.crossword.neighbors(var)):
                        result = var
                
        return result
    
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)      

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
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
    # structure = "data/structure0.txt"
    # words = "data/words0.txt"
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
