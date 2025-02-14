from flask import request, Flask
import re


@app.route("/direct")
def direct():
    unsafe_pattern = request.args["pattern"]
    re.search(unsafe_pattern, "")
