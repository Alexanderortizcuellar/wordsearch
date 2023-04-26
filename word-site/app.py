import string
from random import choice

import tabulate
from flask import Flask, redirect, render_template

app = Flask(__name__)


grid = [[choice(string.ascii_uppercase) for col in range(20)]
        for row in range(20)]
grid = tabulate.tabulate(grid, tablefmt="html")


@app.route("/")
def home():
    return render_template("index.html", grid=grid)


if __name__ == "__main__":
    app.run("localhost", 8080, debug=True)


