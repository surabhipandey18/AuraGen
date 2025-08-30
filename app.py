from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/meditation")
def meditation():
    return render_template("meditation.html")
@app.route("/mood")
def mood_log():
    return render_template("mood.html")

if __name__ == "__main__":
    app.run(debug=True)

