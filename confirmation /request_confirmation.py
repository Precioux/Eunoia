import requests

# Define the URL of the confirmation server
url = "http://localhost:8000/check_intent/"

# Define the input data
data = {
    "conversation": {
        "intent": {
            "label": "city_distance",
            "logit_score": "14.513713836669922",
            "softmax_score": "0.9989056587219238",
            "min_max_normalized_score": "1.0",
            "simple_normalized_score": "0.265685111284256"
        },
        "top_intents": [
            {
                "label": "city_distance",
                "logit_score": "14.513713836669922",
                "softmax_score": "0.9989056587219238",
                "min_max_normalized_score": "1.0",
                "simple_normalized_score": "0.265685111284256"
            },
            {
                "label": "tehran_metro_info",
                "logit_score": "6.802395343780518",
                "softmax_score": "0.000447240803623572",
                "min_max_normalized_score": "0.31824249029159546",
                "simple_normalized_score": "0.12452327460050583"
            },
            {
                "label": "oos",
                "logit_score": "6.064477920532227",
                "softmax_score": "0.00021382965496741235",
                "min_max_normalized_score": "0.25300323963165283",
                "simple_normalized_score": "0.11101510375738144"
            },
            {
                "label": "tasadofi",
                "logit_score": "5.099951267242432",
                "softmax_score": "8.150404028128833e-05",
                "min_max_normalized_score": "0.167729452252388",
                "simple_normalized_score": "0.09335867315530777"
            },
            {
                "label": "ask_weather",
                "logit_score": "4.252612113952637",
                "softmax_score": "3.492887844913639e-05",
                "min_max_normalized_score": "0.09281621873378754",
                "simple_normalized_score": "0.07784745842218399"
            },
            {
                "label": "city_sightseeing",
                "logit_score": "4.251783847808838",
                "softmax_score": "3.4899941965704784e-05",
                "min_max_normalized_score": "0.09274299442768097",
                "simple_normalized_score": "0.07783229649066925"
            },
            {
                "label": "ask_job_experience",
                "logit_score": "3.6118063926696777",
                "softmax_score": "1.8402906789560802e-05",
                "min_max_normalized_score": "0.0361626036465168",
                "simple_normalized_score": "0.06611699610948563"
            },
            {
                "label": "ask_capital",
                "logit_score": "3.5135037899017334",
                "softmax_score": "1.6679923646734096e-05",
                "min_max_normalized_score": "0.027471672743558884",
                "simple_normalized_score": "0.064317487180233"
            },
            {
                "label": "proverb",
                "logit_score": "3.314483404159546",
                "softmax_score": "1.36697508423822e-05",
                "min_max_normalized_score": "0.009876284748315811",
                "simple_normalized_score": "0.060674261301755905"
            },
            {
                "label": "nahjolbalaghe",
                "logit_score": "3.202773332595825",
                "softmax_score": "1.2224900274304673e-05",
                "min_max_normalized_score": "0.0",
                "simple_normalized_score": "0.058629319071769714"
            }
        ],
        "slots": [
            {
                "start": 8,
                "end": 13,
                "text": "تهران",
                "label": "source_city",
                "score": "0.9997884631156921"
            }
        ]
    },
    "whatever": True
}


# Send the POST request to the server
response = requests.post(url, json=data)

# Print the response from the server
print(response.json())