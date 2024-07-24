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
    print('generating ID')
    id = ''
    if is_table_empty('states'):
        id = '0000'
    else:
        vid = get_latest_conversation_id()
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

    return id


# Load input file
filename = 'test'
excel_file_path_data = './' + filename + '.xlsx'
dfd = pd.read_excel(excel_file_path_data, engine='openpyxl')
cid = ''
conversation = []
flag = False

# Load ontology
filename = 'Ontology'
excel_file_path_data = './' + filename + '.xlsx'
dfo = pd.read_excel(excel_file_path_data, engine='openpyxl')
data_dict= {}

for index, row in dfo.iterrows():
    intent = row['intent']
    if intent not in data_dict:
        data_dict[intent] = {}
        data_dict[intent]['slots'] = {}
        data_dict[intent]['slots']['mandatory'] = []
        data_dict[intent]['slots']['optional'] = []
    slot1 = row['Slot 1']
    m1 = row['1-mandatory']
    def1 = row['1-default']
    slot2 = row['Slot 2']
    m2 = row['2-mandatory']
    def2 = row['2-default']
    slot3 = row['Slot 3']
    m3 = row['3-mandatory']
    def3 = row['3-default']
    slot4 = row['Slot 4']
    m4 = row['4-mandatory']
    def4 = row['4-default']
    if intent in data_dict:
        if m1 == 1:
            data_dict[intent]['slots']['mandatory'].append(slot1)
        elif slot1 != 0:
            data_dict[intent]['slots']['optional'].append(slot1)
            # defaults[slot1] = def1
        if m2 == 1:
            data_dict[intent]['slots']['mandatory'].append(slot2)
        elif slot2 != 0:
            data_dict[intent]['slots']['optional'].append(slot2)
            # defaults[slot2] = def2
        if m3 == 1:
            data_dict[intent]['slots']['mandatory'].append(slot3)
        elif slot3 != 0:
            data_dict[intent]['slots']['optional'].append(slot3)
            # defaults[slot3] = def3
        if m4 == 1:
            data_dict[intent]['slots']['mandatory'].append(slot4)
        elif slot4 != 0:
            data_dict[intent]['slots']['optional'].append(slot4)
            # defaults[slot4] = def4


for index, row in dfd.iterrows():
    original_status = ''
    whatever_flag = False
    print('Reading Row...')
    print("=================================================================")
    speaker = row['speaker']
    text = row['text']
    intent = row['intent']
    print(f'row: {speaker}, {text}, {intent}')
    slot_counter = 0
    if pd.notna(intent) and speaker == 'user':
        slots_label = data_dict[intent]["slots"]["mandatory"]
        slots = {}
        for s in slots_label:
            slots[s] = row[s]
            if row[s] != '-':
                slot_counter = slot_counter + 1
            if row[s] == 'whatever':
                whatever_flag = True
        print(f'slots: {slots}')
        if slot_counter == len(slots_label):
            original_status = 'completed'
        else:
            original_status = 'not-completed'
        print(f'original_status: {original_status}')

    print("------------------------------------------------------")
    if speaker == 'user' and pd.notna(text):
        print('Setting CID')
        print("------------------------------------------------------")
        if not flag:
            cid = conversation_ID_generator()
            flag = True
            print(f'CID set as {cid}')
        else:
            print('previous CID : {}'.format(cid))
        print("=================================================================")
        conversation.append(text)
        str_conversation = ' '.join(conversation)
        print(f'Sending to NLU:')
        print("------------------------------------------------------")
        print(str_conversation)
        result_NLU = send_NLU(str_conversation, text)
        print("------------------------------------------------------")
        print('This is NLU Result')
        print("------------------------------------------------------")
        result_NLU_json = result_NLU.json()
        print(json.dumps(result_NLU_json, indent=4, ensure_ascii=False))
        result_confirmation = (send_confirmation(result_NLU_json)).json()
        print("=================================================================")
        print('This is confirmation result')
        print("------------------------------------------------------")
        print(result_confirmation)
        # Add conversation_id to result_NLU_json
        result_NLU_json['conversation_id'] = cid
        dst_status = None
        dst_context = None
        dst_intent = None
        if result_confirmation['status'] == 'confirmed':
            result_DST = send_DST(result_NLU_json).json()
            print("=================================================================")
            print('This is DST')
            print(json.dumps(result_DST, indent=4, ensure_ascii=False))
            print("=================================================================")
            dst_status = result_DST.get('status')
            dst_context = result_DST.get('context')
            dst_intent = result_DST.get('intent')

    elif speaker == 'done':
        str_conversation = ' '.join(conversation)
        print("=================================================================")
        print(f'conversation: {str_conversation}')
        print(len(conversation))
        print('Conversation Ended!')
        flag = False
        cid = ''
        conversation.clear()
        print('*******************************************************************************************')


# Close the connection when done
def close_connection():
    conn.close()


# Close the connection
close_connection()
