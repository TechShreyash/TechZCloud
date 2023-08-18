import os
from time import sleep

for i in ["index.html", "file.html"]:
    with open(f"templates/{i}") as f:
        text = (
            f.read()
            .replace("index.css", "minindex.css")
            .replace("index.js", "minindex.js")
        )

    while "  " in text:
        text = text.replace("  ", " ")

    while "\n" in text:
        text = text.replace("\n", "")

    with open(f"templates/min{i}", "w") as f:
        f.write(text)
        print("minified", i)

import os

for i in ["index.css"]:
    with open(f"static/{i}") as f:
        text = f.read()
    while "  " in text:
        text = text.replace("  ", " ")
    while "\n" in text:
        text = text.replace("\n", "")
    with open(f"static/min{i}", "w") as f:
        f.write(text)

print("minify js file manually")
