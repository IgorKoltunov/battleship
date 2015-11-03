""" Classic game of Battleship against the AI.
"""

from pprint import pprint
import random

# Size of the playing field grid in units squared.
GRID_SIZE = 6


class Grid(object):
    """ Class for keeping track of player's grid state.
    """
    def __init__(self, size):
        self.size = size
        self.gridState = []
        self.aliveShipObjectList = []
                
        # Create initial empty grid state. 
        for row in range(size):
            row = []
            for column in range(size):
                row.append(0)
            self.gridState.append(row)

    def populate_grid(self):  
        """ Populate the grid with ships.
        """
        # Dictionary of ship type to length and number per player.
        shipSizeDic = {#'Aircraft Carrier': (5, 1),
                       #'Battleship': (4, 1),
                       #'Cruiser': (3, 1),
                       #'Destroyer': (2, 2),
                       #'Submarine': (1, 2),}
                       'DebugShip': (4, 2)}
        
        # Place ships on the grid in random locations.
        for shipType in shipSizeDic:
            size, number = shipSizeDic[shipType]
            for i in range(number):
                shipObject = Ship(shipType, get_random_ship_placement_location(self, size))
                self.aliveShipObjectList.append(shipObject)
                for row, column in shipObject.sectionLocationList:
                    self.gridState[row][column] = 1 

    def get_hidden_grid(self):
        """ Method is used to hide enemy ships during the game.
        """
        # Make a copy of the grid.
        hiddenGridState = list(self.gridState)

        # Change all the ship cells to 0 for printing to hide ship locations.
        for rowIndex, row in enumerate(self.gridState):
            for columnIndex, column in enumerate(row):
                if column == 1:
                    hiddenGridState[rowIndex][columnIndex] = 0
        return hiddenGridState
                    
                    
class Ship(object):
    """ Class that stores ship state, location and damage taken.
    """
    def __init__(self, name, sectionLocationTupleList):
        self.name = name
        self.sectionLocationList = sectionLocationTupleList
        self.damagedSectionList = []
        self.isAlive = True
    
    def take_damage(self, gridLocation):
        """ Method for keeping track of damage to the ship.
        """
        # Catch a dead ship case.
        if not self.isAlive:
            print('Error: Cant take damage. Ship is not alive.')            

        if gridLocation in self.sectionLocationList:
            self.damagedSectionList.append(gridLocation)

        # Catch wrong grid location.
        else:
            print('Error: Cant take damage as Ship is not at this grid location.')

        # Mark ship as dead if all sections are destroyed.
        if set(self.damagedSectionList) == set(self.sectionLocationList):
            self.isAlive = False


class AIMind(object):            
    """ Class that handles AI move logic.
    """
    def __init__(self, grid):        
        self.grid = grid
        self.aiMoveTuple = None
        self.isTargetMode = False
        self.isSecondHit = False
        self.orientation = None
        self.origHitTuple = None
        self.hitTuple = None
        self.subsequentHitTuple = None
        
    def provide_random_move(self):
        """ Return a random move on a given grid.
        """
        row = random.randrange(GRID_SIZE)
        column = random.randrange(GRID_SIZE)
        self.aiMoveTuple = (row, column)

        # Look for a valid move if first random location is invalid. 
        while not is_valid_move(self.grid, self.aiMoveTuple) or is_move_adjacent_to_known_ship(self.grid, self.aiMoveTuple):
            row = random.randrange(GRID_SIZE)
            column = random.randrange(GRID_SIZE)
            self.aiMoveTuple = (row, column)
        
        return self.aiMoveTuple     

    def provide_pattern_move(self, hitTuple):
        """ Method generates moves adjacent to the last known hit.
        """
        row, column = hitTuple
        
        # Make hits to cells adjacent to last known hit.
        if is_valid_move(self.grid, (row + 1, column)):
            row += 1
        elif is_valid_move(self.grid, (row - 1, column)):
            row -= 1    
        elif is_valid_move(self.grid, (row, column + 1)):
            column += 1     
        elif is_valid_move(self.grid, (row, column - 1)):
            column -= 1    
        else:
            # If there are no valid moves in adjacent cells, fall back
            # to random hit logic.
            print('No Valid Moves found in search pattern. Switching to random')
            self.isTargetMode = False
            return self.provide_random_move()
                
        self.aiMoveTuple = (row, column)    
        return self.aiMoveTuple        

    def provide_targeted_move(self, aiMoveTuple):
        """ After there have been multiple hits on same ship,
            this method will provide moves along that axis.
        """
        row, column = self.aiMoveTuple
        origRow, origColumn = self.origHitTuple
        subRow, subColumn = self.subsequentHitTuple

        # Determine orientation of the ship.
        if not self.orientation:
            if origRow - subRow == 0:
                self.orientation = 'horizontal'
            elif origColumn - subColumn == 0:
                self.orientation = 'vertical'

        if self.orientation == 'horizontal':
            # Keep attacking adjacent cells on same axis as long as last move was not a miss.
            if is_valid_move(self.grid, (origRow, subColumn + 1)) and self.grid.gridState[row][column] != 3:
                self.aiMoveTuple = (origRow, subColumn + 1)
            
            # Attack cells in different direction starting from
            # original hit point.
            else:
                origColumn -= 1
                self.origHitTuple = (origRow, origColumn)
                self.aiMoveTuple = self.origHitTuple
                    
                while not is_valid_move(self.grid, self.aiMoveTuple):
                    origColumn -= 1
                    self.origHitTuple = (origRow, origColumn)
                    self.aiMoveTuple = self.origHitTuple
                    
        # Same logic as above but for vertical ship orientation.
        elif self.orientation == 'vertical':
            if is_valid_move(self.grid, (subRow + 1, origColumn)) and self.grid.gridState[row][column] != 3:
                self.aiMoveTuple = (subRow + 1, origColumn)
            else:
                origRow -= 1
                self.origHitTuple = (origRow, origColumn)
                self.aiMoveTuple = self.origHitTuple

                while not is_valid_move(self.grid, self.aiMoveTuple):
                    origRow -= 1
                    self.origHitTuple = (origRow, origColumn)
                    self.aiMoveTuple = self.origHitTuple

        return self.aiMoveTuple


