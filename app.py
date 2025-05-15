from flask import Flask, request, jsonify
from flask_cors import CORS
from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer

app = Flask(__name__)
CORS(app)

# Initialize morphology database and analyzer
db = MorphologyDB.builtin_db()
analyzer = Analyzer(db)

# Dictionary of common grammar explanations
GRAMMAR_RULES = {
    'فعل ماضي': 'فعل ماضي مبني على السكون لاتصاله بتاء المتحرك',
    'فعل مضارع': 'فعل مضارع مرفوع وعلامة رفعه الضمة',
    'حرف جر': 'حرف جر يؤدي إلى مجرور ما بعده',
    'ضمير متصل': 'ضمير متصل مبني في محل رفع فاعل أو غيره حسب السياق',
    'اسم إشارة': 'اسم إشارة يدل على شيء معين',
    'فاعل': 'فاعل مرفوع يدل على من قام بالفعل',
    'مفعول به': 'مفعول به منصوب يدل على من وقع عليه الفعل',
    'مجرور': 'مجرور بحرف جر أو إضافة',
    'خبر': 'خبر مرفوع يتمم معنى المبتدأ',
}

# Modular function: Determine إعراب explanation per word & its analyses
def i3rab_explanation(word, analyses):
    # If no analyses, return default message
    if not analyses:
        return "لم يتم إيجاد تحليل لهذه الكلمة."

    # Pick best analysis (usually the first)
    analysis = analyses[0]

    pos = analysis.get('pos', '')
    lex = analysis.get('lex', '')
    diac = analysis.get('diac', '')
    # Morphological features
    # e.g. aspect (past/present), person, gender, number, case, etc.
    features = analysis.get('bw', '')  # Buckwalter features

    # Sample rule checks (expand this for full grammar later)
    # Verb past tense with attached ت
    if pos == 'verb' and lex.endswith('ت'):
        return GRAMMAR_RULES['فعل ماضي']

    # Verb present tense (approximate)
    if pos == 'verb' and lex.startswith('ي'):
        return GRAMMAR_RULES['فعل مضارع']

    # Prepositions (حروف الجر)
    if pos == 'prep':
        return GRAMMAR_RULES['حرف جر']

    # Attached pronouns (simplified)
    if 'prc3' in analysis:  # prc3 is usually the suffix pronoun attached
        return GRAMMAR_RULES['ضمير متصل']

    # Nouns: try to infer إعراب from suffix (very simplified)
    if pos == 'noun':
        # Detect case endings from diacritics (very basic)
        if diac.endswith('ُ'):  # Damma - رفع
            return GRAMMAR_RULES['فاعل']
        elif diac.endswith('َ'):  # Fatha - نصب
            return GRAMMAR_RULES['مفعول به']
        elif diac.endswith('ِ'):  # Kasra - جر
            return GRAMMAR_RULES['مجرور']
        else:
            return "اسم مبني أو غير معلوم الإعراب بدقة."

    # Pronouns (منفصلة)
    if pos == 'pron':
        return GRAMMAR_RULES['ضمير متصل']

    # Default fallback
    return "شرح إعرابي غير متوفر لهذه الكلمة."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sentence = data.get('sentence', '').strip()
    if not sentence:
        return jsonify({"error": "يرجى إدخال جملة صحيحة."}), 400

    words = sentence.split()
    results = []

    for word in words:
        # Analyze morphological forms
        analyses = analyzer.analyze(word)
        explanation = i3rab_explanation(word, analyses)
        results.append({
            "word": word,
            "explanation": explanation,
            "analyses": analyses  # Return analyses so frontend can optionally show full details
        })

    return jsonify({
        "sentence": sentence,
        "results": results
    })

if __name__ == '__main__':
    app.run(debug=True)
