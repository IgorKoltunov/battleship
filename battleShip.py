""" You sunk my Battle Ship!
"""

from pprint import pprint
import random

GRID_SIZE = 5


class Grid(object):
    """ Class for Game Grid."""
    def __init__(self, size):
        self.size = size
        self.gridState = []
        for row in range(size):
            row = []
            for column in range(size):
                row.append(0)
            self.gridState.append(row)
    
    def get_hidden_grid(self):
        hiddenGridState = list(self.gridState)
        for rowIndex, row in enumerate(self.gridState):
            for columnIndex, column in enumerate(row):
                if column == 1:
                    hiddenGridState[rowIndex][columnIndex] = 2
        return hiddenGridState


class Ship(object):
    """ Class that stores ship state"""
    def __init__(self, name, sectionLocationTupleList):
        self.name = name
        self.sectionLocationList = sectionLocationTupleList
        self.damagedSectionList = []
        self.isAlive = True
    
    def take_damage(self, gridLocation):
        # Catch dead ship case
        if not self.isAlive:
            print('Error: Cant take damage. Ship is not alive.')
            return None

        if gridLocation in self.sectionLocationList:
            self.damagedSectionList.append(gridLocation)

        # Catch wrong grid location
        else:
            print('Error: Cant take damage as Ship is not on this grid location')
            return None

        # Set ship as dead if all sections are destroyed
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


def get_random_ship_placement_location(grid, shipLength):
    """ Find random but valid ship placement location.
    """
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
        sectionLocationTuple = tuple((row, column))
        sectionLocationTupleList.append(sectionLocationTuple)
        
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
                    
                    sectionLocationTuple = tuple((row, column))
                    sectionLocationTupleList.append(sectionLocationTuple)
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
    shipSizeDic = {#'Aircraft Carrier': (5, 1),
                   #'BattleShip': (4, 1),
                   #'Cruiser': (3, 1),
                   #'Destroyer': (2, 2),
                   'Submarine': (1, 2)}
    shipObjectList = []
    for shipType in shipSizeDic:
        size, number = shipSizeDic[shipType]
        for i in range(number):
            shipObject = Ship(shipType, get_random_ship_placement_location(grid, size))
            shipObjectList.append(shipObject)
            for row, column in shipObject.sectionLocationList:
                grid.gridState[row][column] = 1
    return shipObjectList


def random_ai_move(previousAIMovesTupleList):
        row = random.randrange(GRID_SIZE)
        column = random.randrange(GRID_SIZE)
        aiMoveTuple = tuple((row, column))
        while aiMoveTuple in previousAIMovesTupleList:
            row = random.randrange(GRID_SIZE)
            column = random.randrange(GRID_SIZE)
            aiMoveTuple = tuple((row, column))
        return aiMoveTuple

def main():

    # Create playing fields for computer and AI.
    humanGrid = Grid(GRID_SIZE)
    aiGrid = Grid(GRID_SIZE)

    # Create ships and populate grids.
    humanShipList = populate_grid(humanGrid)
    aiShipList = populate_grid(aiGrid)

    # Debug:
    print('Starting Grid State Human')
    pprint(humanGrid.gridState)
    print('Starting Grid State AI')
    pprint(aiGrid.gridState)


    previousAIMovesTupleList = []
    # Keep game going while there are AI and Human ships alive.
    while len(aiShipList) != 0 and len(humanShipList) != 0:
        isHit = False
        # Get a move from human
        row = int(input('Give a row number (0-9): '))
        column = int(input('Give a column number (0-9): '))
        humanMoveTuple = tuple((row, column))

        # Check if there was a hit
        for ship in aiShipList:
            if humanMoveTuple in ship.sectionLocationList:
                print('Human, there was a hit!')
                isHit = True
                print(humanMoveTuple)
                print(ship.name, ship.sectionLocationList)
                ship.take_damage(humanMoveTuple)
                if not ship.isAlive:
                    print('Nice! You sunk the', ship.name)
                    aiShipList.remove(ship)
                aiGrid.gridState[row][column] = 2
        if not isHit:
            print('Human Missed!')
            aiGrid.gridState[row][column] = 3
        print('AI Grid:')
        print('Human move was:', humanMoveTuple)
        pprint(aiGrid.gridState)

        isHit = False
         # Get a move from AI.
        aiMoveTuple = random_ai_move(previousAIMovesTupleList)
        previousAIMovesTupleList.append(aiMoveTuple)

        # Check if there was a hit
        for ship in humanShipList:
            if aiMoveTuple in ship.sectionLocationList:
                row, column = aiMoveTuple
                print('AI, there was a hit!')
                isHit = True
                print(aiMoveTuple)
                print(ship.name, ship.sectionLocationList)
                ship.take_damage(aiMoveTuple)
                if not ship.isAlive:
                    print('Nice! You sunk the', ship.name)
                    humanShipList.remove(ship)
                humanGrid.gridState[row][column] = 2
        if not isHit:
            print('AI Missed!')
            row, column = aiMoveTuple
            humanGrid.gridState[row][column] = 3
        print('Human Grid:')
        print('AI move was:', aiMoveTuple)
        pprint(humanGrid.gridState)

    print('Game is finished!')

main ()

