import os
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

# Calculate evaluation metrics
def calculate_accuracy(df, column):
    correct_predictions = df[df[column] == df[f'expected_{column}']].shape[0]
    total_predictions = df.shape[0]
    return correct_predictions / total_predictions if total_predictions > 0 else 0

# Iterate over all Excel files in the data folder
data_folder = 'data/single/'
for file in os.listdir(data_folder):
    if file.endswith('.xlsx'):
        print(f'Loading {file}')
        print("=================================================================")
        filename = os.path.join(data_folder, file)
        dfd = pd.read_excel(filename, engine='openpyxl')
        cid = ''
        conversation_schedule1 = []
        conversation_schedule2 = []
        flag = False

        # Load ontology
        filename_ontology = 'Ontology.xlsx'
        dfo = pd.read_excel(filename_ontology, engine='openpyxl')
        data_dict = {}

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
                if m2 == 1:
                    data_dict[intent]['slots']['mandatory'].append(slot2)
                elif slot2 != 0:
                    data_dict[intent]['slots']['optional'].append(slot2)
                if m3 == 1:
                    data_dict[intent]['slots']['mandatory'].append(slot3)
                elif slot3 != 0:
                    data_dict[intent]['slots']['optional'].append(slot3)
                if m4 == 1:
                    data_dict[intent]['slots']['mandatory'].append(slot4)
                elif slot4 != 0:
                    data_dict[intent]['slots']['optional'].append(slot4)

        # Initialize a list to store results
        results = []

        for index, row in dfd.iterrows():
            original_status = ''
            whatever_flag_original = False
            print('Reading Row...')
            print("=================================================================")
            speaker = row['speaker']
            text = row['text']
            original_intent = row['intent']
            print(f'row: {speaker}, {text}, {original_intent}')
            slot_counter = 0
            original_slots = []
            if pd.notna(original_intent) and speaker == 'user':
                slots_label = data_dict[original_intent]["slots"]["mandatory"]
                slots = {}
                print(slots_label)
                for s in slots_label:
                    slots[s] = row[s]
                    if row[s] != '-':
                        slot_counter += 1
                        original_slots.append(s)
                    if row[s] == 'whatever':
                        whatever_flag_original = True
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
                conversation_schedule1.append(str(text))
                conversation_schedule2.append(str(text))
                str_conversation_schedule1 = ' '.join(conversation_schedule1)
                str_conversation_schedule2 = ' '.join(conversation_schedule2)
                print(f'Sending to NLU:')
                print("------------------------------------------------------")
                print(str_conversation_schedule1)
                result_NLU = send_NLU(str_conversation_schedule1, text)
                print("------------------------------------------------------")
                print('This is NLU Result')
                print("------------------------------------------------------")
                result_NLU_json = result_NLU.json()
                print(json.dumps(result_NLU_json, indent=4, ensure_ascii=False))
                nlu_slots = []
                if len(result_NLU_json['conversation']['slots']) > 0:
                    for slot in result_NLU_json['conversation']['slots']:
                        if slot not in nlu_slots:
                            nlu_slots.append(slot['label'])
                whatever_flag_NLU = result_NLU_json['whatever']
                whatever = 0
                if whatever_flag_NLU == whatever_flag_original:
                    whatever = 1
                slot_check = 0
                for slot in nlu_slots:
                    if slot in original_slots:
                        slot_check += 1
                if len(original_slots) > 0:
                    slot_percentage = slot_check / len(original_slots)
                else:
                    if len(original_slots) == 0 and slot_check == 0:
                        slot_percentage = 1

                result_confirmation = (send_confirmation(result_NLU_json)).json()
                print("=================================================================")
                print('This is confirmation result')
                print("------------------------------------------------------")
                print(result_confirmation)
                confirmed_intent = result_confirmation.get('intent1')
                confirmation_status = result_confirmation.get('status')
                # Add conversation_id to result_NLU_json
                result_NLU_json['conversation_id'] = cid
                dst_status = None
                dst_context = None
                dst_intent = None
                if confirmation_status == 'confirmed':
                    result_DST = send_DST(result_NLU_json).json()
                    print("=================================================================")
                    print('This is DST')
                    print(json.dumps(result_DST, indent=4, ensure_ascii=False))
                    print("=================================================================")
                    dst_status = result_DST.get('status')
                    dst_context = result_DST.get('context')
                    dst_intent = result_DST.get('intent')

                # Append results
                status_flag = 0
                if original_status == dst_status:
                    status_flag = 1
                intent_flag = 0
                if original_intent == confirmed_intent:
                    intent_flag = 1
                results.append([cid, text, original_intent, confirmed_intent, intent_flag, original_slots, nlu_slots, slot_percentage, whatever_flag_original, whatever_flag_NLU, whatever, original_status, dst_status, status_flag, dst_context])
            elif speaker == 'done':
                full_conversation_schedule1 = ' '.join(conversation_schedule1)
                full_conversation_schedule2 = ' '.join(conversation_schedule2)
                print("=================================================================")
                print(f'conversation: {full_conversation_schedule1}')
                print(len(conversation_schedule1))
                print('Conversation Ended!')
                flag = False
                cid = ''
                conversation_schedule1.clear()
                conversation_schedule2.clear()
                print('*******************************************************************************************')

        # Convert results to DataFrame
        df_columns = ['cid', 'text', 'original_intent', 'confirmed_intent', 'intent_flag', 'original_slots', 'NLU_slots', 'slot_percentage', 'whatever_original', 'whatever_NLU', 'whatever_check', 'original_status', 'DST_status', 'status_flag', 'DST_result']
        df_results = pd.DataFrame(results, columns=df_columns)

        print(df_results.head())

        # Save the DataFrame to an Excel file
        excel_output_path = 'results2/results-' + file + '.xlsx'
        df_results.to_excel(excel_output_path, index=False)

# Close the connection when done
def close_connection():
    conn.close()

# Close the connection
close_connection()
