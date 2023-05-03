import string
from random import choice,shuffle

import tabulate
from flask import Flask, redirect, render_template, request, url_for
from wordsearch import WordSearch


app = Flask(__name__)


@app.route("/", methods=["post", "get"])
def home():
    width = request.args.get("width")
    height = request.args.get("height")
    show_answers = request.args.get("answers")
    if height is None or width is None:
        width, height = 10, 10
    words = [
        "DESENMASCARAR",
        "SATISFACTION",
        "MINIMIZING",
        "ALEXANDER",
        "EXCELLENT",
        "PERDONAR",
        "ENTREGAR",
        "TOMATO",
        "PYTHON",
        "BULDOG",
        "RECIBIR",
        "MARCOS",
        "PEDRO",
        "BOXER",
        "MARIA",
        "ALEX",
        "JAMAS"
    ]
    shuffle(words)
    grid = WordSearch(words, int(width), int(height)).grid
    grid = tabulate.tabulate(grid, tablefmt="html")
    return render_template("index.html", grid=grid, width=width, height=height, words=words)


if __name__ == "__main__":
    app.run("localhost", 8080, debug=True)
