main.py

import os import telebot from telebot import types import json

TOKEN = os.environ.get('TOKEN') ADMIN_ID = int(os.environ.get('ADMIN_ID')) bot = telebot.TeleBot(TOKEN)

TASK_REWARD = 30 REFERRAL_REWARD = 10 MIN_WITHDRAW = 1000 MAX_SCREENSHOTS = 3

TASKS = { "Task 1": "📌 Pin Submit: https://tinyurl.com/37xxp2an\n🖼 সবগুলো স্ক্রিনশট দিন\n💰 পেমেন্ট: ৳30", "Task 2": "📌 Pin Submit: https://tinyurl.com/4vc76fw5\n🖼 সবগুলো স্ক্রিনশট দিন\n💰 পেমেন্ট: ৳30", "Task 3": "📧 Email Submit: https://tinyurl.com/yyherfxt\n🖼 সবগুলো স্ক্রিনশট দিন\n💰 পেমেন্ট: ৳30", "Task 4": "📧 Email Submit: https://tinyurl.com/25nt96v9\n🖼 সবগুলো স্ক্রিনশট দিন\n💰 পেমেন্ট: ৳30" }

DATA_FILE = 'users.json' if not os.path.exists(DATA_FILE): with open(DATA_FILE, 'w') as f: json.dump({}, f)

editing_user_id = None  # Global variable for admin editing user

Helper Functions

def load_data(): with open(DATA_FILE) as f: return json.load(f)

def save_data(data): with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=2)

def create_user_if_not_exist(user_id, username, ref=None): data = load_data() if str(user_id) not in data: data[str(user_id)] = { 'username': username, 'balance': 0, 'referrals': [], 'submitted_tasks': [], 'pending_screenshots': [], 'withdraw_requested': False } if ref and str(ref) in data and str(ref) != str(user_id): data[str(ref)]['referrals'].append(user_id) data[str(ref)]['balance'] += REFERRAL_REWARD save_data(data)

def get_user_info_text(user_id): data = load_data() user = data.get(str(user_id)) if user: return f"🆔 ID: {user_id}\n👤 Username: @{user['username']}\n💰 Balance: ৳{user['balance']}\n👥 Referrals: {len(user['referrals'])}\n✅ Submitted Tasks: {len(user['submitted_tasks'])}" else: return "❌ ইউজার খুঁজে পাওয়া যায়নি।"

@bot.message_handler(commands=['start']) def start_handler(message): user_id = message.from_user.id username = message.from_user.username or "NoUsername" ref = None if len(message.text.split()) > 1: ref = message.text.split()[1] create_user_if_not_exist(user_id, username, ref)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.row("🧾 টাস্ক", "📤 স্ক্রিনশট জমা")
markup.row("💸 উইথড্র", "👥 রেফার")
if user_id == ADMIN_ID:
    markup.row("🛠️ ইউজার এডিট", "🧍 ইউজার দেখুন")
