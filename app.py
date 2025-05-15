from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return "فصيح backend is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sentence = data.get('sentence', '').strip()

    if not sentence:
        return jsonify({"error": "يرجى إدخال جملة."}), 400

    # Dummy example analysis response - replace with your real NLP logic
    words = sentence.split()
    response = []
    for w in words:
        response.append({
            "word": w,
            "diac": "-",      # placeholder for pronunciation
            "pos": "NOUN",    # placeholder for part of speech
            "lex": w,         # placeholder for root
            "bw": "code"      # placeholder for Buckwalter or code
        })

    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
