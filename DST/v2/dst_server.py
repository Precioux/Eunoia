from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import uvicorn
import random
from typing import List
import jdatetime
import detectlanguage
from db.slots.funcs import *
from db.states.funcs import *

detectlanguage.configuration.api_key = "865a173a6afa544dc6043e77922fb7e9"

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "chitchat-dst-db"

# Connect to the database
conn = psycopg2.connect(
    dbname=DB_NAME,
    host=DB_HOST,
    port=DB_PORT
)
conn.autocommit = True
cursor = conn.cursor()

app = FastAPI(title="DST Server")

# Global data structures
data_dict = {}
questions = {}
defaults = {}
single_slot = []
multi_slot = []
optional_slot = []


# Define Pydantic models
class SlotItem(BaseModel):
    start: int
    end: int
    text: str
    label: str
    score: float


class IntentItem(BaseModel):
    label: str
    logit_score: float
    softmax_score: float
    min_max_normalized_score: float
    simple_normalized_score: float


class Conversation(BaseModel):
    intent: IntentItem
    top_intents: List[IntentItem]
    slots: List[SlotItem]


class UserRequest(BaseModel):
    conversation: Conversation
    whatever: bool
    conversation_id: str


# Definitions:
shamsi_b = {"فروردین": '1', "اردیبهشت": '2', "خرداد": "3", "تیر": "4", "مرداد": '5', "شهریور": '6', "مهر": '7',
            "آبان": '8', "آذر": '9', "دی": '10', "بهمن": '11', "اسفند": '12'}
miladi_fa_b = {"ژانویه": '1', "فوریه": '2', "مارچ": "3", "آپریل": "4", "می": '5', "جون": '6', "جولای": '7', "اوت": '8',
               "سپتامبر": '9', "اکتبر": '10', "نوامبر": '11', "دسامبر": '12', "آگوست": '8'}
miladi_eng_b = {"January": '1', "February": '2', "March": "3", "April": "4", "May": '5', "June": '6', "July": '7',
                "August": '8', "September": '9', "October": '10', "November": '11', "December": '12'}
ghamari_b = {"محرم": '1', "صفر": '2', "ربیع الاول": "3", "ربیع الثانی": "4", "جمادی الاول": '5', "جمادی الثانیه": '6',
             "رجب": '7', "شعبان": '8', "رمضان": '9', "شوال": '10', "ذیقعده": '11', "ذیحجه": '12'}
# #################################################################################################
shamsi = {"فروردین": '01', "اردیبهشت": '02', "خرداد": "03", "تیر": "04", "مرداد": '05', "شهریور": '06', "مهر": '07',
          "آبان": '08', "آذر": '09', "دی": '10', "بهمن": '11', "اسفند": '12'}
miladi_fa = {"ژانویه": '01', "فوریه": '02', "مارچ": "03", "آپریل": "04", "می": '05', "جون": '06', "جولای": '07',
             "اوت": '08',
             "سپتامبر": '09', "اکتبر": '10', "نوامبر": '11', "دسامبر": '12', "آگوست": '8'}
miladi_eng = {"January": '01', "February": '02', "March": "03", "April": "04", "May": '05', "June": '06', "July": '07',
              "August": '08', "September": '09', "October": '10', "November": '11', "December": '12'}
ghamari = {"محرم": '01', "صفر": '02', "ربیع الاول": "03", "ربیع الثانی": "04", "جمادی الاول": '05',
           "جمادی الثانیه": '06',
           "رجب": '07', "شعبان": '08', "رمضان": '09', "شوال": '10', "ذیقعده": '11', "ذیحجه": '12'}
# #################################################################################################
operator = {'plus', 'minus', 'multiply', 'divide', 'radical', 'power', 'redical'}
source_unit = {'unit_volume1', 'unit_length1', 'unit_surface1', 'unit_mass1'}
dest_unit = {'unit_volume2', 'unit_length2', 'unit_surface2', 'unit_mass2'}
date_names = {'امروز', 'دیروز', 'فردا', 'پس فردا', 'پریروز', 'روز', 'فعلی', 'الان', 'صبحی', 'بروز'}
alphabet = {'الف': 'ا', 'جیم': 'ج', 'دال': 'د', 'ذال': 'ذ', 'سین': 'س', 'شین': 'ش', 'صاد': 'ص', 'ضاد': 'ض', 'عین': 'ع',
            'غین': 'غ', 'قاف': 'ق', 'کاف': 'ک', 'گاف': 'گ', 'لام': 'ل', 'میم': 'م', 'نون': 'ن', 'واو': 'و'}
