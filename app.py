from flask import Flask,  jsonify ,request
from flask_cors import CORS
import json
import os


app = Flask(__name__)
CORS(app,origins=["*"])

SCORES_FILE:str="scores.json"

def load_scores() -> dict:
    if not os.path.exists(SCORES_FILE):
        return {"guah":float("inf")}
    with open(SCORES_FILE,"r") as f:
        return json.load(f)
    
def save_scores(scores) -> None:
    with open(SCORES_FILE,"w") as f:
        json.dump(scores,f)
@app.route("/")
def index():
    return "backend good"
@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.get_json()
    name = data.get('name')
    time = data.get('time')
    updated = False

    scores = load_scores()
    if name not in scores or time < scores[name]:
        scores[name] = time
        save_scores(scores)

    return jsonify({'status': 'success',
                    "updated":updated,
                    "best_time":scores[name]
                })
@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    scores = load_scores()
    return jsonify(scores)
if __name__ == "__main__":
    porti = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=porti)