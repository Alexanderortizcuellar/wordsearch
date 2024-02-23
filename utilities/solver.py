import random


def find_positions(puzzle:str, word:str):
    with open(puzzle) as file:
            grid = file.readlines()
            grid = list(map(lambda x:x.replace("\n",""), grid))
            grid = list(map(lambda x:x.replace(" ",""), grid))
            width = len(grid[0])
            height = len(grid)
            positions = []
            for row in range(height):
                for column in range(width):
                    if grid[row][column] == word[0]:
                        positions.append((row, column,grid[row][column]))
    return grid,positions,height,width


directions = [(1,0), (0,1), (1,1), (-1,0),(0,-1),(-1,-1)]

def find_word(word):
    grid,positions,height,width = find_positions("wordsearch.txt", word)
    for position in positions:
        xstart = position[0]
        ystart = position[1]
        for d in directions:
            word_location = []
            for i,c in enumerate(word):
                if xstart+i*d[0] >= height or ystart+i*d[1] >= width:
                    break
                pos = grid[xstart+i*d[0]][ystart+i*d[1]]
                if pos == c:
                    word_location.append((xstart+i*d[0],ystart+i*d[1]))
                else:
                    word_location.clear()
                    break
            else:
                print(word,word_location)
                break
            continue
    