gc = ['gold_type', 'coin_type']
suras = {
    1: "الفاتحه",
    2: "البقره",
    3: "آل عمران",
    4: "النساء",
    5: "المائده",
    6: "الانعام",
    7: "الاعراف",
    8: "الانفال",
    9: "التوبه",
    10: "يونس",
    11: "هود",
    12: "يوسف",
    13: "الرعد",
    14: "ابراهيم",
    15: "الحجر",
    16: "النحل",
    17: "الاسراء",
    18: "الكهف",
    19: "مريم",
    20: "طه",
    21: "الانبياء",
    22: "الحج",
    23: "المؤمنون",
    24: "النور",
    25: "الفرقان",
    26: "الشعراء",
    27: "النمل",
    28: "القصص",
    29: "العنكبوت",
    30: "الروم",
    31: "لقمان",
    32: "السجده",
    33: "الاحزاب",
    34: "سبا",
    35: "فاطر",
    36: "يس",
    37: "الصافات",
    38: "ص",
    39: "الزمر",
    40: "غافر",
    41: "فصلت",
    42: "الشورى",
    43: "الزخرف",
    44: "الدخان",
    45: "الجاثيه",
    46: "الاحقاف",
    47: "محمد",
    48: "الفتح",
    49: "الحجرات",
    50: "ق",
    51: "الذاريات",
    52: "الطور",
    53: "النجم",
    54: "القمر",
    55: "الرحمن",
    56: "الواقعه",
    57: "الحديد",
    58: "المجادله",
    59: "الحشر",
    60: "الممتحنه",
    61: "الصف",
    62: "الجمعه",
    63: "المنافقون",
    64: "التغابن",
    65: "الطلاق",
    66: "التحريم",
    67: "الملك",
    68: "القلم",
    69: "الحاقه",
    70: "المعارج",
    71: "نوح",
    72: "الجن",
    73: "المزمل",
    74: "المدثر",
    75: "القيامه",
    76: "الانسان",
    77: "المرسلات",
    78: "النبأ",
    79: "النازعات",
    80: "عبس",
    81: "التكوير",
    82: "الانفطار",
    83: "المطففين",
    84: "الانشقاق",
    85: "البروج",
    86: "الطارق",
    87: "الاعلى",
    88: "الغاشيه",
    89: "الفجر",
    90: "البلد",
    91: "الشمس",
    92: "الليل",
    93: "الضحى",
    94: "الشرح",
    95: "التين",
    96: "العلق",
    97: "القدر",
    98: "البينه",
    99: "الزلزله",
    100: "العاديات",
    101: "القارعه",
    102: "التكاثر",
    103: "العصر",
    104: "الهمزه",
    105: "الفيل",
    106: "قريش",
    107: "الماعون",
    108: "الكوثر",
    109: "الكافرون",
    110: "النصر",
    111: "المسد",
    112: "الاخلاص",
    113: "الفلق",
    114: "الناس"
}

sightseeing = {
    "مراکز و مناظر دیدنی": 3,
    "مراکز تفریحی": 124,
    "مراکز و خدمات تفریحی و گردشگری": 93,
    "جاذبه های طبیعی": 98,
    "روستا و دهکده": 140,
    "جاذبه های تاریخی و فرهنگی": 188,
    "جاذبه های انسان ساخت": 196,
    "موزه": 9,
    "جاذبه های مذهبی": 119,
    "سایر": 91,
    "بناها و مجسمه های تاریخی": 16,
    "مراکز خرید": 41,
    "تفریحات ورزشی و ماجراجویانه": 104,
    "مجموعه تاریخی": 2,
    "موزه های تخصصی": 13,
    "خرید": 19,
    "مسجد": 123,
    "مجموعه ورزشی و ورزشگاه": 102,
    "دیدنی ها": 85,
    "اماکن مذهبی": 5,
    "مناظر دیدنی معروف": 15,
    "آبشار": 86,
    "میراث فرهنگی": 116,
    "موزه های تاریخی": 8,
    "کلیسا": 29,
    "بناهای باستانی": 14,
    "پل": 39,
    "سواحل": 81,
    "محله ها": 7,
    "غار": 183,
    "رزمی و بدنسازی": 97,
    "معماری خاص و باشکوه": 4,
    "امامزاده": 195,
    "خانه های تاریخی": 189,
    "تفریحات آبی و ساحلی": 68,
    "آرامگاه": 191,
    "بازارهای خیابانی": 60,
    "اماکن دیدنی": 106,
    "کوهستان": 87,
    "باغ": 125,
    "موزه های هنری": 17,
    "بازار و مراکز خرید": 120,
    "شهربازی": 89,
    "بیشتر": 10,
    "پارک های موضوعی": 12,
    "جاذبه های طبیعی و پارک ها": 132,
    "محله های تاریخی": 6,
    "چشمه": 66,
    "پارک ملی": 69,
    "آکواریوم و باغ وحش": 44,
    "جنگل": 61,
    "فعالیت های در فضای باز": 78,
    "جزایر": 54,
    "پارک های آبی": 67,
    "تفرجگاه ساحلی": 80,
    "حمام تاریخی": 166,
    "برج": 45,
    "تفریحات آبی": 11,
    "پارک جنگلی": 185,
    "مناطق حیات وحش": 70,
    "مراکز آموزشی": 79,
    "تالاب": 178,
    "اسکله ها و بندر های تفریحی": 59,
    "مراکز خدماتی": 117,
    "گالری و نمایشگاه": 18,
    "سد": 198,
    "دره": 180,
    "مناطق حفاظت شد": 184,
    "مجموعه خدمات آبی": 90,
    "پینت بال": 30,
    "هتل و مراکز اقامتی": 100,
    "سوارکاری": 99,
    "شهرک سینمایی": 88,
    "قایق سواری": 77,
    "تنگه": 181,
    "مراکز بازی": 176,
    "فرهنگسراها": 107,
    "اسکی": 214,
    "اسپا و آبدرمانی": 167,
    "تئاتر و هنرهای نمایشی": 121,
    "ورزشهای توپی": 92,
    "ورزش های راکتی": 101,
    "غذا و نوشیدنی": 31,
    "باشگاه تیراندازی": 94,
    "تاترها": 64,
    "نمایشها و کنسرتها": 65,
    "فوتبال": 112,
    "یوگا و مدیتیشن": 95,
    "کوه نوردی و اسکی": 96,
    "مزرعه گردشگری": 130,
    "آبگرم و آب معدنی طبیعی": 212,
    "موزه های نظامی": 38,
    "تفریحات هوایی": 73,
    "ترامواها": 57,
    "حمل و نقل": 58,
    "کارتینگ": 217,
    "کمپ های ورزشی": 83,
    "کوهنوردی": 215,
    "کودک": 109,
    "کویر": 187,
    "آتشکده": 193,
    "اقامتگاه بوم گردی": 118,
    "تله کابین": 200,
    "کافه و کافی شاپ": 114,
    "باغ پرندگان": 197,
    "پناهگاه حیات وحش": 186,
    "ساختمان و اداره": 108,
    "کارگاه های فرهنگی و هنری": 84,
    "مرداب": 179,
    "غواصی": 154,
    "دریاچه های مصنوعی": 177,
    "دلفیناریوم": 75,
    "والیبال": 105,
    "بانجی جامپینگ": 222,
    "مسیرهای تفریحی": 82,
    "نیایشگاه و معابد": 194,
    "فود کورت": 138,
    "کنیسه": 192,
    "زیپلاین": 216,
    "مسیرهای اتومبیل رانی": 74,
    "مجتمع تفریحی": 72,
    "اسب سواری": 71,
    "سینما و سالن های نمایش": 201,
    "فعالیت‌های تجربه گرا": 221,
    "پاراگلایدر": 129,
    "بسکتبال": 113,
    "پاراسل": 204,
    "فانوس دریایی": 62,
    "حمام سنتی": 213,
    "دوچرخه سواری": 218,
    "تورها": 76,
    "خانه مسافر و ویلا": 115,
    "سافاری و آفرود": 156,
    "موتور ATV": 157,
    "تفریحات جنگلی": 199,
    "خدمات ویژه مسافری": 53,
    "پدل بوردینگ": 211,
    "ورزش های همگانی": 111,
    "ماهیگیری": 209,
    "سالنهای فرودگاه": 52,
    "موج سواری": 205
}

