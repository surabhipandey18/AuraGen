from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import google.generativeai as genai
from config import Config
import requests
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["APP_SECRET"]

# ----- Pages -----
#home
@app.route("/")
def home():
    return render_template("home.html")
@app.route("/api/quote", methods=["GET"])
def quote():
    try:
        r = requests.get("https://zenquotes.io/api/random"); r.raise_for_status(); j=r.json()[0]
        return jsonify({"quote":j.get("q"),"author":j.get("a")})
    except: return jsonify({"quote":"Keep going — small steps matter.","author":"SoulBloom"})

#meditation page
@app.route("/meditation")
def meditation():
    return render_template("meditation.html")

#mood tracker page
@app.route("/mood")
def mood_log():
    return render_template("mood.html")

#chatbot page
@app.route("/chatbot")
def chat_page():
    return render_template("chatbot.html")

#spotify
@app.route("/spotify")
def spotify_page():
    return render_template("spotify.html")

#journal page
@app.route("/journal")
def journal():
    return render_template("journal.html")

#new journal
@app.route("/journal_copy")
def journal_copy():
    return render_template("journal_copy.html", edit_mode=False)

#save journal
@app.route("/save_journal", methods=["POST"])
def save_journal():
    title = request.form["title"]
    mood = request.form["mood"]
    content = request.form["content"]
    os.makedirs("journals", exist_ok=True)
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + safe_title + ".txt"

    filepath = os.path.join("journals", filename)
    # Save entry into text file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"Mood: {mood}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")
        f.write(content)

        flash("Journal entry saved successfully!", "success")
        return redirect(url_for("get_journal_entries"))

#see the journal entries
@app.route("/journal_entries", methods=["GET"])
def get_journal_entries():
    entries = []
    os.makedirs("journals", exist_ok=True)

    for filename in os.listdir("journals"):
        filepath = os.path.join("journals", filename)
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            title = lines[0].replace("Title: ", "").strip() if len(lines) > 0 else ""
            mood = lines[1].replace("Mood: ", "").strip() if len(lines) > 1 else ""
            date_str = lines[2].replace("Date: ", "").strip() if len(lines) > 2 else ""
            content = "".join(lines[4:]) if len(lines) > 4 else ""

            try:
                date_created = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except:
                date_created = None

            entries.append({
                "filename": filename,
                "title": title,
                "mood": mood,
                "date_created": date_created,
                "content": content
            })

    # Sort by newest first
    entries.sort(key=lambda x: x["date_created"] or datetime.min, reverse=True)

    return render_template("old_entries.html", entries=entries)

#edit journal
@app.route("/journal/edit/<filename>")
def edit_entry(filename):
    filepath = os.path.join("journals", filename)
    if not os.path.exists(filepath):
        flash("Entry not found!", "error")
        return redirect(url_for("get_journal_entries"))

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        title = lines[0].replace("Title: ", "").strip() if len(lines) > 0 else ""
        mood = lines[1].replace("Mood: ", "").strip() if len(lines) > 1 else ""
        content = "".join(lines[4:]) if len(lines) > 4 else ""

    return render_template("journal_copy.html",
                           filename=filename,
                           title=title,
                           mood=mood,
                           content=content)


@app.route("/journal/update/<filename>", methods=["POST"])
def update_journal(filename):
    title = request.form["title"]
    mood = request.form["mood"]
    content = request.form["content"]

    filepath = os.path.join("journals", filename)
    if not os.path.exists(filepath):
        flash("Journal not found", "error")
        return redirect(url_for("get_journal_entries"))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"Mood: {mood}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")
        f.write(content)

    flash("Journal entry updated successfully!", "success")
    return redirect(url_for("get_journal_entries"))

#delete journal
@app.route("/journal/delete/<filename>", methods=["POST"])
def delete_entry(filename):
    filepath = os.path.join("journals", filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash("Journal entry deleted successfully!", "success")
    else:
        flash("Journal entry not found!", "error")

    return redirect(url_for("get_journal_entries"))

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

