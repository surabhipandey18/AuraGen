from flask import Flask, render_template,request, jsonify
import google.generativeai as genai
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
print("GEMINI_API_KEY loaded:", app.config.get("GEMINI_API_KEY"))
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/meditation")
def meditation():
    return render_template("meditation.html")
@app.route("/mood")
def mood_log():
    return render_template("mood.html")
@app.route("/chatbot")
def chat_page(): return render_template("chatbot.html")
@app.route("/spotify")
def spotify_page():
    return render_template("spotify.html")
@app.route("/api/spotify/search")
def spotify_search():
    q = request.args.get("q", "")
    
    return jsonify({
        "playlists": {"items":[{"name": "Calm Vibes", "external_urls": {"spotify": "https://open.spotify.com/"}}]},
        "tracks": {"items":[{"name": "Peaceful Song", "artists":[{"name":"Unknown"}], "preview_url": ""}]}
    })
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "message required"}), 400

    try:
        genai.configure(api_key=app.config["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(message)
        reply = response.text if response.text else "Sorry, I couldn't respond."
        return jsonify({"reply": reply})
    except Exception as e:
        
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

