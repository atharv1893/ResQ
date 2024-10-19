from flask import Flask, request, jsonify, render_template
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import re
import google.generativeai as genai
from googleapiclient.discovery import build

API_KEY = 'AIzaSyDQvp1J6Y5OpGqtX0i-OYoIHzYBFzrPm6o'
model = AutoModelForTokenClassification.from_pretrained("NeverLearn/Medical-NER-finetuned-ner")

pipe = pipeline("token-classification", model="NeverLearn/Medical-NER-finetuned-ner")

genai.configure(api_key="AIzaSyCl85XjleRXW37YnMcD33qjpHWJeCtMwls")
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/medical', methods=['POST'])
def medical_advice():
    data = request.get_json()
    text_data = data['text']

    if "youtube" in text_data.lower():
        # YouTube search code (remains unchanged)
        pass
    else:
        # Custom medical terms
        custom_terms = {
            "od": "FREQUENCY", "bid": "FREQUENCY", "tid": "FREQUENCY",
            "qid": "FREQUENCY", "prn": "FREQUENCY", "ac": "TIMING",
            "pc": "TIMING", "hs": "TIMING", "npo": "TIMING",
            "po": "WAY OF INTAKE", "pr": "WAY OF INTAKE", "iv": "WAY OF INTAKE",
            "im": "WAY OF INTAKE", "sc": "WAY OF INTAKE", "sl": "WAY OF INTAKE",
            "td": "WAY OF INTAKE", "bucc": "WAY OF INTAKE", "inh": "WAY OF INTAKE"
        }

        # Perform NER on the input text
        ner_results = pipe(text_data)
        merged_entities = []
        current_entity = None
        current_label = None

        # Function to apply custom rules based on predefined terms
        def apply_custom_rules(word):
            lower_word = word.lower()
            if lower_word in custom_terms:
                return custom_terms[lower_word]
            return None

        # Merge adjacent same-label entities and apply custom rules
        for entity in ner_results:
            word = entity['word'].strip('▁')  # Clean up word
            label = entity['entity']

            # Check if word matches any custom rule
            custom_label = apply_custom_rules(word)
            if custom_label:
                label = custom_label

            # Merge entities with the same label
            if label == current_label:
                current_entity += " " + word
            else:
                if current_entity is not None:
                    merged_entities.append((current_entity, current_label))
                current_entity = word
                current_label = label

        if current_entity is not None:
            merged_entities.append((current_entity, current_label))

        # Add custom terms not caught by the NER model
        for word in text_data.split(" "):
            label = apply_custom_rules(word)
            if label:
                merged_entities.append((word, label))

        # Gather all entities for final output
        all_entities = [entity for entity, _ in merged_entities]

        # Prepare message for Gemini AI, using all entities at once
        if all_entities:
            chat_session = model.start_chat(history=[])

            # Generate care advice based on extracted entities
            # care_message = f"{text_data}. Don't provide me any medical advice but just tell me what care should I take for {', '.join(all_entities)}."

            care_message = (
                f"{text_data}.Dont provide me any medical advice , but just tell me what care should I take for/"
                f" {', '.join(all_entities)}.Dont start with basic intro, directly start with your answer.Give answer in html"
                f" format Keep 2 line space between heading and remaining tags, and list tags as a sub points.")

            care = chat_session.send_message(care_message)

            # Generate dietary advice for recovery
            # diet_message = f"What should I eat to speed up my recovery if I am experiencing {', '.join(all_entities)}?"

            diet_message = (
                f"What should I eat to speed up my recovery process if I am having {text_data}.Dont start "
                f"with basic intro, directly start with your answer.Give answer in html format. Keep 2 line space"
                f" between heading and remaining tags, and list tags as a sub points.")

            diet = chat_session.send_message(diet_message)

            # Generate home remedies based on the conditions
            # home_remedies_message = f"What home remedies can help with {', '.join(all_entities)}?"

            home_remedies_message = (f"What all home remedies you suggest for my {text_data}.Dont start "
                                     f"with basic intro, directly start with your answer. Give answer in html format."
                                     f" Keep 2 line space between heading and remaining tags, and list tags as a sub points.")

            home_remedies = chat_session.send_message(home_remedies_message)

            final_output = care.text + '<br><br>' + diet.text + '<br><br>' + home_remedies.text
            return jsonify({'results': final_output})

        else:
            return jsonify({'results': 'No relevant entities found.'})

@app.route('/maps')
def maps():
    return render_template('maps.html')
if __name__ == '__main__':
    app.run(debug=True)
