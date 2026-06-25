# -*- coding: utf-8 -*-
import os
import sqlite3
import urllib.request
import urllib.parse
import json
from functools import wraps
from flask import Flask, render_template, request, Response, send_from_directory, redirect
import sys, os
# Add parent directory to import bot module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bot import get_ai_resp

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='templates')

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

def send_telegram_msg(chat_id, text):
    if not TELEGRAM_BOT_TOKEN:
        return

@app.route('/bot_log')
def get_bot_log():
    try:
        with open('../bot.log', 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/plain')
    except Exception as e:
        return str(e)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    try:
        data = urllib.parse.urlencode(payload).encode('utf-8')
        urllib.request.urlopen(url, data=data)
    except Exception as e:
        print(f"Error sending TG message: {e}")

import sys
import time
ADMIN_USER = "aziz67876578"
ADMIN_PASS = "67596854903876584"

# Robust DB Path resolution for development and standalone EXE packaging
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    # Try looking for nemis.db in the EXE folder, or in the parent folder
    possible_paths = [
        os.path.join(exe_dir, "nemis.db"),
        os.path.join(os.path.dirname(exe_dir), "nemis.db"),
        os.path.join(exe_dir, "website", "nemis.db")
    ]
    DB_PATH = possible_paths[0]
    for path in possible_paths:
        if os.path.exists(path):
            DB_PATH = path
            break
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nemis.db")

def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    return Response(
    'Вход в Админ-панель Abdulaziz Nemis AI\n'
    'Пожалуйста, введите логин и пароль.', 401,
    {'WWW-Authenticate': 'Basic realm="Admin Access"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Web assistant UI page
@app.route('/assistant')
def assistant_page():
    return render_template('assistant.html')

# API endpoint for AI queries
@app.route('/assistant/query', methods=['POST'])
def assistant_query():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    lang = data.get('lang', 'ru')
    if not question:
        return {"error": "Empty question"}, 400
    answer = get_ai_resp(question, lang)
    return {"answer": answer}

@app.route('/api/user_data', methods=['POST'])
def get_or_create_user_data():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    name = data.get('name', 'User')
    username = data.get('username', '')
    if not uid:
        return {"error": "Missing user_id"}, 400
    
    conn = get_db_connection()
    user = conn.execute("SELECT name, username, phone, current_lesson, selected_level, last_activity, sub, sub_expire, webapp_password, webapp_surname FROM users WHERE id=?", (uid,)).fetchone()
    
    # Check if subscription has expired
    if user and user['sub'] != 'none' and user['sub_expire']:
        try:
            exp_time = time.mktime(time.strptime(user['sub_expire'], '%Y-%m-%d %H:%M:%S'))
            if time.time() > exp_time:
                conn.execute("UPDATE users SET sub='none' WHERE id=?", (uid,))
                conn.commit()
                # Inform the user via bot that their sub expired
                try:
                    import os, urllib.request, urllib.parse
                    bot_token = os.getenv("BOT_TOKEN")
                    msg = "⚠️ 1 oy o'tdi, darslarni davom ettirish uchun to'lov qilishingiz kerak.\nIltimos, darslarni davom ettirish uchun to'lov qiling."
                    p = {'chat_id': uid, 'text': msg, 'parse_mode': 'Markdown'}
                    urllib.request.urlopen(f"https://api.telegram.org/bot{bot_token}/sendMessage", data=urllib.parse.urlencode(p).encode('utf-8'))
                except:
                    pass
                user = dict(user)
                user['sub'] = 'none'
        except Exception as e:
            print(f"Error checking sub expiry: {e}")
            
    if not user:
        # Create user with default values
        conn.execute("INSERT OR IGNORE INTO users (id, name, username, step, current_lesson, last_activity) VALUES (?,?,?, 'main', 1, NULL)", (uid, name, username))
        conn.commit()
        res = {
            "name": name,
            "surname": "",
            "username": username,
            "phone": "",
            "current_lesson": 1,
            "selected_level": None,
            "last_activity": None,
            "sub": "none",
            "webapp_registered": False
        }
    else:
        res = {
            "name": user['name'] or name,
            "surname": user['webapp_surname'] or "",
            "username": user['username'] or username,
            "phone": user['phone'] or "",
            "current_lesson": user['current_lesson'] or 1,
            "selected_level": user['selected_level'],
            "last_activity": user['last_activity'],
            "sub": user['sub'] or "none",
            "webapp_registered": bool(user['webapp_password'])
        }
    conn.close()
    return res

@app.route('/api/webapp_register', methods=['POST'])
def webapp_register():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    name = data.get('name', '').strip()
    surname = data.get('surname', '').strip()
    password = data.get('password', '').strip()
    
    if not uid or not name or not password:
        return {"error": "Barcha maydonlarni to'ldiring"}, 400
        
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE id=?", (uid,)).fetchone()
    if not user:
        conn.execute("INSERT INTO users (id, name, webapp_surname, webapp_password, step, current_lesson) VALUES (?, ?, ?, ?, 'main', 1)", (uid, name, surname, password))
    else:
        conn.execute("UPDATE users SET name=?, webapp_surname=?, webapp_password=? WHERE id=?", (name, surname, password, uid))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.route('/api/webapp_login', methods=['POST'])
def webapp_login():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    password = data.get('password', '').strip()
    
    if not uid or not password:
        return {"error": "Parolni kiriting"}, 400
        
    conn = get_db_connection()
    user = conn.execute("SELECT webapp_password FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    
    if not user or not user['webapp_password']:
        return {"error": "Foydalanuvchi topilmadi. Iltimos ro'yxatdan o'ting."}, 404
        
    if user['webapp_password'] != password:
        return {"error": "Parol noto'g'ri. Iltimos qayta urinib ko'ring."}, 401
        
    return {"status": "ok"}

@app.route('/api/webapp_reset_password', methods=['POST'])
def webapp_reset_password():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    new_password = data.get('password', '').strip()
    
    if not uid or not new_password:
        return {"error": "Yangi parolni kiriting"}, 400
        
    conn = get_db_connection()
    conn.execute("UPDATE users SET webapp_password=? WHERE id=?", (new_password, uid))
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

@app.route('/api/save_level', methods=['POST'])
def save_level():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    level = data.get('level', '').strip()
    if not uid or not level:
        return {"error": "Missing parameters"}, 400
    
    # If starting A1, redirect to A1_Prep first (30 lessons)
    db_level = 'A1_Prep' if level == 'A1' else level
    
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    conn.execute("UPDATE users SET selected_level=?, current_lesson=1, last_activity=? WHERE id=?", (db_level, now_str, uid))
    conn.commit()
    conn.close()
    return {"status": "ok", "last_activity": now_str, "selected_level": db_level}

@app.route('/api/complete_lesson', methods=['POST'])
def complete_lesson():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    if not uid:
        return {"error": "Missing user_id"}, 400
    
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    user = conn.execute("SELECT current_lesson, selected_level FROM users WHERE id=?", (uid,)).fetchone()
    if not user:
        conn.close()
        return {"error": "User not found"}, 404
    
    current_lesson = user['current_lesson'] or 1
    selected_level = user['selected_level'] or 'A1'
    max_lessons = 60
    
    if current_lesson >= max_lessons:
        conn.close()
        return {"status": "exam_ready", "current_lesson": current_lesson, "max_lessons": max_lessons}
        
    next_lesson = current_lesson + 1
    conn.execute("UPDATE users SET current_lesson=?, last_activity=? WHERE id=?", (next_lesson, now_str, uid))
    conn.commit()
    conn.close()
    return {"status": "ok", "current_lesson": next_lesson, "last_activity": now_str}

@app.route('/api/get_lesson', methods=['POST'])
def get_lesson():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    if not uid:
        return {"error": "Missing user_id"}, 400
        
    conn = get_db_connection()
    user = conn.execute("SELECT current_lesson, selected_level, lang FROM users WHERE id=?", (uid,)).fetchone()
    if not user:
        conn.close()
        return {"error": "User not found"}, 404
        
    current_lesson = user['current_lesson'] or 1
    selected_level = user['selected_level'] or 'A1'
    lang = user['lang'] or 'ru'
    conn.close()
    
    requested_lesson = data.get('lesson_number')
    if requested_lesson:
        try:
            lesson_to_load = int(requested_lesson)
        except ValueError:
            lesson_to_load = current_lesson
    else:
        lesson_to_load = current_lesson
    
    lang_map = {'uz': "Uzbek", 'ru': "Russian", 'en': "English", 'de': "German"}
    explain_lang = lang_map.get(lang, "Russian")
    
    if int(lesson_to_load) == 1:
        lesson_text = """
📖 **1-Dars: Salomlashish va tanishuv (Begrüßung und Kennenlernen)**

Assalomu alaykum! Nemis tilini o‘rganishga bag‘ishlangan ilk darsimizga xush kelibsiz. Ushbu 10 daqiqalik dars davomida biz nemis tilida salomlashish, ism so‘rash va qayerdan ekanligimizni aytishni o‘rganamiz.
Har bir iborani ovoz chiqarib qaytarishni unutmang!

**1. 💡 Grammatik / Salomlashish (Begrüßung)**
Nemis tilida ham xuddi o‘zbek tilidagidek vaziyatga qarab rasmiy va norasmiy (do‘stona) salomlashish shakllari mavjud.

**Hallo!** [Xallo!] — Salom! (Do‘stona shakli)
**Guten Tag!** [Guten Tag!] — Kun xayr! / Assalomu alaykum! (Rasmiy shakli)
**Guten Morgen!** [Guten Morgen!] — Hayrli tong! (Ertalab aytiladi)
**Guten Abend!** [Guten Abend!] — Hayrli kech! (Kechki payt aytiladi)

**2. 🗣️ Wortschatz / Tanishuv: Ism so‘rash (Kennenlernen)**
Do‘stona shakli (Yaqinlar, tengdoshlar yoki bolalar uchun):
**Wie heißt du?** [Vi xayst du?] — Sening isming nima?
**Ich heiße...** [Ix xayse...] — Mening ismim...

Rasmiy shakli (Kattalar, notanish kishilar yoki ish joyida):
**Wie heißen Sie?** [Vi xaysen Zi?] — Sizning ismingiz nima?

**Kelib chiqishi: Qayerdansiz? (Herkunft)**
Nemis tilida "dan" qo‘shimchasi *aus* predlogi orqali ifodalanadi.
**Woher kommst du?** [Voxer komst du?] — Sen qayerdansan?
**Woher kommen Sie?** [Voxer kommen Zi?] — Siz qayerdansiz?
**Ich komme aus Usbekistan.** [Ix komme aus Usbekistan.] — Men O‘zbekistondanman.

**Yoqimli so‘zlar va Xayrlashish (Höflichkeit und Abschied)**
**Freut mich!** [Froyt mix!] — Tanishganimdan xursandman!
**Danke!** [Danke!] — Rahmat!
**Tschüss!** [Chyus!] — Xayr! / Ko‘rishguncha! (Do‘stona shakli)
**Auf Wiedersehen!** [Auf viderzeen!] — Xayr! / Salomat bo‘ling! (Rasmiy shakli)

**3. 🎭 Dialog / Kichik muloqot (Amaliyot)**
O‘rgangan bilimlarimizni amalda tekshiramiz. Quyidagi dialogni o‘qib ko‘ring:

**A:** Hallo! Wie heißt du? [Xallo! Vi xayst du?] — Salom! Sening isming nima?
**B:** Hallo! Ich heiße Anvar. Und du? [Xallo! Ix xayse Anvar. Und du?] — Salom! Mening ismim Anvar. Sening-chi?
**A:** Ich heiße Max. Woher kommst du, Anvar? [Ix xayse Maks. Voxer komst du, Anvar?] — Mening ismim Maks. Qayerdansan, Anvar?
**B:** Ich komme aus Usbekistan. [Ix komme aus Usbekistan.] — Men O‘zbekistondanman.
**A:** Freut mich! [Froyt mix!] — Tanishganimdan xursandman!
**B:** Tschüss! [Chyus!] — Xayr!

**4. 📝 Übungen**
Yuqoridagi so'zlarni o'z ismingiz bilan qo'llab, ovoz chiqarib takrorlang.

**5. 🎯 Leseaufgabe / Praktisches Aufgabe**
Yuqoridagi dialogni qayta o'qib chiqing. Agar talaffuz yoki so'zlarning ma'nosini yaxshi tushunmagan bo'lsangiz, istalgan iborani nusxalab oling va AI Repetitor bilan suhbat (Chat) bo'limiga yuborib, tushuntirib berishini so'rang.
"""
    elif int(lesson_to_load) == 2:
        lesson_text = """
📖 **2-Dars: Nemis tili alifbosi va o‘qish qoidalari (Das Alphabet)**

Birinchi darsimiz muvaffaqiyatli yakunlandi! Bugun biz nemis tili alifbosi va eng muhim o‘qish qoidalari bilan tanishamiz. Nemis tilida so‘zlar qanday yozilsa, deyarli shunday o‘qiladi, biroq bir nechta maxsus harflar va birikmalar bor. Ularni eslab qolish juda oson!

**1. Alifbo (Das Alphabet)**
Nemis alifbosida 26 ta asosiy harf bor. Keling, ularning nomlanishi va aytilishini ko‘rib chiqamiz:
A a — [A]
B b — [Be]
C c — [Tse]
D d — [De]
E e — [E]
F f — [Ef]
G g — [Ge]
H h — [Xa]
I i — [I]
J j — [Yot] (o‘zbekcha "Y" tovushini beradi)
K k — [Ka]
L l — [El]
M m — [Em]
N n — [En]
O o — [O]
P p — [Pe]
Q q — [Ku]
R r — [Er]
S s — [Es]
T t — [Te]
U u — [U]
V v — [Fau] (ko‘pincha "F" kabi o‘qiladi)
W w — [Ve] (o‘zbekcha "V" kabi o‘qiladi)
X x — [Iks]
Y y — [Yupsilon]
Z z — [Tset] (o‘zbekcha "S" va "T" qorishmasi, "Ts" kabi o‘qiladi)

**2. Maxsus nemis harflari (Umlaut va Eszett)**
Nemis tilida faqat ushbu tilga xos bo‘lgan 4 ta maxsus harf mavjud. Ularni yaxshilab eslab qoling:
**Ä ä (A-umlaut)** — [E] kabi o‘qiladi. Misol: Mädchen [Medxen] — qiz bola.
**Ö ö (O-umlaut)** — [Yo] kabi yumshoq o‘qiladi (lablar oldinga cho‘ziladi). Misol: schön [shyon] — go‘zal.
**Ü ü (U-umlaut)** — [Yu] kabi yumshoq o‘qiladi. Misol: tschüss [chyus] — xayr.
**ß (Eszett)** — bu harf har doim ikkita "ss" kabi o‘qiladi. Misol: heißen [xaysen] — nomlanmoq.

**3. Unli harflar birikmasi (O‘qish qoidalari)**
Ikki unli harf yonma-yon kelsa, yangi tovush hosil qiladi:
**ei** — [Ay] deb o‘qiladi:
Nein [Nayn] — Yo‘q
Mein [Mayn] — Mening

**eu va äu** — [Oy] deb o‘qiladi:
Euro [Oyro] — Yevro
Häuser [Xoyzer] — Uylar

**ie** — [I] tovushini uzunroq qilib o‘qitadi:
Auf Wiedersehen [Auf viderzeen] — Xayrlashish iborasi.

**4. Undosh harflar birikmasi**
Nemis tilida eng ko‘p uchraydigan undosh birikmalar:
**ch** — [X] kabi o‘qiladi:
Ich [Ix] — Men

**sch** — [Sh] kabi o‘qiladi:
Schule [Shule] — Maktab

**st va sp** — so‘z boshida [Sht] va [Shp] deb o‘qiladi:
Sprechen [Shprexen] — Gapirmoq
Straße [Shtrasse] — Ko‘cha

**5. 📝 Übungen (O‘qishni mashq qilamiz)**
Quyidagi so‘zlarni qoidaga asosan ovoz chiqarib o‘qib ko‘ring:
Nein [Nayn] — Yo‘q
Deutsch [Doych] — Nemis tili
Sprechen [Shprexen] — Gapirmoq
Freund [Froynd] — Do‘st
Weiß [Vays] — Oq

**6. 🎯 Leseaufgabe / Praktisches Aufgabe**
Dars yakuni: Barakalla! Endi siz nemischa so‘zlarni to‘g‘ri o‘qishni bilasiz. 
Yuqoridagi so'zlarni yana bir marta takrorlang. Agar talaffuzga qiynalsangiz, so'zni nusxalab olib "AI Tutor" ga yuboring, u sizga qanday aytilishini ovozli tarzda jo'natadi! Keyingi darsda biz 0 dan 20 gacha sanashni o‘rganamiz.
"""
    else:
        prompt = (
            f"Provide a structured, detailed German language lesson for Level {selected_level}, Lesson {lesson_to_load} out of 60. "
            f"The lesson explanations, grammar rules, and vocabulary translations must be entirely in {explain_lang}. "
            "Keep it highly educational, comprehensive, well-formatted, and easy to read. Structure it with these EXACT headers:\n"
            f"📖 Lektion {lesson_to_load}: [Lesson Topic Name]\n\n"
            "1. 💡 Grammatik (Comprehensive grammar explanation with multiple examples. Include reading rules if applicable)\n"
            "2. 🗣️ Wortschatz (Extensive vocabulary list including essential verbs, nouns, and phrases with translations)\n"
            "3. 🎭 Dialog (A conversational dialogue demonstrating the topic)\n"
            "4. 📝 Übungen (3 quick practice exercises)\n"
            "5. 🎯 Leseaufgabe / Praktisches Aufgabe (Provide a dedicated, clear German text related to the topic. It MUST be a reading text like a story, a letter, or an article. Keep the text entirely in German. Underneath the text, add a note in {explain_lang} saying: 'If you don't understand this text, or want me to check your reading, copy the text and send it to the AI Chat Tutor. You can ask the tutor to explain it to you or listen to you read.')\n\n"
            "Provide solutions to the exercises at the very end of the lesson."
        )
        lesson_text = get_ai_resp(prompt, lang)
        
    return {"lesson_text": lesson_text, "current_lesson": current_lesson, "loaded_lesson": lesson_to_load, "selected_level": selected_level}

@app.route('/api/pass_exam', methods=['POST'])
def pass_exam():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    if not uid:
        return {"error": "Missing user_id"}, 400
        
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    user = conn.execute("SELECT selected_level FROM users WHERE id=?", (uid,)).fetchone()
    if not user:
        conn.close()
        return {"error": "User not found"}, 404
        
    current_level = user['selected_level'] or 'A1'
    next_level = current_level
    
    if current_level == 'A1_Prep' or current_level == 'A1':
        next_level = 'A2'
    elif current_level == 'A2':
        next_level = 'B1'
    elif current_level == 'B1':
        next_level = 'B2'
    elif current_level == 'B2':
        next_level = 'B2'
        
    conn.execute("UPDATE users SET selected_level=?, current_lesson=1, last_activity=? WHERE id=?", (next_level, now_str, uid))
    conn.commit()
    conn.close()
    return {"status": "ok", "selected_level": next_level, "current_lesson": 1, "last_activity": now_str}

@app.route('/api/fail_exam', methods=['POST'])
def fail_exam():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('user_id', '')).strip()
    if not uid:
        return {"error": "Missing user_id"}, 400
        
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    user = conn.execute("SELECT selected_level FROM users WHERE id=?", (uid,)).fetchone()
    if not user:
        conn.close()
        return {"error": "User not found"}, 404
        
    conn.execute("UPDATE users SET current_lesson=1, last_activity=? WHERE id=?", (now_str, uid))
    conn.commit()
    conn.close()
    return {"status": "ok", "current_lesson": 1, "last_activity": now_str}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def upgrade_schema():
    conn = get_db_connection()
    try:
        conn.execute("ALTER TABLE users ADD COLUMN webapp_password TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN webapp_surname TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

upgrade_schema()

@app.route('/admin')
@requires_auth
def admin_panel():
    conn = get_db_connection()
    users_count = conn.execute("SELECT count(*) FROM users").fetchone()[0]
    banned_count = conn.execute("SELECT count(*) FROM users WHERE banned=1").fetchone()[0]
    payments_total = conn.execute("SELECT sum(amount) FROM payments").fetchone()[0] or 0
    hacker_logs = conn.execute("SELECT * FROM hacker_logs ORDER BY id DESC LIMIT 10").fetchall()
    
    # Check if extra_ai column exists
    try:
        conn.execute("ALTER TABLE users ADD COLUMN extra_ai INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
        
    users = conn.execute("SELECT * FROM users ORDER BY rowid DESC LIMIT 50").fetchall()
    extra_buyers = conn.execute("SELECT count(*) FROM users WHERE extra_ai > 0").fetchone()[0]
    
    conn.close()
    
    return render_template('admin.html', 
                           users_count=users_count, 
                           banned_count=banned_count,
                           payments_total=payments_total,
                           hacker_logs=hacker_logs,
                           users=users,
                           extra_buyers=extra_buyers)

@app.route('/grant_access', methods=['POST'])
@requires_auth
def grant_access():
    user_id = request.form.get('user_id')
    action = request.form.get('action')
    
    conn = get_db_connection()
    if action in ['standard', 'platinum', 'vip']:
        expire_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 30 * 86400))
        conn.execute("UPDATE users SET sub=?, sub_expire=?, unlocked='[]', ai_count=0 WHERE id=?", (action, expire_date, user_id))
        
        # Get phone number to log in payments table
        u = conn.execute("SELECT phone FROM users WHERE id=?", (user_id,)).fetchone()
        phone = u['phone'] if u and u['phone'] else '-'
        amount = 60000 if action == 'standard' else (120000 if action == 'platinum' else 2000000)
        pay_date = time.strftime('%Y-%m-%d %H:%M:%S')
        conn.execute("INSERT INTO payments (user_id, amount, date, phone, tariff) VALUES (?,?,?,?,?)", (user_id, amount, pay_date, phone, action))
    elif action == 'extra100':
        conn.execute("UPDATE users SET extra_ai = extra_ai + 100 WHERE id=?", (user_id,))
    elif action == 'extra200':
        conn.execute("UPDATE users SET extra_ai = extra_ai + 200 WHERE id=?", (user_id,))
        
    conn.commit()
    conn.close()
    
    return redirect('/admin')

@app.route('/unban', methods=['POST'])
@requires_auth
def unban_user():
    user_id = request.form.get('user_id')
    conn = get_db_connection()
    # Разблокируем, сбрасываем нарушения и "сжигаем" тариф
    conn.execute("UPDATE users SET banned=0, violations=0, sub='none', extra_ai=0 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/reject_payment', methods=['POST'])
@requires_auth
def reject_payment():
    user_id = request.form.get('user_id')
    conn = get_db_connection()
    user = conn.execute("SELECT lang FROM users WHERE id=?", (user_id,)).fetchone()
    lang = user['lang'] if user and user['lang'] else 'ru'
    
    msgs = {
        'ru': "❌ Ваш платеж отклонен. Пожалуйста, проверьте данные или свяжитесь с поддержкой.",
        'uz': "❌ To'lovingiz rad etildi. Iltimos, ma'lumotlarni tekshiring yoki qo'llab-quvvatlash xizmatiga murojaat qiling.",
        'en': "❌ Your payment was rejected. Please check the details or contact support."
    }
    send_telegram_msg(user_id, msgs.get(lang, msgs['ru']))
    conn.execute("UPDATE users SET step='main' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/fake_payment', methods=['POST'])
@requires_auth
def fake_payment():
    user_id = request.form.get('user_id')
    conn = get_db_connection()
    
    msg = (
        "⚠️ *ВНИМАНИЕ / DIQQAT / ATTENTION*\n\n"
        "🇷🇺 Вы отправили фальшивый чек. По закону Узбекистана это называется мошенничеством, и ваш аккаунт был зафиксирован. Если у вас есть претензии, пишите админу в техподдержку.\n\n"
        "🇺🇿 Siz soxta chek yubordingiz. O'zbekiston qonunchiligiga ko'ra bu firibgarlik deb ataladi va sizning hisobingiz qayd etildi. Agar e'tirozlaringiz bo'lsa, texnik yordamga murojaat qiling.\n\n"
        "🇺🇸 You sent a fake receipt. According to the laws of Uzbekistan, this is called fraud, and your account has been recorded. If you have any claims, contact tech support."
    )
    send_telegram_msg(user_id, msg)
    
    # Блокируем пользователя
    conn.execute("UPDATE users SET banned=1, step='banned' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

def keep_alive():
    while True:
        try:
            import urllib.request
            urllib.request.urlopen("https://nemis-ai.onrender.com/")
        except:
            pass
        import time
        time.sleep(14 * 60)

import threading
threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    print("Abdulaziz Nemis AI Web Server starting on http://localhost:5000")
    print("Admin Panel available at http://localhost:5000/admin")
    app.run(host='0.0.0.0', port=5000, debug=False)
