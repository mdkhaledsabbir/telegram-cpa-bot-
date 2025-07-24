import os
import telebot
from telebot import types
import json

# Env variables
TOKEN = os.environ.get('TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
bot = telebot.TeleBot(TOKEN)

# CPA Tasks
TASKS = {
    "Task 1": "📌 Pin Submit: https://tinyurl.com/37xxp2an\n🖼 ৩টি স্ক্রিনশট দিন",
    "Task 2": "📌 Pin Submit: https://tinyurl.com/4vc76fw5\n🖼 ৩টি স্ক্রিনশট দিন",
    "Task 3": "📧 Email Submit: https://tinyurl.com/yyherfxt\n🖼 ৩টি স্ক্রিনশট দিন",
    "Task 4": "📧 Email Submit: https://tinyurl.com/25nt96v9\n🖼 ৩টি স্ক্রিনশট দিন"
}

# JSON data file
DATA_FILE = 'users.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {'referrals': 0, 'balance': 0, 'submitted': False}
        ref = message.text.split(' ')[1] if len(message.text.split()) > 1 else None
        if ref and ref in data and ref != user_id:
            data[ref]['referrals'] += 1
            data[ref]['balance'] += 10
            bot.send_message(int(ref), f"🎉 আপনি ১টি রেফারেল পেয়েছেন!\n💰 ব্যালেন্স এখন: ৳{data[ref]['balance']}")

    save_data(data)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 টাস্কগুলো", "📤 স্ক্রিনশট জমা", "💸 ব্যালেন্স", "📨 উইথড্র", "👥 রেফার লিংক")
    bot.send_message(message.chat.id, "স্বাগতম! নিচের বাটনগুলো ব্যবহার করুন 👇", reply_markup=markup)

# Task list
@bot.message_handler(func=lambda m: m.text == "📝 টাস্কগুলো")
def task_list(message):
    msg = "🔹 বর্তমান টাস্কসমূহ:\n\n"
    for title, link in TASKS.items():
        msg += f"✅ {title}\n{link}\n\n"
    bot.send_message(message.chat.id, msg)

# Screenshot prompt
@bot.message_handler(func=lambda m: m.text == "📤 স্ক্রিনশট জমা")
def ask_screenshot(message):
    bot.send_message(message.chat.id, "🔄 দয়া করে ৩টি স্ক্রিনশট এক এক করে পাঠান।")

# Handle screenshot
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.chat.id)
    caption = f"🆔 ইউজার ID: {user_id}\n👤 ইউজারনেম: @{message.chat.username or 'N/A'}"
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(ADMIN_ID, caption)
    bot.send_message(message.chat.id, "✅ আপনার স্ক্রিনশট গ্রহণ করা হয়েছে। চেক করে এপ্রুভ করা হবে।")

# Balance check
@bot.message_handler(func=lambda m: m.text == "💸 ব্যালেন্স")
def check_balance(message):
    user_id = str(message.chat.id)
    data = load_data()
    user = data.get(user_id, {})
    balance = user.get('balance', 0)
    bot.send_message(message.chat.id, f"💰 আপনার মোট ব্যালেন্স: ৳{balance} টাকা")

# Temporary dictionary to hold withdraw steps
withdraw_data = {}

@bot.message_handler(func=lambda m: m.text == "📨 উইথড্র")
def withdraw_request(message):
    user_id = str(message.chat.id)
    data = load_data()
    balance = data[user_id]['balance']
    
    if balance < 1000:
        bot.send_message(message.chat.id, "❌ উইথড্র এর জন্য কমপক্ষে ৳1000 টাকা থাকতে হবে।")
        return

    withdraw_data[user_id] = {}
    msg = bot.send_message(message.chat.id, "👤 আপনার পূর্ণ নাম লিখুন:")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    user_id = str(message.chat.id)
    withdraw_data[user_id]['name'] = message.text
    msg = bot.send_message(message.chat.id, "📞 আপনার মোবাইল নম্বর দিন:")
    bot.register_next_step_handler(msg, process_number)

def process_number(message):
    user_id = str(message.chat.id)
    withdraw_data[user_id]['number'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("বিকাশ", "নগদ", "রকেট")
    msg = bot.send_message(message.chat.id, "💳 আপনি কোন মেথডে টাকা নিতে চান?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_method)

def process_method(message):
    user_id = str(message.chat.id)
    data = load_data()
    balance = data[user_id]['balance']

    withdraw_data[user_id]['method'] = message.text
    name = withdraw_data[user_id]['name']
    number = withdraw_data[user_id]['number']
    method = withdraw_data[user_id]['method']

    # Final confirmation to user
    bot.send_message(message.chat.id, "✅ আপনার উইথড্র রিকোয়েস্ট গ্রহণ করা হয়েছে। এপ্রুভ হলে জানানো হবে।\n📅 পেমেন্ট প্রতিমাসের ৩১ তারিখ দেওয়া হবে।")

    # Notify admin
    info = f"""📥 নতুন উইথড্র রিকোয়েস্ট:
👤 নাম: {name}
📞 নম্বর: {number}
💳 মেথড: {method}
💰 ব্যালেন্স: ৳{balance}
🆔 ইউজার: @{message.chat.username or 'N/A'} ({user_id})"""
    
    bot.send_message(ADMIN_ID, info)

# Referral link
@bot.message_handler(func=lambda m: m.text == "👥 রেফার লিংক")
def referral(message):
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিংক:\nhttps://t.me/{bot.get_me().username}?start={message.chat.id}\n\n👥 প্রতি রেফারে ১০ টাকা!")

# Admin: Check user balance
@bot.message_handler(commands=['balance'])
def check_user_balance(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        parts = message.text.split()
        target_id = parts[1]
        data = load_data()

        if target_id in data:
            bal = data[target_id]['balance']
            ref = data[target_id]['referrals']
            bot.send_message(message.chat.id, f"📊 ইউজার {target_id}:\n💰 ব্যালেন্স: ৳{bal}\n👥 রেফার: {ref}")
        else:
            bot.send_message(message.chat.id, "❌ ইউজার খুঁজে পাওয়া যায়নি।")
    except:
        bot.send_message(message.chat.id, "⚠️ কমান্ড ভুল!\nসঠিক ব্যবহার: /balance <user_id>")

bot.infinity_polling()
