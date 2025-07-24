import os
import telebot
from telebot import types
import json

TOKEN = os.environ.get('TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
bot = telebot.TeleBot(TOKEN)

TASKS = {
    "Task 1": "📌 Pin Submit: https://tinyurl.com/37xxp2an\n🖼 ৩টি স্ক্রিনশট দিন",
    "Task 2": "📌 Pin Submit: https://tinyurl.com/4vc76fw5\n🖼 ৩টি স্ক্রিনশট দিন",
    "Task 3": "📧 Email Submit: https://tinyurl.com/yyherfxt\n🖼 ৩টি স্ক্রিনশট দিন",
    "Task 4": "📧 Email Submit: https://tinyurl.com/25nt96v9\n🖼 ৩টি স্ক্রিনশট দিন"
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
        data[user_id] = {'referrals': 0, 'balance': 0, 'submitted': False}
        ref = message.text.split(' ')[1] if len(message.text.split()) > 1 else None
        if ref and ref in data and ref != user_id:
            data[ref]['referrals'] += 1
            data[ref]['balance'] += 10
            bot.send_message(int(ref), "🎉 আপনি ১টি রেফারেল পেয়েছেন! আপনার ব্যালেন্স এখন: ৳{} টাকা".format(data[ref]['balance']))
    save_data(data)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 টাস্কগুলো", "📤 স্ক্রিনশট জমা", "💸 ব্যালেন্স", "📨 উইথড্র", "👥 রেফার লিংক")
    bot.send_message(message.chat.id, "স্বাগতম! বাটনগুলো ব্যবহার করুন।", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📝 টাস্কগুলো")
def task_list(message):
    msg = "🔹 বর্তমান টাস্ক:\n\n"
    for title, link in TASKS.items():
        msg += f"✅ {title}\n{link}\n\n"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "📤 স্ক্রিনশট জমা")
def ask_screenshot(message):
    bot.send_message(message.chat.id, "🔄 দয়া করে ৩টি স্ক্রিনশট পাঠান (এক এক করে)।")

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.chat.id)
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "✅ আপনার স্ক্রিনশট গ্রহণ করা হয়েছে। চেক করে এপ্রুভ করা হবে।")
await bot.send_message(admin_id, f"স্ক্রিনশট পাঠিয়েছে:\nName: {message.from_user.full_name}\nUser ID: {message.from_user.id}")
@bot.message_handler(func=lambda m: m.text == "💸 ব্যালেন্স")
def check_balance(message):
    user_id = str(message.chat.id)
    data = load_data()
    user = data.get(user_id, {})
    balance = user.get('balance', 0)
    bot.send_message(message.chat.id, f"💰 আপনার মোট ব্যালেন্স: ৳{balance} টাকা")

@bot.message_handler(func=lambda m: m.text == "📨 উইথড্র")
def withdraw_request(message):
    user_id = str(message.chat.id)
    data = load_data()
    balance = data[user_id]['balance']
    if balance >= 1000:
        bot.send_message(message.chat.id, "✅ আপনার উইথড্র রিকোয়েস্ট গ্রহণ করা হয়েছে। এপ্রুভ হলে জানানো হবে।")
        bot.send_message(ADMIN_ID, f"📨 @{message.chat.username or message.chat.id} উইথড্র রিকোয়েস্ট করেছে। মোট ব্যালেন্স: ৳{balance}")
    else:
        bot.send_message(message.chat.id, "❌ উইথড্র এর জন্য কমপক্ষে ৳1000 টাকা থাকতে হবে।")

@bot.message_handler(func=lambda m: m.text == "👥 রেফার লিংক")
def referral(message):
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিংক:\nhttps://t.me/{bot.get_me().username}?start={message.chat.id}")
await message.reply(
    f"✅ আপনার রেফার লিংক:\n{ref_link}\n\n💰 প্রতি সফল রেফারে আপনি পাবেন ১০ টাকা!\n\n👫 বন্ধুদের শেয়ার করুন এবং আয় করুন।"
        )
bot.infinity_polling()
