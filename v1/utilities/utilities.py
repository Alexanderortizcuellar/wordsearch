import string
import random
from unidecode import unidecode


def clean_words(words: list[str]) -> list[str]:
    words = [unidecode(word) for word in words]
    words = sorted(words, key=len, reverse=True)
    words = list(map(lambda x: x.upper().strip(), words))
    words = [word.replace('"', "") for word in words]
    return words


def unfill(grid, positions):
    pass


def fill(grid):
    width = len(grid[0])
    height = len(grid)
    for row in range(height):
        for item in range(width):
            if grid[row][item] == "*":
                grid[row][item] = random.choice(string.ascii_uppercase)
    return grid


def remove_asterisks(grid) -> list[list[str]]:
    width = len(grid[0])
    height = len(grid)
    for row in range(height):
        for item in range(width):
            if grid[row][item] == "*":
                grid[row][item] = ""
    return grid


def predict_width_height(words, ratio=2.3):
    words = clean_words(words)
    if len(words) > 0:
        len_longest = len(words[0])
        letters = sum(list(map(len, words)))
        total = letters * ratio
        dimension = round(total**0.5)
        if dimension < len_longest:
            dimension = len_longest
        return dimension
    return 10
