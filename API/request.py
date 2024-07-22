import requests
import json


url = "http://localhost:8092/predict"
params = {'conversation': 'من از تهران میخوام برم سفر چقد راهه؟ فرقی نداره یه شهرو همینطوری بگو', 'turn':'فرقی نداره یه شهرو همینطوری بگو'}
response = requests.get(url, params=params)
result = response.json()

# response2 = requests.post("http://localhost:8080/process_request", json=result)
# print(response2.json())
# Pretty print the JSON response
print(json.dumps(result, indent=4, ensure_ascii=False))