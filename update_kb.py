import re

with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_kb1 = """        kb = [
            [{"text": "🔍 Проверка чеков"}, {"text": "📊 Статистика"}],
            [{"text": "🚨 Атака"}, {"text": "🔍 Атака детально"}],
            [{"text": "📈 Аналитика"}, {"text": "💰 Финансы"}],
            [{"text": "👥 Участники"}, {"text": "🎬 Видео контент"}],
            [{"text": "🤖 AI логи"}, {"text": "🔎 Поиск пользователя"}],
            [{"text": "📢 Объявление"}, {"text": "🔓 Разблокировать"}],
            [{"text": "⬅️ В меню"}]
        ]"""

old_kb2 = """        kb = [
            [{"text": "📊 Statistika"}, {"text": "👥 Foydalanuvchilar"}],
            [{"text": "📢 Xabar yuborish"}, {"text": "🔓 Blokdan chiqarish"}],
            [{"text": "🤖 AI loglari"}, {"text": "⬅️ Menyu"}]
        ]"""

new_kb = """        kb = [
            [{"text": "📊 Statistika"}, {"text": "🚨 Ataka"}],
            [{"text": "🔍 Ataka batafsil"}, {"text": "🤖 AI loglari"}],
            [{"text": "🎁 VIP Sovg'a qilish"}, {"text": "⬅️ Menyu"}]
        ]"""

content = content.replace(old_kb1, new_kb)
content = content.replace(old_kb2, new_kb)
content = content.replace("⬅️ В меню", "⬅️ Menyu")

# Fix the step transitions
content = content.replace('if txt == "🔍 Проверка чеков":', 'if txt == "🎁 VIP Sovg\'a qilish":\n        db.update_user(uid, step="admin_gift_vip")\n        send_msg(cid, "🎁 *VIP Sovg\'a qilish:*\\n\\nFoydalanuvchining Telegram ID raqamini yuboring:", kb={"keyboard": [[{"text": "⬅️ Menyu"}]], "resize_keyboard": True})\n        return\n\n    # OLD PROVERKA CHEKOV LOGIC HAS BEEN REPLACED\n    if txt == "IGNORE_ME_NOW":')

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated KBs and menu text.")