def normalize(text):
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ي": "ی",
        "ك": "ک"
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def find_sura_id(sura_name):
    sura_name_normalized = normalize(sura_name)
    for key, value in suras.items():
        value_normalized = normalize(value)
        if sura_name_normalized in value_normalized or sura_name_normalized == value_normalized:
            return key
    return ''


def persian_text_to_int(text):
    # Create a dictionary to map Persian text numbers to their integer values
    numbers = {
        'صفر': 0,
        'یک': 1,
        'دو': 2,
        'سه': 3,
        'چهار': 4,
        'پنج': 5,
        'شش': 6,
        'هفت': 7,
        'هشت': 8,
        'نه': 9,
        'ده': 10,
        'یازده': 11,
        'دوازده': 12,
        'سیزده': 13,
        'چهارده': 14,
        'پانزده': 15,
        'شانزده': 16,
        'هفده': 17,
        'هجده': 18,
        'نوزده': 19,
        'بیست': 20,
        'سی': 30,
        'چهل': 40,
        'پنجاه': 50,
        'شصت': 60,
        'هفتاد': 70,
        'هشتاد': 80,
        'نود': 90,
        'صد': 100,
        'هزار': 1000
    }

    # Split the text into individual Persian numbers
    tokens = text.split()

    # Convert each Persian number to its integer value
    result = 0
    current_number = 0
    for token in tokens:
        if token in numbers:
            current_number += numbers[token]
        elif token == 'و':
            continue
        else:
            result += current_number * numbers['هزار']
            current_number = 0

    result += current_number
    return result


