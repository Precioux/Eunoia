import pandas as pd
from DST.db.states.funcs import *
import requests
import json

# Define URLs for the servers
url_NLU = "http://localhost:8092/predict"
url_confirmation = "http://localhost:8000/check_intent/"
url_DST = "http://localhost:8080/process_request"

def send_NLU(data, turn):
    global url_NLU
    params = {'conversation': data, 'turn': turn}
    response = requests.get(url_NLU, params=params)
    return response

def send_confirmation(data):
    global url_confirmation
    response = requests.post(url_confirmation, json=data)
    return response

def send_DST(data):
    global url_DST
    response = requests.post(url_DST, json=data)
    return response

def conversation_ID_generator():
    print('###################################')
    print('generating ID')
    id = ''
    if is_table_empty('states'):
        id = '0000'
    else:
        vid = get_latest_conversation_id()
        print(f'id: {vid}')
        n = int(vid)
        nid = n + 1
        if nid < 10:
            id = '000' + str(nid)
        elif nid < 100:
            id = '00' + str(nid)
        elif nid < 1000:
            id = '0' + str(nid)
        else:
            id = str(nid)

    print('###################################')
    return id

# Load ontology
filename = 'multi'
excel_file_path_data = './' + filename + '.xlsx'
dfd = pd.read_excel(excel_file_path_data, engine='openpyxl')
cid = ''
conversation = []

for index, row in dfd.iterrows():
    speaker = row['speaker']
    text = row['text']
    intent = row['intent']
    print(f'row: {speaker}, {text}, {intent}')
    flag = False
    if speaker != 'done' and pd.notna(text):
        if not flag:
            cid = conversation_ID_generator()
            flag = True
            print(f'cid set as {cid}')
        else:
            print('previous cid : {}'.format(cid))
        if speaker == 'user':
            conversation.append(text)
            str_conversation = ' '.join(conversation)
            result_NLU = send_NLU(str_conversation, text)
            print('This is NLU Result')
            result_NLU_json = result_NLU.json()
            print(json.dumps(result_NLU_json, indent=4, ensure_ascii=False))
            result_confirmation = (send_confirmation(result_NLU_json)).json()
            print('This is confirmation result')
            print(result_confirmation)
            # Add conversation_id to result_NLU_json
            result_NLU_json['conversation_id'] = cid
            print(json.dumps(result_NLU_json, indent=4, ensure_ascii=False))
            if result_confirmation['status'] == 'confirmed':
                result_DST = send_DST(result_NLU_json).json()
                print('This is DST')
                print(json.dumps(result_DST, indent=4, ensure_ascii=False))
            else:
                print('cannot send to DST Server')

    elif speaker == 'done':
        str_conversation = ' '.join(conversation)
        print(f'conversation: {str_conversation}')
        print(len(conversation))
        print('Conversation Ended!')
        cid = ''
        conversation.clear()
        print('***************************************')
        print('')