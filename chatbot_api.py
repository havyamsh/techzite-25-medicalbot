
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

MODEL_NAME = "ktrapeznikov/biobert_v1.1_pubmed_squad_v2"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)
    med_qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Model loading failed: {e}")
    med_qa_pipeline = None  # Avoid crashing the API

MEDICAL_KNOWLEDGE = """
Influenza, also known as the flu, is a viral infection that attacks the respiratory system. Symptoms include fever, cough, sore throat, runny nose, muscle aches, and fatigue.

COVID-19 is a contagious disease caused by the SARS-CoV-2 virus. Common symptoms include fever, dry cough, fatigue, loss of taste or smell, and difficulty breathing.

Migraine is a neurological condition characterized by severe headaches, often accompanied by nausea, vomiting, and sensitivity to light and sound.

Gastroenteritis, often called the stomach flu, is an inflammation of the stomach and intestines. Symptoms include vomiting, diarrhea, stomach cramps, and nausea.

The common cold is a viral infection of the upper respiratory tract. Symptoms include sneezing, runny nose, mild cough, and sore throat.
"""

def analyze_symptoms(user_input):
    if not med_qa_pipeline:
        print("Pipeline is not initialized!")
        return None  # Avoid calling a non-existent model

    try:
        # Construct the question
        question = f"What conditions might cause these symptoms: {user_input}?"

        # Get the model's answer
        result = med_qa_pipeline(
            context=MEDICAL_KNOWLEDGE,
            question=question
        )
        
        print("Model output:", result)  # Debug log

        # Check if the model's confidence is too low
        if result['score'] < 0.1:
            return None
        
        # Extract the answer and check for known conditions
        answer = result['answer'].lower()
        conditions = [
            c for c in ["influenza", "covid-19", "migraine", "gastroenteritis", "common cold"]
            if c in answer
        ]
        
        return conditions if conditions else None
        
    except Exception as e:
        print(f"Error in analyze_symptoms: {e}")
        return None

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        print("Received data:", data)  # Debug log

        user_input = data.get("user_input", "").strip().lower()
        if not user_input:
            return jsonify({"response": "Please describe your symptoms."})

        # Analyze symptoms
        conditions = analyze_symptoms(user_input)
        print("Identified conditions:", conditions)  # Debug log

        if not conditions:
            return jsonify({
                "response": "I couldn't identify any specific conditions. I recommend consulting a doctor. Would you like to book an appointment?",
                "action": "book_appointment"
            })

        response = (
            f"Your symptoms might relate to {', '.join(conditions)}. "
            "Would you like me to book an appointment?"
        )

        return jsonify({
            "response": response,
            "conditions": conditions,
            "action": "book_appointment"
        })

    except Exception as e:
        print(f"Chat error: {e}")  # Print error in logs
        return jsonify({"response": "Sorry, there was an error. Please try again later."})

if __name__ == "__main__":
    app.run(debug=True)