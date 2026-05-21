import telebot
import sqlite3
import threading
import time

from datetime import datetime, timedelta

TOKEN = "8940873691:AAFuGPq3wws2hqySPpeGaI4Onj8O2wnPu80"

GRUPO_ID = -100XXXXXXXXXX

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("subs.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS subs (
    user_id INTEGER,
    expire_date TEXT
)
""")

conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"Tu ID es: {message.chat.id}")

@bot.message_handler(commands=['daracceso'])
def dar_acceso(message):

    admin_id = message.chat.id

    partes = message.text.split()

    if len(partes) != 3:
        bot.reply_to(message, "Uso:\n/daracceso USER_ID DIAS")
        return

    user_id = int(partes[1])
    dias = int(partes[2])

    expire_date = datetime.now() + timedelta(days=dias)

    invite = bot.create_chat_invite_link(
        chat_id=GRUPO_ID,
        member_limit=1,
        expire_date=int(time.time()) + 300
    )

    cursor.execute(
        "INSERT INTO subs VALUES (?, ?)",
        (user_id, expire_date.strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()

    bot.send_message(
        user_id,
        f"Tu acceso:\n{invite.invite_link}\n\nVence el: {expire_date}"
    )

    bot.reply_to(message, "Acceso enviado.")

def revisar_subs():

    while True:

        ahora = datetime.now()

        cursor.execute("SELECT user_id, expire_date FROM subs")

        usuarios = cursor.fetchall()

        for user_id, expire_date in usuarios:

            fecha = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S")

            if ahora > fecha:

                try:
                    bot.ban_chat_member(GRUPO_ID, user_id)
                    bot.unban_chat_member(GRUPO_ID, user_id)

                    bot.send_message(
                        user_id,
                        "Tu suscripción venció."
                    )

                except:
                    pass

                cursor.execute(
                    "DELETE FROM subs WHERE user_id=?",
                    (user_id,)
                )

                conn.commit()

        time.sleep(60)

threading.Thread(target=revisar_subs).start()

bot.infinity_polling()