bot.send_message(user_id, "👋 স্বাগতম! আপনি কাজ শুরু করতে পারেন নিচের মেনু থেকে।", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🧾 টাস্ক") def task_list_handler(message): for title, desc in TASKS.items(): bot.send_message(message.chat.id, f"🔸 {title}\n{desc}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📤 স্ক্রিনশট জমা") def ask_for_screenshots(message): bot.send_message(message.chat.id, f"🖼 {MAX_SCREENSHOTS}টি স্ক্রিনশট দিন।") data = load_data() data[str(message.from_user.id)]['pending_screenshots'] = [] save_data(data)

@bot.message_handler(content_types=['photo']) def handle_screenshots(message): user_id = message.from_user.id data = load_data() if str(user_id) not in data: return pending = data[str(user_id)].get('pending_screenshots', []) if len(pending) < MAX_SCREENSHOTS: pending.append(message.photo[-1].file_id) data[str(user_id)]['pending_screenshots'] = pending save_data(data) bot.reply_to(message, f"✅ স্ক্রিনশট {len(pending)}/{MAX_SCREENSHOTS} জমা হয়েছে।")

if len(pending) == MAX_SCREENSHOTS:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ এপ্রুভ", callback_data=f"approve:{user_id}"))
        markup.add(types.InlineKeyboardButton("❌ রিজেক্ট", callback_data=f"reject:{user_id}"))
        for file_id in pending:
            bot.send_photo(ADMIN_ID, file_id)
        bot.send_message(ADMIN_ID, f"👤 ইউজার: {user_id} স্ক্রিনশট সাবমিট করেছে।", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve:')) def approve_task(call): user_id = call.data.split(':')[1] data = load_data() if user_id in data: data[user_id]['balance'] += TASK_REWARD data[user_id]['submitted_tasks'].append(len(data[user_id]['submitted_tasks']) + 1) data[user_id]['pending_screenshots'] = [] save_data(data) bot.send_message(int(user_id), "✅ আপনার কাজটি এপ্রুভ করা হয়েছে।") bot.answer_callback_query(call.id, "টাকা যোগ হয়েছে।")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject:')) def reject_task(call): user_id = call.data.split(':')[1] data = load_data() if user_id in data: data[user_id]['pending_screenshots'] = [] save_data(data) bot.send_message(int(user_id), "❌ আপনার টাস্ক ভুল ছিল। আবার চেষ্টা করুন।") bot.answer_callback_query(call.id, "রিজেক্ট করা হয়েছে।")

@bot.message_handler(func=lambda m: m.text == "👥 রেফার") def referral_info(message): data = load_data() user = data.get(str(message.from_user.id), {}) ref_link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}" bot.send_message(message.chat.id, f"👥 রেফার সংখ্যা: {len(user.get('referrals', []))}\n🧾 রেফার প্রতি: ৳10\n📨 আপনার রেফার লিংক:\n{ref_link}")

@bot.message_handler(func=lambda m: m.text == "💸 উইথড্র") def withdraw_handler(message): user_id = message.from_user.id data = load_data() user = data.get(str(user_id)) if user['balance'] >= MIN_WITHDRAW: user['withdraw_requested'] = True save_data(data) bot.send_message(message.chat.id, "✅ আপনার উইথড্র রিকোয়েস্ট গ্রহণ করা হয়েছে।\n📲 পেমেন্ট মেথড: bKash, Nagad, Rocket") bot.send_message(ADMIN_ID, f"📤 উইথড্র রিকোয়েস্ট\n🆔: {user_id}\n৳{user['balance']}") else: bot.send_message(message.chat.id, f"❌ উইথড্র করতে হলে কমপক্ষে ৳{MIN_WITHDRAW} প্রয়োজন।")

@bot.message_handler(func=lambda m: m.text == "🧍 ইউজার দেখুন") def ask_for_userid(message): msg = bot.send_message(message.chat.id, "🔍 যে ইউজার আইডি দেখতে চান, দিন:") bot.register_next_step_handler(msg, show_user_info)

def show_user_info(message): user_id = message.text.strip() bot.send_message(message.chat.id, get_user_info_text(user_id))

@bot.message_handler(func=lambda m: m.text == "🛠️ ইউজার এডিট") def edit_user_start(message): msg = bot.send_message(message.chat.id, "✏️ যেই ইউজার আইডি এডিট করতে চান, দিন:") bot.register_next_step_handler(msg, ask_balance_edit)

def ask_balance_edit(message): global editing_user_id editing_user_id = message.text.strip() msg = bot.send_message(message.chat.id, "💰 নতুন ব্যালেন্স লিখুন:") bot.register_next_step_handler(msg, apply_balance_edit)

def apply_balance_edit(message): global editing_user_id try: new_balance = int(message.text.strip()) data = load_data() if editing_user_id in data: data[editing_user_id]['balance'] = new_balance save_data(data) bot.send_message(message.chat.id, "✅ ব্যালেন্স আপডেট হয়েছে।") else: bot.send_message(message.chat.id, "❌ ইউজার খুঁজে পাওয়া যায়নি।") except ValueError: bot.send_message(message.chat.id, "❌ সঠিক সংখ্যা লিখুন।")

bot.polling(none_stop=True)
