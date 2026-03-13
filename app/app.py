from flask import Flask
import os

app = Flask(__name__)

def get_version():
    try:
        with open("version.txt", "r") as f:
            return f.read()
    except:
        return "unknown"

@app.route("/")
def home():
    version = get_version()
    return f"DevOps CI/CD Demo - Version {version}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)