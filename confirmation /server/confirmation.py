from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.preprocessing import PolynomialFeatures
import json
import uvicorn
import numpy as np
import joblib
import os
import pandas as pd
import random

# Check if the model file exists
model_path = 'final_model2.pkl'
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file {model_path} not found. Please ensure the file is in the correct location.")

# Load the model
model = joblib.load(model_path)

app = FastAPI(title='Confirmation server')


class IntentRequest(BaseModel):
    conversation: dict
    whatever: bool


# Define a function to preprocess the input data
def preprocess_input(api_response):
    top_intents = api_response["conversation"]["top_intents"]
    if len(top_intents) < 2:
        return None

    features = []
    first_intent = top_intents[0]
    second_intent = top_intents[1]

    top_intent_1_softmax = float(first_intent["softmax_score"])
    top_intent_1_normalized = float(first_intent["simple_normalized_score"])
    top_intent_2_softmax = float(second_intent["softmax_score"])
    top_intent_2_normalized = float(second_intent["simple_normalized_score"])
    simple_normalized_diff = abs(top_intent_1_normalized - top_intent_2_normalized)

    features.extend([
        top_intent_1_softmax,
        top_intent_1_normalized,
        top_intent_2_softmax,
        top_intent_2_normalized,
        simple_normalized_diff,
        top_intent_1_softmax * top_intent_2_softmax,  # interaction_1
        top_intent_1_normalized * top_intent_2_normalized,  # interaction_2
        top_intent_1_softmax * top_intent_1_normalized,  # interaction_3
        top_intent_2_softmax * top_intent_2_normalized  # interaction_4
    ])

    # Create polynomial features
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    poly_features = poly.fit_transform(np.array([[
        top_intent_1_softmax,
        top_intent_1_normalized,
        top_intent_2_softmax,
        top_intent_2_normalized,
        simple_normalized_diff
    ]]))
    poly_features = poly_features[0]

    # Append polynomial features to the original features
    features.extend(poly_features)

    return np.array([features])


# Define a function to predict the status
def predict_status(features):
    if features is None:
        return "unclear"

    probabilities = model.predict_proba(features)
    predicted_class = np.argmax(probabilities, axis=1)[0]

    return ["confirmed", "doubt", "unclear"][predicted_class]


def question_generator(first_intent, second_intent):
    questions = []
    intents = {}
    # unrecognized questions
    filename = 'unrecognized'
    excel_file_path_data = './' + filename + '.xlsx'
    dfd = pd.read_excel(excel_file_path_data, engine='openpyxl')
    for index, row in dfd.iterrows():
        q = row['question']
        questions.append(q)

    filename = 'intents'
    excel_file_path_data = './' + filename + '.xlsx'
    dfd = pd.read_excel(excel_file_path_data, engine='openpyxl')
    for index, row in dfd.iterrows():
        intent = row['english']
        per = row['persian']
        intents[intent] = per

    random_question = random.choice(questions)
    first_intent_per = intents[first_intent]
    second_intent_per = intents[second_intent]
    ya = 'یا'
    final_question = random_question + " " + first_intent_per + " " + ya + " " + second_intent_per
    return final_question


def check_intent(status, api_response):
    response_data = api_response["conversation"]
    result = {'status': status, 'intent1': '', 'intent2': '', 'context': ''}

    top_intents = response_data.get("top_intents", [])
    first_intent_label = top_intents[0]["label"]
    second_intent_label = top_intents[1]["label"]
    if status == "confirmed":
        result['intent1'] = first_intent_label
    elif status == "doubt":
        result['intent1'] = first_intent_label
        result['intent2'] = second_intent_label
        question = question_generator(first_intent_label, second_intent_label)
        result['context'] = question
    elif status == "unclear":
        result['context'] = "عذرمیخوام متوجه منظورتون نشدم."

    return result


@app.post("/check_intent/")
async def analyze_intent(intent_request: IntentRequest):
    try:
        input_data = preprocess_input(intent_request.dict())
        print('preprocessing')
        print(input_data)
        status = predict_status(input_data)
        print(f'status: {status}')
        result = check_intent(status, intent_request.dict())

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("confirmation:app", host="0.0.0.0", port=8000, reload=True)