def is_valid_placement(grid, row, column):
    """ Function checks if a particular point on a grid is valid for
        ship section placement.
    """

    # Check if point is outside of grid index range.
    if row < 0 or row > grid.size - 1:
        return False
    if column < 0 or column > grid.size - 1:
        return False

    # Make sure there is nothing there.
    if grid.gridState[row][column] != 0:
        return False  

    # If right side grid edge, there is no adjacent cell to check.
    if column == grid.size - 1:
        pass
    # Check if adjacent to another ship on the right.
    elif grid.gridState[row][column + 1] != 0:
        return False

    # If left side grid edge, there is no adjacent cell to check.
    if column == 0:
        pass
    # Check if adjacent to another ship on the left.
    elif grid.gridState[row][column - 1] != 0:
        return False
 
    # If bottom grid edge, there is no adjacent cell to check.
    if row == grid.size - 1:
        pass    
    # Check if adjacent to another ship below.
    elif grid.gridState[row + 1][column] != 0:
        return False
    
    # If top grid edge, there is no adjacent cell to check.
    if row == 0:
        pass
    # Check if adjacent to another ship above.
    elif grid.gridState[row - 1][column] != 0:
        return False

    # Check if Top Right corner of the grid.
    if row != 0 and column != grid.size - 1:
        # Check if adjacent to another ship on top right.
        if grid.gridState[row - 1][column + 1] != 0:
            return False
    
    # Check if Top Left corner of the grid.
    if row != 0 and column != 0:
        # Check if adjacent to another ship on top left.
        if grid.gridState[row - 1][column - 1] != 0:
            return False        
    
    # Check if Bottom Right corner of the grid.
    if row != grid.size - 1 and column != grid.size - 1:
        # Check if adjacent to another ship on bottom right.
        if grid.gridState[row + 1][column + 1] != 0:
            return False  
            
    # Check if Bottom Left corner of the grid.
    if row != grid.size - 1 and column != 0:
        # Check if adjacent to another ship on bottom left.    
        if grid.gridState[row + 1][column - 1] != 0:
            return False
    
    # All checks have passed. Ship placement location is valid.
    return True

    
def is_valid_move(grid, moveTuple):
    """ Check if a particular move would be valid.
    """
    row, column = moveTuple
    # Check if move is outside of grid index range.
    if row < 0 or row > grid.size - 1:
        return False
    if column < 0 or column > grid.size - 1:
        return False
        
    # Check if point has already been attacked.
    if grid.gridState[row][column] == 2 or grid.gridState[row][column] == 3:
        return False
    
    # All checks have passed. Move is valid.
    return True    


def is_move_adjacent_to_known_ship(grid, moveTuple):
    """ Check if a particular move would be adjacent to known ship.
        This function is used to improve random move generation logic.
        Since ships can't be adjacent to each other, those cells can be ignored.
    """
    row, column = moveTuple
    
    # Check if Right Side edge.
    if column == grid.size - 1:
        pass
    # Check if adjacent to another ship on the right.
    elif grid.gridState[row][column + 1] == 2:
        return True

    # Check if Left Side edge.
    if column == 0:
        pass
    # Check if adjacent to another ship on the left.
    elif grid.gridState[row][column - 1] == 2:
        return True
 
    # Check if Bottom Edge.
    if row == grid.size - 1:
        pass    
    # Check if adjacent to another ship below.
    elif grid.gridState[row + 1][column] == 2:
        return True
    
    # Check if Top Edge.
    if row == 0:
        pass
    # Check if adjacent to another ship above.
    elif grid.gridState[row - 1][column] == 2:
        return True

    # Check if Top Right corner of the grid.
    if row != 0 and column != grid.size - 1:
        # Check if adjacent to another ship on top right.
        if grid.gridState[row - 1][column + 1] == 2:
            return True
    
    # Check if Top Left corner of the grid.
    if row != 0 and column != 0:
        # Check if adjacent to another ship on top left.
        if grid.gridState[row - 1][column - 1] == 2:
            return True      
    
    # Check if Bottom Right corner of the grid.
    if row != grid.size - 1 and column != grid.size - 1:
        # Check if adjacent to another ship on bottom right.
        if grid.gridState[row + 1][column + 1] == 2:
            return True  
            
    # Check if Bottom Left corner of the grid.
    if row != grid.size - 1 and column != 0:
        # Check if adjacent to another ship on bottom left.    
        if grid.gridState[row + 1][column - 1] == 2:
            return True
    
    # All checks have passed. Location is not adjacent to any ships
    return False