def is_numeric_string(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def convert_input(input_text):
    if is_numeric_string(input_text):
        return int(input_text)
    else:
        return persian_text_to_int(input_text)


# convert text to date
def convert_relative_date(relative_date_text):
    print(f'checking {relative_date_text}')
    today = jdatetime.date.today()
    if relative_date_text == 'امروز' or relative_date_text == 'بروز' or relative_date_text == 'روز' or relative_date_text == 'صبحی' or relative_date_text == 'الان' or relative_date_text == 'فعلی':
        return today
    elif relative_date_text == 'دیروز':
        return today - jdatetime.timedelta(days=1)
    elif relative_date_text == 'پریروز':
        return today - jdatetime.timedelta(days=2)
    elif relative_date_text == 'فردا':
        return today + jdatetime.timedelta(days=1)
    elif relative_date_text == 'پس فردا':
        return today + jdatetime.timedelta(days=2)
    else:
        return False


# Language detection functions
def detect_language(text):
    ans = detectlanguage.detect(text)
    print(ans[0]['language'])
    return ans


def is_persian(text):
    ans = detectlanguage.detect(text)
    if len(ans)>0:
        print(ans[0]['language'])
        return ans[0]['language'] == 'fa'
    else:
        return False


def is_english(text):
    ans = detectlanguage.detect(text)
    if len(ans)>0:
        print(ans[0]['language'])
        return ans[0]['language'] == 'en'
    else:
        return False


def date_formatter(date):
    dd = 0
    mm = 0
    yy = 0
    for d in date:
        if d in shamsi.keys():
            print(f'month recognized : {shamsi[d]}')
            mm = shamsi[d]
        else:
            d_int = int(d)
            print(type(d_int))
            if 1 <= d_int <= 31 and dd == 0:
                dd = d_int
                print(f'day recognized : {d_int}')
            else:
                # adding century
                if d_int < 100:
                    yy = d_int + 1300
                else:
                    yy = d_int
                print(f'year recognized : {d_int}')
    if yy == 0:
        yy = 1403
    print(f'{yy}-{mm}-{dd}')
    date_format = f'{yy}-{mm}-{dd}'
    return date_format


def is_date_today_or_next_week(input_date_str):
    # Parse the input date string (assuming it is in "YYYY-MM-DD" format)
    input_date = jdatetime.datetime.strptime(input_date_str, '%Y-%m-%d').date()
    print(f'input_date_str: {input_date_str}')

    # Get today's date in the Jalali calendar
    today = jdatetime.date.today()
    print(f'today: {today}')

    # Calculate the date one week from today
    next_week = today + jdatetime.timedelta(days=7)
    print(f'next_week: {next_week}')

    # Check if the input date is today or within the next week
    if input_date == today:
        return "today"
    elif today < input_date <= next_week:
        return "week"
    else:
        return False


def turn_generator(conversation_id: str) -> int:
    status = get_latest_status(conversation_id)
    if status is None:
        return 1
    elif status == 'not-completed':
        previous_turn = get_latest_turn(conversation_id)
        print('previous_turn: ', previous_turn)
        new_turn = int(previous_turn) + 1
        print('new_turn: ', new_turn)
        return new_turn
    elif status == 'completed':
        return 1


# Load data from files
def data_up():
    global data_dict
    global questions
    global defaults
    if len(questions) == 0 and len(data_dict) == 0:
        # Load ontology
        filename = 'Ontology'
        excel_file_path_data = './' + filename + '.xlsx'
        dfd = pd.read_excel(excel_file_path_data, engine='openpyxl')

        for index, row in dfd.iterrows():
            intent = row['intent']
            n = row['num']
            if n > 1:
                multi_slot.append(intent)
            elif n == 1:
                single_slot.append(intent)
            elif n == 0:
                optional_slot.append(intent)

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

        # Load questions
        filename = 'questions'
        excel_file_path_data = './' + filename + '.xlsx'
        dfd = pd.read_excel(excel_file_path_data, engine='openpyxl')

        for index, row in dfd.iterrows():
            question = row['question']
            slot = row['slot']
            if slot not in questions:
                questions[slot] = []
            questions[slot].append(question)

        filename = 'defaults'
        excel_file_path_data = './' + filename + '.xlsx'
        dfd = pd.read_excel(excel_file_path_data, engine='openpyxl')

        for index, row in dfd.iterrows():
            default = row['default']
            slot = row['slot']
            defaults[slot] = default


# DST function
def dst(intent, slots_dict, whatever_flag, cid):
    global data_dict
    global questions
    data_up()
    m = 0
    n = 0
    not_found = []
    belief_state = f'Belief State - {intent} :  '
    if intent in data_dict:
        print('DST')
        print("=================================================================")
        print(f'Intent verified : {intent}')
        m_slots = data_dict[intent]['slots']['mandatory']
        n = len(data_dict[intent]['slots']['mandatory'])
        print(f'required slots: {n} {m_slots}')
        for slot in m_slots:
            print(f'checking for {slot}')
            belief_state = belief_state + f'{slot} = '
            if slot in slots_dict:
                print(f'founded! {slots_dict[slot]}')
                belief_state = belief_state + f'{slots_dict[slot]}  '
                m = m + 1
            elif slot == 'operator':
                print('operator checking....')
                flagP = False
                for s in slots_dict:
                    if s in operator:
                        print(f'operator founded : {s}')
                        belief_state = belief_state + f'{s}'
                        flagP = True
                        m = m + 1
                if not flagP:
                    print(f'not founded')
                    not_found.append(slot)
                    belief_state = belief_state + f'not found   '
            elif slot == 'source_unit':
                flagP = False
                for s in slots_dict:
                    if s in source_unit:
                        print(f'source unit founded : {s}')
                        flagP = True
                        belief_state = belief_state + f'{s}     '
                        m = m + 1
                if not flagP:
                    print(f'not founded')
                    not_found.append(slot)
                    belief_state = belief_state + f'not found   '

            elif slot == 'dest_unit':
                flagP = False
                for s in slots_dict:
                    if s in dest_unit:
                        print(f'dest unit founded : {s}')
                        flagP = True
                        belief_state = belief_state + f'{s}'
                        m = m + 1
                if not flagP:
                    print(f'not founded')
                    not_found.append(slot)
                    belief_state = belief_state + f'not found   '

            elif slot == 'gc':
                print('gc checking....')
                flagP = False
                for s in slots_dict:
                    if s in gc:
                        print(f'gc founded : {s}')
                        belief_state = belief_state + f'{s} : {slots_dict[s]}'
                        flagP = True
                        m = m + 1
                if not flagP:
                    print(f'not founded')
                    not_found.append(slot)
                    belief_state = belief_state + f'not found   '

            else:
                print(f'not founded')
                not_found.append(slot)
                belief_state = belief_state + f'not found   '


    else:
        print(f"Intent '{intent}' not found in data_dict")

    context = ''
    status = ''
    if n == m:
        status = 'completed'
        context = ''
        print(belief_state)
    else:
        if not whatever_flag:
            status = 'not-completed'
            print(f'Asking question for {not_found[0]}')
            q = random.choice(questions[not_found[0]])
            context = {'question': q}
            print(belief_state)
        if whatever_flag:
            print(f'Setting default value to {not_found}')
            for slot in not_found:
                print(defaults[slot])
                slots_dict[slot] = defaults[slot]
                m = m + 1
            if n == m:
                status = 'completed'
            else:
                status = 'not-completed'

    # Checking intents for converters

    if intent == 'ask_restaurant':
        context = {'answer': 'عذرمیخوام من اطلاعات کافی برای پاسخگویی سوالات مرتبط با رستوران‌ها رو ندارم'}
        status = 'no-answer'

    if intent == 'calendar_convert' and status == 'completed':
        print('This is calender convert')
        flag_calender = False
        # converting source
        ans = {'source_calender': '', 'dest_calender': '', 'date': ''}
        dd = 0
        mm = 0
        yy = 0
        if slots_dict['dest_calender'] != '' and slots_dict['source_calender'] != '' and slots_dict['date'] != '':
            date = slots_dict['date'].split()
            print(date)
            if slots_dict['source_calender'] == 'شمسی' or slots_dict['source_calender'] == 'shamsi':
                print('shamsi')
                ans['source_calender'] = 'shamsi'
                for d in date:
                    if d in shamsi.keys():
                        print(f'month recognized : {shamsi[d]}')
                        mm = shamsi[d]
                    elif d in ghamari.keys() or d in miladi_fa.keys():
                        flag_calender = True
                    else:
                        d_int = int(d)
                        print(type(d_int))
                        if 1 <= d_int <= 31 and dd == 0:
                            dd = d_int
                            print(f'day recognized : {d_int}')
                        else:
                            # adding century
                            if d_int < 100:
                                yy = d_int + 1300
                            else:
                                yy = d_int
                            print(f'year recognized : {d_int}')
                if yy == 0:
                    yy = 1403
                print(f'{yy}-{mm}-{dd}')
                ans['date'] = f'{yy}-{mm}-{dd}'
            if slots_dict['source_calender'] == 'میلادی' or slots_dict['source_calender'] == 'miladi':
                print('miladi')
                ans['source_calender'] = 'miladi'
                for d in date:
                    print(f'checking {d} {type(d)}')
                    if type(d) is str and is_english(d):
                        d = d.capitalize()
                        print(d)
                    if d in miladi_fa.keys():
                        print(f'month recognized : {miladi_fa[d]}')
                        mm = miladi_fa[d]
                    elif d in miladi_eng.keys():
                        print(f'month recognized : {miladi_eng[d]}')
                        mm = miladi_eng[d]
                    elif d in shamsi.keys() or d in ghamari.keys():
                        flag_calender = True 
                    else:
                        d_int = int(d)
                        print(type(d_int))
                        if 1 <= d_int <= 31 and dd == 0:
                            dd = d_int
                            print(f'day recognized : {d_int}')
                        else:
                            yy = d_int
                            print(f'year recognized : {d_int}')
                if yy == 0:
                    yy = 2024
                print(f'{yy}-{mm}-{dd}')
                ans['date'] = f'{yy}-{mm}-{dd}'
            if slots_dict['source_calender'] == 'قمری' or slots_dict['source_calender'] == 'ghamari':
                print('ghamari')
                ans['source_calender'] = 'ghamari'
                for d in date:
                    if d in ghamari.keys():
                        print(f'month recognized : {ghamari[d]}')
                        mm = ghamari[d]
                    elif d in miladi_fa.keys() or d in shamsi.keys():
                        flag_calender = True
                    else:
                        d_int = int(d)
                        print(type(d_int))
                        if 1 <= d_int <= 31 and dd == 0:
                            dd = d_int
                            print(f'day recognized : {d_int}')
                        else:
                            yy = d_int
                            print(f'year recognized : {d_int}')
                if yy == 0:
                    yy = 1446
                print(f'{yy}-{mm}-{dd}')
                ans['date'] = f'{yy}-{mm}-{dd}'
            if slots_dict['dest_calender'] == 'قمری' or slots_dict['dest_calender'] == 'ghamari':
                ans['dest_calender'] = 'ghamari'
            if slots_dict['dest_calender'] == 'شمسی' or slots_dict['dest_calender'] == 'shamsi':
                ans['dest_calender'] = 'shamsi'
            if slots_dict['dest_calender'] == 'میلادی' or slots_dict['dest_calender'] == 'miladi':
                ans['dest_calender'] = 'miladi'
            if not flag_calender:
                context = str(ans)
            else:
                status = 'unacceptable'
                context = 'امکان تبدیل تقویم وجود ندارد اطلاعات را به درستی وارد کنید'

    if intent == 'where_to_go':
        context = "متاسفم من اطلاعات کافی درمورد مکان های دیدنی ندارم که پاسخگوی شما باشم"
        status = 'completed'

    if intent == 'city_sightseeing' and status == 'completed':
        if 'place_type' in slots_dict:
            id = sightseeing[slots_dict['place_type']]
            print(f'{slots_dict["place_type"]} : {id}')
            context = { 'city': slots_dict['city'] , 'place_type' : id}

    if intent == 'ask_azan' and status == 'completed':
        ans = {'city': slots_dict['city'], 'prayer_time': '', 'timestamp': str(jdatetime.date.today())}
        print(f'This is ask azan')
        if slots_dict['prayer_time'] == 'اذان صبح' or 'سحر':
            ans['prayer_time'] = 'azan_sobh'
        elif slots_dict['prayer_time'] == 'طلوع آفتاب':
            ans['prayer_time'] = 'toloe_aftab'
        elif slots_dict['prayer_time'] == 'اذان ظهر':
            ans['prayer_time'] = 'azan_zohre'
        elif slots_dict['prayer_time'] == 'غروب آفتاب':
            ans['prayer_time'] = 'ghorob_aftab'
        elif slots_dict['prayer_time'] == 'اذان مغرب' or 'افطار':
            ans['prayer_time'] = 'azan_maghreb'
        elif slots_dict['prayer_time'] == 'نیمه شب شرعی':
            ans['prayer_time'] = 'nime_shabe_sharie'
        elif slots_dict['prayer_time'] == 'اوقات شرعی':
            ans['prayer_time'] = ''
        context = str(ans)

    if intent == 'translate_it' and status == 'completed':
        print('This is Translate it')
        if slots_dict['sentence'] != '':
            ans = {'source_language': '', 'dest_language': '', 'sentence': slots_dict['sentence']}
            if is_persian(slots_dict['sentence']):
                ans['source_language'] += 'persian'
                ans['dest_language'] += 'english'
            elif is_english(slots_dict['sentence']):
                ans['source_language'] += 'english'
                ans['dest_language'] += 'persian'
            context = str(ans)

    # if intent == 'translate_it':
    #     print('This is Translate it')
    #     if slots_dict['sentence'] != '' and slots_dict['destination_language'] != '':
    #         ans = {'source_language': detect_language(slots_dict['sentence']),
    #                'dest_language': slots_dict['destination_language'], 'sentence': slots_dict['sentence']}
    #         context = str(ans)

    if intent == 'ask_math' and status == 'completed':
        print(f'This is ask math')
        opr = ''
        for s in slots_dict:
            if s in operator:
                opr = s
        print(f'operation: {opr}')
        if opr == 'radical' or opr == 'redical':
            num1 = convert_input(slots_dict['num1'])
            context = {'operator': 'power', 'num1': num1, 'num2': ''}
        else:
            if 'num2' in slots_dict:
                num1 = convert_input(slots_dict['num1'])
                num2 = convert_input(slots_dict['num2'])
                if opr == 'divide' and num2 == 0:
                    status = 'unacceptable'
                    context = 'امکان تقسیم بر صفر وجود ندارد'
                else:
                    context = {'operator': opr, 'num1': num1, 'num2': num2}
            else:
                print('num2 not found')
                status = 'not-completed'
                print(f'Asking question for num2')
                q = random.choice(questions['num2'])
                belief_state = belief_state + f'    num2 = not found'
                context = q
                print(belief_state)

    if intent == 'unit_convert':
        print('This is unit convert')
        if status == 'completed':
            if 'unit_volume1' in slots_dict and 'unit_volume2' in slots_dict:
                context = {'source_unit': slots_dict['unit_volume1'], 'dest_unit': slots_dict['unit_volume2']}
            elif 'unit_length1' in slots_dict and 'unit_length2' in slots_dict:
                context = {'source_unit': slots_dict['unit_length1'], 'dest_unit': slots_dict['unit_length2']}
            elif 'unit_mass1' in slots_dict and 'unit_mass2' in slots_dict:
                context = {'source_unit': slots_dict['unit_mass1'], 'dest_unit': slots_dict['unit_mass2']}
            elif 'unit_surface1' in slots_dict and 'unit_surface2' in slots_dict:
                context = {'source_unit': slots_dict['unit_surface1'], 'dest_unit': slots_dict['unit_surface2']}
            else:
                status = 'unacceptable'
                context = 'لطفا اطلاعات رو به صورت کامل و درست وارد کنید'

    if intent == 'esm_famil':
        if status == 'completed':
            ans = {'subject': slots_dict['esm_famil_subject'], 'alphabet': ''}
            if slots_dict['alphabet'] in alphabet:
                ans['alphabet'] = alphabet[slots_dict['alphabet']]
            else:
                ans['alphabet'] = slots_dict['alphabet']
            context = ans

    if intent == 'tasadofi':
        print('This is tasadofi')
        if status == 'completed':
            sp = convert_input(slots_dict['starting_point'])
            ep = convert_input(slots_dict['ending_point'])
            context = {'starting_point': sp, 'ending_point': ep}

    if intent == 'city_distance' and status == 'completed':
        context = {'source_city': slots_dict['source_city'], 'dest_city': slots_dict['dest_city']}

    if intent == 'convert_currency':
        if status == 'completed':
            context = {'source_item': slots_dict['currency'], 'dest_item': slots_dict['dest_currency']}

    if intent == 'movie_show_time':
        context = "متاسفم من اطلاعات کافی درمورد زمان پخش فیلم ها ندارم که پاسخگوی شما باشم"
        status = 'completed'

    if intent == 'price_gold' and status == 'completed':
        context = ''
        if 'gold_type' in slots_dict:
            context = {'type': 'Gold'}
        elif 'coin_type' in slots_dict:
            context = {'type': 'Coin'}

    if intent == 'get_food_energy' and status == 'completed':
        context = {'food': slots_dict['food_name']}

    if intent == 'get_food_nutrition':
        context = "متاسفم من اطلاعات کافی درمورد مواد مغذی ندارم که پاسخگوی شما باشم"
        status = 'completed'

    if intent == 'complaints' and status == 'completed':
        context = "اعتراض شما ثبت شد و به زودی به آن رسیدگی می شود."
        status = 'completed'

    # president is ok

    if intent == 'next_event_date' and status == 'completed':
        context = {'event': slots_dict['holiday']}

    if intent == 'birth_things' and status == 'completed':
        m = 0
        if slots_dict['month'] in shamsi_b:
            m = shamsi[slots_dict['month']]
        elif slots_dict['month'].capitalize() in miladi_eng_b:
            m = miladi_eng[slots_dict['month'].capitalize()]
        elif slots_dict['month'] in miladi_fa_b:
            m = miladi_fa[slots_dict['month']]
        elif slots_dict['month'] in ghamari_b:
            m = ghamari[slots_dict['month']]
        context = {'month': m}

    # city population is ok

    if intent == 'adie' and status == 'completed':
        context = {'title': slots_dict['prayer_name']}

    if intent == 'find_cinama':
        context = "متاسفم من اطلاعات کافی درمورد سینماها ندارم که پاسخگوی شما باشم"
        status = 'completed'

    if intent == 'movie_score':
        context = "متاسفم من اطلاعات کافی درمورد امتیاز فیلم ها ندارم که پاسخگوی شما باشم"
        status = 'completed'

    if intent == 'movie_genre':
        context = "متاسفم من اطلاعات کافی درمورد ژانر فیلم ها ندارم که پاسخگوی شما باشم"
        status = 'completed'

    if intent == 'movie_info':
        context = "متاسفم من اطلاعات کافی درمورد ژانر فیلم ها ندارم که پاسخگوی شما باشم"
        status = 'completed'

    # word meaning is ok

    # dictation is ok

    if intent == 'create_password' and status == 'completed':
        length = convert_input(slots_dict['length'])
        context = {'length': length}

    if intent == 'ask_weather' and 'date' in slots_dict and status == 'completed':
        date = ''
        vd = convert_relative_date(slots_dict['date'])
        if not vd:
            date = date_formatter(slots_dict['date'].split())
            print(f'formatted date: {date}')

        else:
            date = vd.strftime("%Y-%m-%d")
            print(f'date: {date}')
        dw = (is_date_today_or_next_week(date))
        datef = ''
        if dw == 'today' or dw == 'week':
            datef = dw
        context = {'city': slots_dict['city'], 'date': datef}

    if intent == 'moshaereh' and status == 'completed':
        context = {'letter': slots_dict['alphabet']}

    if intent == 'president' or intent == 'ask_capital':
        if status == 'completed':
            if slots_dict['country'] == 'کشور خودمون' or slots_dict['country'] == 'کشورمون' or slots_dict[
                'country'] == 'کشور ما':
                context = {'country': 'Iran'}
            else:
                context = {'country': slots_dict['country']}

    # ask currency is ok

    if intent == 'quran_info' and status == 'completed':
        soureh_id = find_sura_id(slots_dict['sore_name'])
        if 'num1' in slots_dict:
            context = {'soureh_id': soureh_id, 'ayeh': convert_input(slots_dict['num1'])}
        else:
            context = {'soureh_id': soureh_id, 'ayeh': ''}

    if intent == 'ask_what_to_cook' and status == 'completed':
        print('this is ask_what_to_cook')
        ingredients = slots_dict['ingredient'].split('-')
        context = {'ingredients': ingredients}

    if intent == 'get_recipe' and status == 'completed':
        context = {'food': slots_dict['food_name']}

    if intent == 'get_cooktime' and status == 'completed':
        context = {'food': slots_dict['food_name']}

    if intent == 'get_ingredients' and status == 'completed':
        context = {'food': slots_dict['food_name']}

    if intent == 'book_info' and status == 'completed':
        context = {'title': slots_dict['book_name']}

    if intent == 'telephone' and status == 'completed':
        context = {'name': slots_dict['telephone']}

    if intent == 'sheer' and status == 'completed':
        poet = ''
        if 'poet' in slots_dict:
            poet = slots_dict['poet']
        context = {'poet': poet}

    if intent == 'sing_a_song' and status == 'completed':
        context = {}

    if intent == 'bot_favorites' and status == 'completed':
        context = "من یک بات هستم و علاقمندی ندارم"
        status = 'completed'

    if intent == 'user_introduce' and status == 'completed':
        context = {}

    if intent == 'ask_sendpic' and status == 'completed':
        context = {}

    if intent == 'danestani' and status == 'completed':
        astronomy = {'کهکشان', 'منظورمه شمسی', 'سیاره', 'نجوم', 'آسمون', 'آسمان', 'آسمان شب', 'ستارگان', 'ستاره'}
        geography = {'جغرافی', 'جغرافیا', 'کشورها', 'کشور', 'قاره', 'امریکا', 'اسیا', 'آسیا', 'آمریکا', 'اروپا',
                     'آفریقا', 'افریقا', 'شهر', 'رود', 'کوه', 'دریا', 'اقیانوس', 'دشت', 'کویر', 'روستا', 'زمین'}
        subject = ''
        if 'd_subject' in slots_dict:
            if slots_dict['d_subject'] == 'تاریخ' or slots_dict['d_subject'] == 'تاریخی':
                subject = 'history'
            elif slots_dict['d_subject'] in astronomy:
                subject = 'Astronomy'
            elif slots_dict['d_subject'] in geography:
                subject = 'Geography'
            else:
                subject = 'General'
        context = {'subject': subject}

    if intent == 'ask_time' and status == 'completed':
        context = {}

    if intent == 'todate_is' and status == 'completed':
        print('This is Today is')
        print(slots_dict)
        date = ''
        if 'date' in slots_dict:
            print(slots_dict['date'])
            vd = convert_relative_date(slots_dict['date'])
            if not vd:
                date = date_formatter(slots_dict['date'].split())
                print(f'formatted date: {date}')

            else:
                date = vd.strftime("%Y-%m-%d")
                print(f'date: {date}')

        context = {'date': date}

    if intent == 'zekr' and status == 'completed':
        day = ''
        if 'day' in slots_dict:
            if slots_dict['day'] == 'شنبه':
                day = 'Saturday'
            elif slots_dict['day'] == 'یکشنبه':
                day = 'Sunday'
            elif slots_dict['day'] == 'دوشنبه':
                day = 'Monday'
            elif slots_dict['day'] == 'سه شنبه':
                day = 'Tuesday'
            elif slots_dict['day'] == 'چهارشنبه':
                day = 'Wednesday'
            elif slots_dict['dat'] == 'پنج شنبه':
                day = 'Thursday'
            elif slots_dict['day'] == 'جمعه':
                day = 'Friday'
        context = {'day': day}

    if intent == 'nahjolbalaghe' and status == 'completed':
        nahj_type = ''
        if 'nahjcat' in slots_dict:
            if slots_dict['nahjcat'] == 'حکمت' or slots_dict['nahjcat'] == 'کلمات قصار':
                nahj_type = 'wisdom'
            elif slots_dict['nahjcat'] == 'نامه':
                nahj_type = 'letter'
            elif slots_dict['nahjcat'] == 'خطبه':
                nahj_type = 'sermon'
        context = {'type': nahj_type}

    if intent == 'oos' or intent == 'offensive':
        status = 'not-completed'
        context = {'متاسفانه قادر به پاسخگویی به خواسته شما نیستم لطفا مجددا تلاش کنید'}

    print("------------------------------------------------------")

    # adding slots to slots database
    print('DATABASE')
    print("=================================================================")
    # checking for intent change:
    print(f'CID for conversation : {cid}')
    print("------------------------------------------------------")
    print('Checking if cid changed...')
    previous_cid = get_latest_conversation_id()
    if previous_cid is not None:
        print(f'previous cid: {previous_cid} cid: {cid}')
        if cid != previous_cid:
            clear_slots()
            print('slots cleared for new cid')
    print("------------------------------------------------------")
    print('Checking if intent changed...')
    latest_intent = get_latest_intent(cid)
    if latest_intent is not None:
        print(f'Latest intent: {latest_intent} - intent: {intent}')
        if latest_intent != intent and intent != 'whatever':
            clear_slots()
            print('slots cleared for new intent')
    print("------------------------------------------------------")
    for slot in slots_dict:
        if is_slot_in_columns(slot):
            print(f'adding {slot}:{slots_dict[slot]} to DB')
            update_slot(slot, slots_dict[slot])
        else:
            print(f'skipping {slot}')

    print("------------------------------------------------------")
    print('Generating turn')
    t = turn_generator(cid)
    if t:
        print(f'turn : {t}')
    print("------------------------------------------------------")
    # adding state to states database
    if intent != 'whatever':
        add_entry(cid, t, status, intent)
    else:
        if is_conversation_id_available(cid):
            intent = get_intent(cid)
            print(f'founded intent {intent} for {cid}')
            add_entry(cid, t, status, intent)
        else:
            print(f'ERROR: No conversation founded with cid {cid}')

    if context == '':
        context = str(slots_dict)

    print("------------------------------------------------------")

    result = {'status': status, 'context': context, 'intent': intent}
    print(result)
    print('*******************************************************************************************')
    return result


# Function to process user request
# Function to process user request
def process_user_request(request: UserRequest):
    global whatever_flag
    intent_label = request.conversation.intent.label.lower()
    print(f'Intent : {intent_label}')

    slots_dict = {}
    for slot in request.conversation.slots:
        slot_label = slot.label.lower()
        if slot_label in ['date', 'sentence']:
            if slot_label in slots_dict:
                slots_dict[slot_label] += ' ' + slot.text
            else:
                slots_dict[slot_label] = slot.text
        elif slot_label == 'ingredient':
            if slot_label in slots_dict:
                slots_dict[slot_label] += '-' + slot.text
            else:
                slots_dict[slot_label] = slot.text
        else:
            slots_dict[slot_label] = slot.text

    print(f'slots: {slots_dict}')
    print(f'whatever flag: {request.whatever}')
    if request.whatever:
        print('WHATEVER FOUNDED')
        whatever_flag = True
    print("------------------------------------------------------")

    # Add conversation_id to the response
    response_data = dst(intent_label, slots_dict, request.whatever, request.conversation_id)

    return response_data


# Endpoint for processing requests
@app.post("/process_request")
async def process_request(request: UserRequest):
    try:
        result = process_user_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    create_slots_table()
    create_states_table()
    uvicorn.run("dst_server:app", host="localhost", port=8080, reload=True)
