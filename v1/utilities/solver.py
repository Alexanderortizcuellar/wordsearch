def find_grid(name:str):
    with open(name) as file:
        grid = file.readlines()
        grid = list(map(lambda x:x.replace("\n",""), grid))
        grid = list(map(lambda x:x.replace(" ",""), grid))
    return grid


def extract_grid(text: str):
    grid = text.splitlines()
    grid = list(map(lambda x:x.replace("\n",""), grid))
    grid = list(map(lambda x:x.replace(" ",""), grid)) 
    return grid

def extract_words(text: str):
    words = text.splitlines()
    words = [x.strip() for x in words if x != "\n" and x != ""]
    words = list(map(lambda x:x.replace("\n",""), words))
    return words

def load_words(name: str):
    with open(name) as file:
        words = [x.strip() for x in file.readlines() if x != "\n"]
        words = list(map(lambda x:x.replace("\n",""), words))
    return words

def find_positions(grid: list[str], word:str):
    width = len(grid[0])
    height = len(grid)
    positions = []
    for row in range(height):
        for column in range(width):
            if grid[row][column] == word[0]:
                positions.append((row, column,grid[row][column]))
    return grid, positions, height, width


directions = [(1,0), (0,1), (1,1), (-1,0),(0,-1),(-1,-1), (1,-1), (-1,1)]

def find_word(word, grid):
    grid,positions,height,width = find_positions(grid, word)
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
                    word_location.append((xstart+i*d[0],ystart+i*d[1], c))
                else:
                    word_location.clear()
                    break
            else:
                return {
                    "word":word,
                    "location":word_location
                }
            continue
    return []
