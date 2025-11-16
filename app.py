from flask import Flask,  jsonify ,request
from flask_cors import CORS
import json
import os
import requests
from dotenv import load_dotenv
import sys
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
app = Flask(__name__)
CORS(app,origins=["*"])

SCORES_FILE:str="scores.json"

def load_scores() -> dict:
	url = f"{SUPABASE_URL}/rest/v1/get_leaderboard"
	headers = {
		"apikey": SUPABASE_API_KEY,
		"Authorization": f"Bearer {SUPABASE_API_KEY}"
	}
	response = requests.get(url, headers=headers)
	data = response.json()
	return {entry["username"]: entry["score"] for entry in data}

    
def save_scores(name: str, score: float) -> None:
	url = f"{SUPABASE_URL}/rest/v1/leaderboard"
	headers = {
		"apikey": SUPABASE_API_KEY,
		"Authorization": f"Bearer {SUPABASE_API_KEY}",
		"Content-Type": "application/json",
		"Prefer": "resolution=merge-duplicates"
	}
	payload = {
		"username": name,
		"score": score
	}
	requests.post(url, headers=headers, json=payload)
@app.route("/")
def health():
    return "OK",200
@app.route("/submit_score", methods=["POST"])
def submit_score():
	data = request.get_json()
	name = data.get("name")
	time = data.get("time")
	updated = False

	scores = load_scores()
	first_ever = name not in scores
	if first_ever or time < scores.get(name, float("inf")):
		save_scores(name, time)
		updated = True

	best_time = time if first_ever else min(time, scores[name])

	return jsonify({
		"status": "success",
		"updated": updated,
		"best_time": best_time,
		"first_ever": first_ever
	})
@app.route('/leaderboard', methods=['GET'])
def leaderboard():
	scores = load_scores()
	sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1]))
	return jsonify(sorted_scores)
if __name__ == "__main__":
    porti = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=porti)