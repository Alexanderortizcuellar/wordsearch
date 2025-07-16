# Word Search Game

A desktop word search game built with Python and PyQt5. This application allows users to select a topic and play a word search puzzle.

## Features

*   **Topic Selection:** Choose from a variety of word search topics.
*   **Interactive Gameplay:** Click and drag to highlight and find words in the grid.
*   **Progress Tracking:** See which words you have found and how many are left.
*   **Dynamic Puzzle Generation:** Puzzles are generated on the fly.
*   **Database Integration:** Topics and words are managed using a SQLite database.

## Getting Started

### Prerequisites

*   Python 3
*   PyQt5

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Alexanderortizcuellar/wordsearch.git
    cd wordsearch
    ```

2.  **Install the dependencies:**
    ```bash
    pip install PyQt5
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

## File Structure

*   `app.py`: The main application file containing the PyQt5 UI and game logic.
*   `generator.py`: Contains the `WordSearchGenerator` class for creating the word search puzzles.
*   `manager.py`: (Purpose to be determined, likely for managing game state or data).
*   `wordsearch.db`: The SQLite database that stores the topics and words for the puzzles.
*   `style.qss` and `managerstyle.qss`: Stylesheets for the application's UI.
*   `topic_card.py`: A custom widget for displaying the topic cards in the menu.
*   `words/`: A directory containing word lists.
*   `v1/`: Contains an older version of the application.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.
