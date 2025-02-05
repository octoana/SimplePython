import os
from flask import request, Flask
import re


# Clear-text logging of sensitive information
# did not trigger an alert in codeQL somehow...
print(f"[INFO] Environment: {os.environ}")

# attempt to trigger a warning in codeQL 
# Regular expression injection
@app.route("/direct")
def direct():
    unsafe_pattern = request.args["pattern"]
    re.search(unsafe_pattern, "")


@app.route("/compile")
def compile():
    unsafe_pattern = request.args["pattern"]
    compiled_pattern = re.compile(unsafe_pattern)
    compiled_pattern.search("")
