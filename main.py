import os
import telebot
from telebot import types
import json

TOKEN = os.environ.get('TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
bot = telebot.TeleBot(TOKEN)

TASK_REWARD = 30
REFERRAL_REWARD = 10
MIN_WITHDRAW = 1000
MAX_SCREENSHOTS = 3

TASKS = {
    "Task 1": "📌 Pin Submit: https://tinyurl.com/37xxp2an\n🖼 সর্বোচ্চ ৩টি স্ক্রিনশট দিন\n💰 পেমেন্ট: ৳30",
    "Task 2": "📌 Pin Submit: https://tinyurl.com/4vc76fw5\n🖼 সর্বোচ্চ ৩টি স্ক্রিনশট দিন\n💰 পেমেন্ট: ৳30",
    "Task 3": "📧 Email Submit: https://tinyurl.com/yyherfxt\n🖼 সর্বোচ্চ ৩টি স্ক্রিনশট দিন\n💰 পেমেন্ট: ৳30",
    "Task 4": "📧 Email Submit: https://tinyurl.com/25nt96v9\n🖼 সর্বোচ্চ ৩টি স্ক্রিনশট দিন\n💰 পেমেন্ট: ৳30"
}

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

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {'referrals': 0, 'balance': 0, 'submitted': 0}
        ref = message.text.split(' ')[1] if len(message.text.split()) > 1 else None
        if ref and ref in data and ref != user_id:
            data[ref]['referrals'] += 1
            data[ref]['balance'] += REFERRAL_REWARD
            bot.send_message(int(ref), f"🎉 আপনি ১টি রেফারেল পেয়েছেন! আপনার ব্যালেন্স এখন: ৳{data[ref]['balance']}")
    save_data(data)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 টাস্কগুলো", "📤 স্ক্রিনশট জমা", "💸 ব্যালেন্স")
    markup.add("📨 উইথড্র", "👥 রেফার লিংক", "📘 কাজের নিয়ম")
    bot.send_message(message.chat.id, "স্বাগতম! নিচের বাটনগুলো ব্যবহার করুন 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📝 টাস্কগুলো")
def task_list(message):
    msg = "🔹 বর্তমান টাস্ক:\n\n"
    for title, link in TASKS.items():
        msg += f"✅ {title}\n{link}\n\n"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "📤 স্ক্রিনশট জমা")
def ask_screenshot(message):
    user_id = str(message.chat.id)
    data = load_data()
    user = data.get(user_id, {})
    submitted = user.get('submitted', 0)

    if submitted >= MAX_SCREENSHOTS:
        bot.send_message(message.chat.id, f"❌ আপনি ইতোমধ্যে সর্বোচ্চ {MAX_SCREENSHOTS}টি স্ক্রিনশট জমা দিয়েছেন।")
        return
    bot.send_message(message.chat.id, f"📸 দয়া করে স্ক্রিনশট পাঠান ({submitted + 1}/{MAX_SCREENSHOTS})")

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.chat.id)
    data = load_data()
    user = data.get(user_id, {})

    if user.get('submitted', 0) >= MAX_SCREENSHOTS:
        bot.send_message(message.chat.id, "❌ আপনি সর্বোচ্চ ৩টি স্ক্রিনশট জমা দিয়েছেন।")
        return

    user['submitted'] += 1
    if user['submitted'] == MAX_SCREENSHOTS:
        user['balance'] += TASK_REWARD
        bot.send_message(message.chat.id, f"✅ স্ক্রিনশট জমা সম্পন্ন! আপনি ৳{TASK_REWARD} পেয়েছেন। মোট ব্যালেন্স: ৳{user['balance']}")
    else:
        bot.send_message(message.chat.id, f"📸 স্ক্রিনশট {user['submitted']}/3 জমা হয়েছে।")

    save_data(data)
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

@bot.message_handler(func=lambda m: m.text == "💸 ব্যালেন্স")
def check_balance(message):
    user_id = str(message.chat.id)
    data = load_data()
    user = data.get(user_id, {})
    balance = user.get('balance', 0)
    referrals = user.get('referrals', 0)
    bot.send_message(message.chat.id, f"💰 আপনার মোট ব্যালেন্স: ৳{balance}\n👥 রেফার সংখ্যা: {referrals}")

@bot.message_handler(func=lambda m: m.text == "📨 উইথড্র")
def withdraw_request(message):
    user_id = str(message.chat.id)
    data = load_data()
    user = data.get(user_id, {})
    balance = user.get('balance', 0)
    if balance >= MIN_WITHDRAW:
        bot.send_message(message.chat.id, "✅ আপনার উইথড্র রিকোয়েস্ট গ্রহণ করা হয়েছে। এডমিন চেক করে জানাবেন।")
        bot.send_message(ADMIN_ID, f"📨 @{message.chat.username or message.chat.id} উইথড্র চায়। ব্যালেন্স: ৳{balance}")
    else:
        bot.send_message(message.chat.id, f"❌ উইথড্র করতে হলে অন্তত ৳{MIN_WITHDRAW} প্রয়োজন।")

    bot.send_message(message.chat.id, "💳 পেমেন্ট মেথড: bKash | Nagad | Rocket")

@bot.message_handler(func=lambda m: m.text == "👥 রেফার লিংক")
def referral(message):
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিংক:\nhttps://t.me/{bot.get_me().username}?start={message.chat.id}")

@bot.message_handler(func=lambda m: m.text == "📘 কাজের নিয়ম")
def rules(message):
    rule_text = (
        "📌 প্রতিটি টাস্কের জন্য সর্বোচ্চ ৩টি স্ক্রিনশট দিন:\n"
        "1️⃣ প্রথম ক্লিক করার সময়\n"
        "2️⃣ এপস/ফর্মে ঢোকার সময়\n"
        "3️⃣ ইমেইল বা পিন সাবমিট করার পর\n\n"
        "🖼 এগুলো স্ক্রিনশট বাটনে পাঠান।\n"
        "✅ যাচাইয়ের পর টাকা অ্যাড করা হবে।"
    )
    bot.send_message(message.chat.id, rule_text)

bot.infinity_polling()
