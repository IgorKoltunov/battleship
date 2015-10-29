""" You sunk my Battle Ship!
"""

from pprint import pprint
import random

# Size of the playing field in units squared.
GRID_SIZE = 8


class Grid(object):
    """ Class for keeping track of player's grid state.
    """
    def __init__(self, size):
        self.size = size
        self.gridState = []
        self.aliveShipObjectList = []
                
        # Create Initial empty grid state. 
        for row in range(size):
            row = []
            for column in range(size):
                row.append(0)
            self.gridState.append(row)
    
    def get_hidden_grid(self):
        """ Method is used to hide enemy ships during the game.
        """
        # Make a copy of the grid.
        hiddenGridState = list(self.gridState)
        
        # Change all the ship cells to 0 to hide ship locations.
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
        # Catch dead ship case.
        if not self.isAlive:
            print('Error: Cant take damage. Ship is not alive.')
            return None

        if gridLocation in self.sectionLocationList:
            self.damagedSectionList.append(gridLocation)

        # Catch wrong grid location.
        else:
            print('Error: Cant take damage as Ship is not at this grid location')
            return None

        # Mark ship as dead if all sections are destroyed.
        if set(self.damagedSectionList) == set(self.sectionLocationList):
            self.isAlive = False


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

    # Check if Right Side edge.
    if column == grid.size - 1:
        pass
    # Check if adjacent to another ship on the right.
    elif grid.gridState[row][column + 1] != 0:
        return False

    # Check if Left Side edge.
    if column == 0:
        pass
    # Check if adjacent to another ship on the left.
    elif grid.gridState[row][column - 1] != 0:
        return False
 
    # Check if Bottom Edge.
    if row == grid.size - 1:
        pass    
    # Check if adjacent to another ship below.
    elif grid.gridState[row + 1][column] != 0:
        return False
    
    # Check if Top Edge.
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
    
    # All checks have passed. Location is valid.
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


def get_random_ship_placement_location(grid, shipLength):
    """ Find random but valid placement location for a ship.
    """
    # Counter to guard against infinite loops.
    tries = 0
    
    sectionLocationTupleList = []
    
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
            # Set orientation for the ship.
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

    
def populate_grid(grid):
    """ Populate a given grid with ships.
    """
    # Dictionary of ship type to length and number per player.
    shipSizeDic = {#'Aircraft Carrier': (5, 1),
                   #'Battleship': (4, 1),
                   #'Cruiser': (3, 1),
                   #'Destroyer': (2, 2),
                   #'Submarine': (1, 2),
                   'DebugShip': (4, 2)}
    
    # Place ships on the grid in random locations.
    for shipType in shipSizeDic:
        size, number = shipSizeDic[shipType]
        for i in range(number):
            shipObject = Ship(shipType, get_random_ship_placement_location(grid, size))
            grid.aliveShipObjectList.append(shipObject)
            for row, column in shipObject.sectionLocationList:
                grid.gridState[row][column] = 1


def random_ai_move(grid):
    """ Return a random move on a given grid.
    """
    row = random.randrange(GRID_SIZE)
    column = random.randrange(GRID_SIZE)
    aiMoveTuple = (row, column)
    
    # Look for a valid move if first random location is invalid. 
    while not is_valid_move(grid, aiMoveTuple):
        row = random.randrange(GRID_SIZE)
        column = random.randrange(GRID_SIZE)
        aiMoveTuple = (row, column)
    
    return aiMoveTuple    


def smart_ai_move(grid, origHitTuple):
    row, column = origHitTuple
    
    if is_valid_move(grid, (row + 1, column)):
        row += 1
    elif is_valid_move(grid, (row - 1, column)):
        row -= 1    
    elif is_valid_move(grid, (row, column + 1)):
        column += 1     
    elif is_valid_move(grid, (row, column - 1)):
        column -= 1    
    else:
        print('No Valid Moves found in search pattern. Switching to random')
        isTargetMode = False
        return random_ai_move(grid)
            
    aiMoveTuple = (row, column)    
    return aiMoveTuple

def ai_move(grid):
    # Since this function is going to be part of a loop, setting these
    # variables as global so their state is remembered for future uses
    # of the function.
    global origHitTuple
    global isTargetMode
    
    # If isTargetMode has not been defined yet, assuming it is False.
    if 'isTargetMode' not in globals():
        isTargetMode = False
    
    if isTargetMode:
        print('Target mode pattern')
        aiMoveTuple = smart_ai_move(grid, origHitTuple)
    else:
        # Get a random move from AI.
        aiMoveTuple = random_ai_move(grid)
    
    # Check if there was a hit
    for ship in grid.aliveShipObjectList:
        if aiMoveTuple in ship.sectionLocationList:
            isTargetMode = True
            row, column = aiMoveTuple
            origHitTuple = aiMoveTuple
            print('AI, there was a hit!')
            print(aiMoveTuple)
            #print(ship.name, ship.sectionLocationList)
            ship.take_damage(aiMoveTuple)
            if not ship.isAlive:
                print('Nice! You sunk the', ship.name)
                grid.aliveShipObjectList.remove(ship)
                isTargetMode = False
                smart_ai_move.variationPattern = 0
                
            grid.gridState[row][column] = 2
            break
            
    else:
        print('AI Missed!')
        row, column = aiMoveTuple
        grid.gridState[row][column] = 3
    
    return aiMoveTuple  

def main():
    humanGrid = Grid(GRID_SIZE)
    populate_grid(humanGrid)
    pprint(humanGrid.gridState)
    
    while len(humanGrid.aliveShipObjectList) != 0:
        aiMoveTuple = ai_move(humanGrid)                   
        print('Human Grid:')
        print('AI move was:', aiMoveTuple)
        pprint(humanGrid.gridState)
        input()
 
main()    
