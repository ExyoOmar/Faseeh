from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer

app = Flask(__name__)
CORS(app)

db = MorphologyDB.builtin_db()
analyzer = Analyzer(db)

def generate_i3rab(word, analysis):
    pos = analysis.get('pos', '')
    lex = analysis.get('lex', '')
    diac = analysis.get('diac', '')
    # Basic starter إعراب rules (expand as you learn!)
    # Check for verb past tense with attached ت
    if pos == 'verb' and 'past' in analysis.get('aspect', ''):
        if word.endswith('ت'):
            return "فعل ماضي مبني على السكون لاتصاله بتاء المتحرك"
        else:
            return "فعل ماضي مبني على الفتح"
    # ضمير متصل (very basic check)
    if lex in ['ت', 'ي', 'نا', 'كم', 'هم', 'ه']:
        return f"ضمير متصل مبني في محل رفع فاعل أو مفعول به حسب موقعه"
    # حرف جر simple check
    if lex in ['الى', 'في', 'على', 'من', 'عن', 'ب', 'ك']:
        return "حرف جر"
    # اسم مجرور بـ حرف جر (very simple)
    if lex == 'حديقة':
        return "اسم مجرور بـ 'الى' وعلامة جره الكسرة الظاهرة"
    # Default fallback
    return "شرح إعرابي غير متوفر لهذه الكلمة."

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
    results = []
    for w in words:
        analyses = analyzer.analyze(w)
        if not analyses:
            results.append({
                'word': w,
                'explanation': 'لم يتم إيجاد تحليل لهذه الكلمة.'
            })
        else:
            # take first analysis for simplicity
            ana = analyses[0]
            i3rab_text = generate_i3rab(w, ana)
            results.append({
                'word': w,
                'explanation': i3rab_text
            })

    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
