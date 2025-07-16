import random
from string import ascii_uppercase
from dataclasses import dataclass, asdict
from rich import print

# import json
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1)]
DIRECTION_MAP = {
    "down": (1, 0),
    "right": (0, 1),
    "diagonal_down_right": (1, 1),
    "up": (-1, 0),
    "left": (0, -1),
    "diagonal_up_left": (-1, -1),
    "diagonal_down_left": (1, -1),
    "diagonal_up_right": (-1, 1),
}

EMPTY = " "


@dataclass
class Schema:
    width: int
    height: int
    words: list[str]
    directions: list[tuple[int, int]]
    grid: list[list[str]]
    positions: dict[str, list[tuple[str, int, int]]]
    dict = asdict


class WordSearchGenerator:
    def __init__(self) -> None:
        self.width = 0
        self.height = 0
        self.words = []
        self.directions = DIRECTIONS
        self.retry = True
        self.grid = []
        self.schema: Schema = Schema(
            self.width,
            self.height,
            self.words,
            self.directions,
            self.grid,
            positions={},
        )

    def generate(
        self,
        width: int = 10,
        height: int = 10,
        words: list[str] = [],
        directions: list[str] = list(DIRECTION_MAP.keys()),
        auto_dimensions: bool = False,
    ) -> dict:
        """
        Generate a Word Search puzzle.

        Args:
            width (int): Width of the grid (number of columns).
            height (int): Height of the grid (number of rows).
            words (list[str]): List of words to include in the puzzle.
            directions (list[str]): Allowed directions for word placement.
                Must be one or more of:
                - "down"
                - "right"
                - "diagonal_down_right"
                - "up"
                - "left"
                - "diagonal_up_left"
                - "diagonal_down_left"
                - "diagonal_up_right"

        Returns:
            dict: A dictionary containing the puzzle grid and metadata.
        """

        self.width = width
        self.height = height
        if auto_dimensions:
            self.width, self.height = self.predict_width_height(words)
        self.words = self.clean_words(words)
        self.directions = self.map_directions(directions)
        self.grid = self._make_grid()
        self.schema = Schema(
            self.width,
            self.height,
            self.words,
            self.directions,
            self.grid,
            positions={},
        )
        for word in self.words:
            rand_direction = self.directions[random.randint(0, len(self.directions) - 1)]
            self.try_fit_word(word, rand_direction)
        self._fill_grid()
        return self.schema.dict()

    def _make_grid(self) -> list[list[str]]:
        """
        Creates the WordSearch grid using
        specified dimensions
        """
        return [[EMPTY for _ in range(self.width)] for _ in range(self.height)]

    def map_directions(self, directions: list[str]) -> tuple[int, int]:
        return tuple(DIRECTION_MAP[direction] for direction in directions)

    def _find_candidates(self) -> list[tuple[int, int]]:
        candidates = []
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] == EMPTY:
                    candidates.append((row, col))
        return candidates

    def _retry(self, word: str) -> tuple[bool, list[tuple[str, int, int]]]:
        candidates = self._find_candidates()
        positions_found: list[tuple[str, int, int]] = []
        for candidate in candidates:
            for direction in self.directions:
                positions_found.clear()
                ystart = candidate[0]
                xstart = candidate[1]
                for index, char in enumerate(word):
                    position_y = ystart + index * direction[0]
                    position_x = xstart + index * direction[1]
                    if not self._check_bounds(position_y, position_x):
                        break
                    if not self._is_available(char, position_y, position_x):
                        break
                    positions_found.append((char, position_y, position_x))
                else:
                    self.place_word(word, positions_found)
                    print("\u2705" + f" added {word}")
                    return True, positions_found
        return False, positions_found

    def try_fit_word(self, word: str, direction: tuple[int, int]):
        targets_used: list[tuple[int, int]] = []
        positions_found: list[tuple[str, int, int]] = []
        attempts = 0
        found = False
        while attempts < 1000:
            positions_found.clear()
            xstart = random.randint(0, self.width)
            ystart = random.randint(0, self.height)
            # print(f"_______\nystart: {ystart}\txstart: {xstart}\n________\n")
            if (ystart, xstart) in targets_used:
                # print(f"{(ystart, xstart)} used already")
                attempts += 1
                continue
            targets_used.append((ystart, xstart))
            for index, char in enumerate(word):
                position_y = ystart + index * direction[0]
                position_x = xstart + index * direction[1]
                # print(f"index: [{index}] y: {position_y} x: {position_x} char: {char}")
                if not self._check_bounds(position_y, position_x):
                    # print(
                    #     f"index: [{index}] y: {position_y} x: {position_x} char: {char} => failed"
                    # )
                    break
                if not self._is_available(char, position_y, position_x):
                    # print(
                    #     f"index: [{index}] y: {position_y} x: {position_x} char: {char} => failed"
                    # )
                    break
                positions_found.append((char, position_y, position_x))
            else:
                # print(positions_found)
                self.place_word(word, positions_found)
                print("\u2705" + f" added {word}")
                found = True
                break
            attempts += 1
        if not found:
            # print(f"<===[ retrying ({word}) ]===>")
            added, _ = self._retry(word)
            if not added:
                print("\u274c" + f" Failed to add {word}")

    def place_word(self, word: str, positions: list[tuple[str, int, int]]) -> bool:
        for position in positions:
            self.grid[position[1]][position[2]] = position[0]
            self.schema.positions[word] = positions
        return True

    def _check_bounds(self, position_y: int, position_x: int) -> bool:
        """
        Check if the index is within
        grid bounds:
        """
        bounds = [
            position_x >= 0 and position_y >= 0,
            position_x < self.width,
            position_y < self.height,
        ]
        return all(bounds)

    def _is_available(self, char: str, position_y: int, position_x: int) -> bool:
        """
        check if the position is available or
        is same char as the current one.
        """
        if (
            self.grid[position_y][position_x] == EMPTY
            or self.grid[position_y][position_x] == char
        ):
            return True
        return False

    def show(self):
        for row in self.grid:
            print(" ".join(row))

    def _fill_grid(self) -> None:
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] == EMPTY:
                    self.grid[row][col] = random.choice(ascii_uppercase)

    def clean_words(self, words: list[str]) -> list[str]:
        cleaned_words = list(
            sorted(map(self._clean_word, words), key=len, reverse=True)
        )
        return cleaned_words

    def _clean_word(self, word: str) -> str:
        word_cleaned = word.strip().upper()
        return word_cleaned

    def predict_width_height(self, words, ratio=1.5) -> tuple[int, int]:
        words = self.clean_words(words)
        if len(words) > 0:
            len_longest = len(words[0])
            letters = sum(list(map(len, words)))
            total = letters * ratio
            dimension = round(total**0.5)
            if dimension < 10:
                return 10, 10
            if dimension < len_longest:
                dimension = len_longest
            return dimension, dimension
        return 10, 10
