from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer

app = Flask(__name__)
CORS(app)

db = MorphologyDB.builtin_db()
analyzer = Analyzer(db)

def analyze_word(word):
    analyses = analyzer.analyze(word)
    if not analyses:
        return {
            'word': word,
            'diac': '',
            'pos': 'غير معروف',
            'lex': '',
            'bw': '',
            'case': '',
            'explanation': 'لم يتم إيجاد تحليل لهذه الكلمة.'
        }
    ana = analyses[0]  # take the first analysis
    # Simple إعراب explanation example (you can expand)
    case = ana.get('case', '')
    pos = ana.get('pos', '')
    explanation = f"هذه الكلمة هي {pos}"
    if case:
        explanation += f" وإعرابها حالة {case}"
    else:
        explanation += " ولا يوجد إعراب محدد."
    return {
        'word': word,
        'diac': ana.get('diac', ''),
        'pos': pos,
        'lex': ana.get('lex', ''),
        'bw': ana.get('bw', ''),
        'case': case,
        'explanation': explanation
    }

@app.route('/')
def home():
    return "فصيح backend is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sentence = data.get('sentence', '').strip()
    if not sentence:
        return jsonify({"error": "يرجى إدخال جملة."}), 400

    words = sentence.split()
    results = [analyze_word(w) for w in words]

    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