def get_random_ship_placement_location(grid, shipLength):
    """ Find random but valid placement location for a ship.
    """
    # Initiating counter to guard against infinite loops in cases where
    # no valid placement can be found.
    tries = 0
    
    sectionLocationTupleList = []
    
    # Keep adding sections to equal the ship length.
    while len(sectionLocationTupleList) != shipLength and tries != 100000:
        tries += 1
        sectionLocationTupleList = []
        # Look for a random place for the first section.
        row = random.randrange(grid.size)
        column = random.randrange(grid.size)
        # Start over if there is no valid placement.
        if not is_valid_placement(grid, row, column):
            continue
        sectionLocationTupleList.append((row, column))
        
        # Continue adding sections if needed.
        if shipLength > 1:
            # Set random orientation for the ship.
            randomOrientation = random.randrange(4)
            for i in range(shipLength - 1):
                
                if randomOrientation == 0:
                    row += 1
                elif randomOrientation == 1:
                    row -= 1
                elif randomOrientation == 2:
                    column += 1
                elif randomOrientation == 3:
                    column -= 1        
                
                if is_valid_placement(grid, row, column):
                                        
                    sectionLocationTupleList.append((row, column))
                # If no valid placement for section, exit loop.
                else:
                    break
            # Start over if section list is incomplete.
            if len(sectionLocationTupleList) < shipLength:
                continue
        # Exit the while loop normally as we have found a location for every section.
        break
    # Unable to find valid location after maximum number of tries.
    else:
        print('Critical Error: No ship placement found after', format(tries, ','), 'tries.')
        return []
    return sectionLocationTupleList

def ai_make_a_move(humanGrid, aiBrain):
    """ Decide on a move from AI based on what is known about the grid
        state. Update the grid, ship and AI state with the results of the move.
    """    
        
    # If there was a previous hit, switch to attacking adjacent cells.
    if aiBrain.isTargetMode and not aiBrain.isSecondHit:
        aiMoveTuple = aiBrain.provide_pattern_move(aiBrain.hitTuple)
    
    # If there were two hits, switch to attacking same axis of cells.
    elif aiBrain.isTargetMode and aiBrain.isSecondHit:       
        aiMoveTuple = aiBrain.provide_targeted_move(aiBrain.aiMoveTuple)

    # If not in target mode, get a random guess.    
    else:     
        aiMoveTuple = aiBrain.provide_random_move()
    
    # Check if the move resulted on a hit on any ship objects.
    for ship in humanGrid.aliveShipObjectList:       
        # If there was a hit, update grid and state accordingly.
        if aiMoveTuple in ship.sectionLocationList:
            if aiBrain.isTargetMode:
                aiBrain.isSecondHit = True
                aiBrain.subsequentHitTuple = aiMoveTuple
            else:
                aiBrain.origHitTuple = aiMoveTuple
            
            row, column = aiMoveTuple
            print('AI, there was a hit!')
            print(aiMoveTuple)
            aiBrain.hitTuple = aiMoveTuple
            ship.take_damage(aiMoveTuple)
            aiBrain.isTargetMode = True
            if not ship.isAlive:
                print('AI sunk the', ship.name)
                humanGrid.aliveShipObjectList.remove(ship)
                aiBrain.isTargetMode = False
                aiBrain.isSecondHit = False
                aiBrain.orientation = None
            humanGrid.gridState[row][column] = 2
            break
    # If there were no hits, mark it as a miss on the grid.   
    else:
        print('AI Missed!')
        row, column = aiMoveTuple
        humanGrid.gridState[row][column] = 3            
    
def main():
    # Create a human grid object.
    humanGrid = Grid(GRID_SIZE)
    
    # Populate the human grid with ships.
    humanGrid.populate_grid()
    
    # Create AI Brain object.
    aiBrain = AIMind(humanGrid)
    
    # Print Starting Human grid state.
    pprint(humanGrid.gridState)

    # Keep the game going while there are any ships alive.
    while humanGrid.aliveShipObjectList:
        ai_make_a_move(humanGrid, aiBrain)

        print('Human Grid:')
        print('AI move was:', aiBrain.aiMoveTuple)
        pprint(humanGrid.gridState)
        input()
 
main()    
