import re

with open('bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, l in enumerate(lines):
    if l.startswith('    if is_owner:'):
        start_idx = i
    if l.strip().startswith('if u[\'step\'] == "agreement":'):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_admin_block = """    if is_owner:
        # Broadcast step (Attack)
        if u['step'] == "admin_broadcast" and txt:
            if txt == "⬅️ Menyu" or txt == "/admin":
                db.update_user(uid, step="admin_main")
                kb = [
                    [{"text": "📊 Statistika"}, {"text": "🚨 Ataka"}],
                    [{"text": "🔍 Ataka batafsil"}, {"text": "🤖 AI loglari"}],
                    [{"text": "🎁 VIP Sovg'a qilish"}, {"text": "⬅️ Menyu"}]
                ]
                send_msg(cid, "🛠️ *Admin Panel*", kb={"keyboard": kb, "resize_keyboard": True}); return
            else:
                all_u = db.get_all_users(); count = 0
                for user_id in all_u:
                    if send_msg(user_id, f"📢 *XABAR:*\\n\\n{txt}"): count += 1
                    import time
                    time.sleep(0.05)
                db.update_user(uid, step="admin_main")
                send_msg(cid, f"✅ Xabar {count} ta foydalanuvchiga yuborildi!")
                return

        # Broadcast Detailed (Ataka batafsil)
        if u['step'] == "admin_broadcast_photo":
            if txt and (txt == "⬅️ Menyu" or txt == "/admin"):
                db.update_user(uid, step="admin_main")
                kb = [
                    [{"text": "📊 Statistika"}, {"text": "🚨 Ataka"}],
                    [{"text": "🔍 Ataka batafsil"}, {"text": "🤖 AI loglari"}],
                    [{"text": "🎁 VIP Sovg'a qilish"}, {"text": "⬅️ Menyu"}]
                ]
                send_msg(cid, "🛠️ *Admin Panel*", kb={"keyboard": kb, "resize_keyboard": True}); return
            else:
                # Forward the message to everyone
                all_u = db.get_all_users(); count = 0
                for user_id in all_u:
                    try:
                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/copyMessage"
                        data = {"chat_id": user_id, "from_chat_id": cid, "message_id": m['message_id']}
                        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
                        res = urllib.request.urlopen(req)
                        if res.getcode() == 200: count += 1
                    except Exception as e: pass
                    import time
                    time.sleep(0.05)
                db.update_user(uid, step="admin_main")
                send_msg(cid, f"✅ Xabar {count} ta foydalanuvchiga yuborildi!")
                return

        # Gift VIP Step
        if u['step'] == "admin_gift_vip" and txt:
            if txt == "⬅️ Menyu" or txt == "/admin":
                db.update_user(uid, step="admin_main")
                kb = [
                    [{"text": "📊 Statistika"}, {"text": "🚨 Ataka"}],
                    [{"text": "🔍 Ataka batafsil"}, {"text": "🤖 AI loglari"}],
                    [{"text": "🎁 VIP Sovg'a qilish"}, {"text": "⬅️ Menyu"}]
                ]
                send_msg(cid, "🛠️ *Admin Panel*", kb={"keyboard": kb, "resize_keyboard": True}); return
            else:
                target_id = txt.strip()
                target_user = db.get_user(target_id)
                if target_user:
                    db.update_user(target_id, sub="vip", sub_expire="2099-12-31 23:59:59", ai_count=0, banned=0, violations=0)
                    send_msg(cid, f"✅ Foydalanuvchi (ID: {target_id}) ga VIP taqdim etildi!")
                    send_msg(target_id, "🎁 Tabriklaymiz! Admin sizga bir umrlik *VIP* ta'lim kurslarini taqdim etdi. Endi barcha xizmatlardan bepul foydalanishingiz mumkin!")
                else:
                    send_msg(cid, "❌ Bunday ID bilan foydalanuvchi topilmadi.")
                return

        # Main Admin Menu Buttons
        if u['step'] == "admin_main" and txt:
            if txt == "📊 Statistika":
                all_u = db.get_all_users()
                total = len(all_u)
                active = sum(1 for v in all_u.values() if v.get('sub') != 'none')
                import time
                today = sum(1 for v in all_u.values() if v.get('registered_at', '').startswith(time.strftime("%Y-%m-%d")))
                text = f"📊 *Umumiy statistika:*\\n\\n👥 Jami: {total}\\n💎 Faol obunalar: {active}\\n🆕 Bugun: {today}"
                send_msg(cid, text)
                return
            elif txt == "🚨 Ataka":
                db.update_user(uid, step="admin_broadcast")
                send_msg(cid, "📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:\\n\\n(Bekor qilish uchun ⬅️ Menyu bosing)", kb={"keyboard": [[{"text": "⬅️ Menyu"}]], "resize_keyboard": True})
                return
            elif txt == "🔍 Ataka batafsil":
                db.update_user(uid, step="admin_broadcast_photo")
                send_msg(cid, "📢 Rasmli, videolar yoki istalgan postni yuboring (forward qilsangiz ham bo'ladi). Barcha foydalanuvchilarga nusxalanadi:\\n\\n(Bekor qilish uchun ⬅️ Menyu bosing)", kb={"keyboard": [[{"text": "⬅️ Menyu"}]], "resize_keyboard": True})
                return
            elif txt == "🤖 AI loglari":
                logs = db.conn.execute('SELECT user_id, prompt, timestamp FROM ai_logs ORDER BY id DESC LIMIT 5').fetchall()
                if not logs:
                    send_msg(cid, "Hech qanday AI loglari topilmadi.")
                else:
                    res = "🤖 *So'nggi 5 ta AI loglari:*\\n\\n"
                    for l in logs:
                        res += f"👤 ID: `{l[0]}`\\n🕒 {l[2]}\\n💬 {l[1][:100]}...\\n\\n"
                    send_msg(cid, res)
                return
            elif txt == "🎁 VIP Sovg'a qilish":
                db.update_user(uid, step="admin_gift_vip")
                send_msg(cid, "🎁 *VIP Sovg'a qilish:*\\n\\nFoydalanuvchining Telegram ID raqamini yuboring:", kb={"keyboard": [[{"text": "⬅️ Menyu"}]], "resize_keyboard": True})
                return
            elif txt == "⬅️ Menyu":
                db.update_user(uid, step="main")
                send_msg(cid, "🏠 Asosiy menyu:", kb=get_main_kb(uid, u.get('lang', 'uz')))
                return
\n"""
    new_lines = lines[:start_idx] + [new_admin_block] + lines[end_idx:]
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Replaced successfully")
else:
    print("Failed to find indices")
