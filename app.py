from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from config import Config
import requests

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["APP_SECRET"]

# ----- Pages -----
@app.route("/")
def home():
    return render_template("home.html")
@app.route("/api/quote", methods=["GET"])
def quote():
    try:
        r = requests.get("https://zenquotes.io/api/random"); r.raise_for_status(); j=r.json()[0]
        return jsonify({"quote":j.get("q"),"author":j.get("a")})
    except: return jsonify({"quote":"Keep going — small steps matter.","author":"SoulBloom"})


@app.route("/meditation")
def meditation():
    return render_template("meditation.html")

@app.route("/mood")
def mood_log():
    return render_template("mood.html")

@app.route("/chatbot")
def chat_page():
    return render_template("chatbot.html")

@app.route("/spotify")
def spotify_page():
    return render_template("spotify.html")

@app.route("/journal")
def journal():
    return render_template("journal.html")

@app.route("/journal_copy")
def journal_copy():
    return render_template("journal_copy.html")

# ----- Chat API -----
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "message required"}), 400

    # Track conversation state
    if "introduced" not in session:
        intro = (
            "Hi there! I'm SoulBloom, your friendly AI assistant here to help you "
            "on your mental wellness journey. How are you feeling today?"
        )
        session["introduced"] = True
        return jsonify({"reply": intro})

    try:
        genai.configure(api_key=app.config["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = (
            "You are SoulBloom, a friendly AI assistant for mental wellness. "
            "Always respond empathetically and offer helpful advice. "
            "If the user shares how they feel, give encouragement or tips accordingly.\n\n"
            f"User: {message}\nBot:"
        )

        response = model.generate_content(prompt)
        reply = response.text if response.text else "Sorry, I couldn't respond."

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

# ----- Spotify Helper -----
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(url, {
        "grant_type": "client_credentials",
        "client_id": app.config["SPOTIFY_CLIENT_ID"],
        "client_secret": app.config["SPOTIFY_CLIENT_SECRET"]
    })
    return auth_response.json().get("access_token")

# ----- Spotify API -----
@app.route("/api/spotify/search")
def spotify_search():
    q = request.args.get("q")
    search_type = request.args.get("type", "track")  # default: track

    if not q:
        return jsonify({"error": "query required"}), 400

    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = f"https://api.spotify.com/v1/search?q={q}&type={search_type}&limit=10"
    r = requests.get(url, headers=headers)

    return jsonify(r.json())

# ----- Run App -----
if __name__ == "__main__":
    app.run(debug=True)



