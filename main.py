import os
import json
import telebot
from telebot import types

# 🔐 Bot Token & Admin ID
BOT_TOKEN = "7930016886:AAG3NcW1V-KZZG2xStvPJ6Rg3l21xETHvXs"
ADMIN_ID = 8046323012

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Auto-create data.json file if not exists
if not os.path.exists("data.json"):
    with open("data.json", "w") as f:
        json.dump({}, f)

# 📂 Load user data
with open("data.json", "r") as f:
    users = json.load(f)

# 💾 Save user data
def save_data():
    with open("data.json", "w") as f:
        json.dump(users, f, indent=4)

# 📦 Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "referrals": 0,
            "submitted": False
        }
        # 🔁 Referral check
        if len(message.text.split()) > 1:
            referrer = message.text.split()[1]
            if referrer in users and referrer != user_id:
                users[referrer]["referrals"] += 1
                users[referrer]["balance"] += 10
                bot.send_message(int(referrer), f"✅ আপনি একজন কে রেফার করেছেন এবং ১০ টাকা পেয়েছেন!")
    save_data()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎯 টাস্ক", "💸 ব্যালেন্স", "📤 স্ক্রিনশট জমা দিন")
    markup.add("👥 রেফার", "📥 উইথড্র", "🧑‍💻 এডমিন")

    bot.send_message(message.chat.id, "✨ স্বাগতম! একটি অপশন নির্বাচন করুন:", reply_markup=markup)

# 🎯 Task button
@bot.message_handler(func=lambda m: m.text == "🎯 টাস্ক")
def show_tasks(message):
    bot.send_message(message.chat.id, "🧾 নিচে আপনার টাস্ক লিঙ্ক:\n\n1️⃣ https://example.com\n2️⃣ https://example2.com\n3️⃣ https://example3.com\n4️⃣ https://example4.com\n\n📝 প্রতিটি টাস্কে ৩টি স্ক্রিনশট দিন। প্রতিটি টাস্কের জন্য ৩০ টাকা পাবেন।")

# 💸 Balance button
@bot.message_handler(func=lambda m: m.text == "💸 ব্যালেন্স")
def show_balance(message):
    user_id = str(message.from_user.id)
    user = users.get(user_id, {})
    balance = user.get("balance", 0)
    refs = user.get("referrals", 0)
    bot.send_message(message.chat.id, f"💰 আপনার ব্যালেন্স: {balance} টাকা\n👥 রেফার সংখ্যা: {refs}")

# 👥 রেফার
@bot.message_handler(func=lambda m: m.text == "👥 রেফার")
def refer_info(message):
    user_id = str(message.from_user.id)
    link = f"https://t.me/myoffer363bot?start={user_id}"
    refs = users[user_id]["referrals"]
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিঙ্ক:\n{link}\n\n👥 মোট রেফার: {refs}\n💵 প্রতি রেফার = ১০ টাকা")

# 📤 Screenshot submit
@bot.message_handler(func=lambda m: m.text == "📤 স্ক্রিনশট জমা দিন")
def submit_screenshot(message):
    bot.send_message(message.chat.id, "📸 দয়া করে আপনার টাস্ক স্ক্রিনশট পাঠান (৩টি)।")
    users[str(message.from_user.id)]["submitted"] = True
    save_data()

# 📥 Withdraw
@bot.message_handler(func=lambda m: m.text == "📥 উইথড্র")
def withdraw_request(message):
    user_id = str(message.from_user.id)
    balance = users[user_id]["balance"]
    if balance >= 1000:
        bot.send_message(message.chat.id, "💳 আপনি কোন মাধ্যমে টাকা তুলতে চান?\nbKash / Nagad / Rocket সহ নাম্বার পাঠান:")
    else:
        bot.send_message(message.chat.id, "❌ মিনিমাম ১০০০ টাকা ব্যালেন্স থাকতে হবে উইথড্র করার জন্য।")

# 🧑‍💻 Admin Panel
@bot.message_handler(func=lambda m: m.text == "🧑‍💻 এডমিন")
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👁️ ইউজার দেখুন", callback_data="view_user"))
    markup.add(types.InlineKeyboardButton("✏️ ইউজার এডিট", callback_data="edit_user"))
    bot.send_message(message.chat.id, "🛠️ এডমিন অপশন:", reply_markup=markup)

# 🔁 Callback handling
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "view_user":
        bot.send_message(call.message.chat.id, "🆔 ইউজার আইডি দিন:")
        bot.register_next_step_handler(call.message, process_view_user)

    elif call.data == "edit_user":
        bot.send_message(call.message.chat.id, "✏️ ইউজার আইডি দিন:")
        bot.register_next_step_handler(call.message, process_edit_user)

# 👁️ View User Info
def process_view_user(message):
    user_id = message.text.strip()
    if user_id in users:
        info = users[user_id]
        bot.send_message(message.chat.id, f"🧑 ইউজার {user_id}:\n💰 ব্যালেন্স: {info['balance']} টাকা\n👥 রেফার: {info['referrals']}")
    else:
        bot.send_message(message.chat.id, "❌ ইউজার খুঁজে পাওয়া যায়নি।")

# ✏️ Edit User
def process_edit_user(message):
    user_id = message.text.strip()
    if user_id in users:
        bot.send_message(message.chat.id, "📥 নতুন ব্যালেন্স দিন:")
        bot.register_next_step_handler(message, lambda m: update_balance(m, user_id))
    else:
        bot.send_message(message.chat.id, "❌ ইউজার খুঁজে পাওয়া যায়নি।")

def update_balance(message, user_id):
    try:
        new_balance = int(message.text.strip())
        users[user_id]["balance"] = new_balance
        save_data()
        bot.send_message(message.chat.id, f"✅ ইউজার {user_id} এর ব্যালেন্স আপডেট হয়েছে: {new_balance} টাকা")
    except:
        bot.send_message(message.chat.id, "❌ ব্যালেন্স আপডেট ব্যর্থ। একটি সঠিক সংখ্যা দিন।")

# 📸 Approve/Reject system
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = str(message.from_user.id)
    if users.get(user_id, {}).get("submitted"):
        caption = f"🆔 ইউজার: {user_id}\n✅ স্ক্রিনশট জমা দিয়েছে"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"))
        markup.add(types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}"))
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup)
        users[user_id]["submitted"] = False
        save_data()

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def approve_reject(call):
    user_id = call.data.split("_")[1]
    if call.data.startswith("approve_"):
        users[user_id]["balance"] += 30
        bot.send_message(int(user_id), "✅ আপনার টাস্ক এপ্রুভ হয়েছে! ৩০ টাকা যোগ হয়েছে।")
    else:
        bot.send_message(int(user_id), "❌ আপনার টাস্ক রিজেক্ট হয়েছে। দয়া করে সঠিকভাবে পূর্ণরায় দিন।")
    save_data()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# ▶️ Run bot
bot.infinity_polling()
