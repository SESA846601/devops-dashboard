from flask import Flask, render_template
import datetime

app = Flask(__name__)

def get_version():
    try:
        with open("version.txt", "r") as f:
            return f.read()
    except:
        return "unknown"

@app.route("/")
def dashboard():
    version = get_version()
    deployment_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "dashboard.html",
        version=version,
        deployment_time=deployment_time
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)