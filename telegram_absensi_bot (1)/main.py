import logging
import csv
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue

TOKEN = os.environ.get("TOKEN")
CSV_FILE = "absensi.csv"

# Jam aktif bot
START_HOUR = 1
END_HOUR = 23

# Batas aktivitas per user per hari
LIMITS = {
    "makan": {"max": 1, "duration": 30},
    "merokok": {"max": 3, "duration": 7},
    "toilet": {"max": 3, "duration": 5},
    "berak": {"max": 1, "duration": 15},
    "delivery": {"max": 1, "duration": 15}
}

# Data harian user
user_sessions = {}
user_usage = {}

# Logging
logging.basicConfig(level=logging.INFO)

def is_within_active_hours():
    now = datetime.now().time()
    return START_HOUR <= now.hour <= END_HOUR

def save_to_csv(username, user_id, activity, start_time, end_time, duration):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Username", "UserID", "Aktivitas", "Jam Mulai", "Jam Selesai", "Durasi (menit)", "Tanggal"])
        writer.writerow([username, user_id, activity, start_time, end_time, duration, datetime.now().strftime("%Y-%m-%d")])

async def start_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_within_active_hours():
        await update.message.reply_text("⏰ Di luar jam absensi (01:00 - 23:00).")
        return

    command = update.message.text.replace("/", "")
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.full_name

    # Cek batas harian
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{user_id}:{command}:{today}"
    if user_usage.get(key, 0) >= LIMITS[command]["max"]:
        await update.message.reply_text(f"❌ Kamu sudah mencapai batas harian untuk aktivitas '{command}'.")
        return

    user_sessions[user_id] = {
        "username": username,
        "activity": command,
        "start": datetime.now()
    }

    user_usage[key] = user_usage.get(key, 0) + 1

    # Reminder
    reminder_minute = max(LIMITS[command]["duration"] - 5, 1)
    context.job_queue.run_once(send_reminder, when=timedelta(minutes=reminder_minute), data={
        "chat_id": update.effective_chat.id,
        "command": command,
        "user_id": user_id
    }, name=f"reminder_{user_id}")

    await update.message.reply_text(f"✅ {username} memulai aktivitas: {command}")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data["chat_id"]
    command = job.data["command"]
    user_id = job.data["user_id"]
    if user_id in user_sessions:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Waktu untuk '{command}' hampir habis!")

async def kembali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_within_active_hours():
        await update.message.reply_text("⏰ Di luar jam absensi (01:00 - 23:00).")
        return

    user_id = update.message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        await update.message.reply_text("❗ Kamu belum memulai aktivitas apa pun.")
        return

    end_time = datetime.now()
    duration = int((end_time - session["start"]).total_seconds() // 60)
    max_dur = LIMITS[session["activity"]]["duration"]
    warning = " ⚠️ Lewat batas waktu!" if duration > max_dur else ""

    save_to_csv(
        session["username"], user_id, session["activity"],
        session["start"].strftime("%H:%M"),
        end_time.strftime("%H:%M"),
        duration
    )

    del user_sessions[user_id]
    await update.message.reply_text(f"📌 Aktivitas '{session['activity']}' dicatat. Durasi: {duration} menit.{warning}")

async def reset_data(context: ContextTypes.DEFAULT_TYPE):
    global user_usage
    user_usage = {}
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        logging.info("CSV file reset harian.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handler aktivitas
    for cmd in ["makan", "merokok", "toilet", "berak", "delivery"]:
        app.add_handler(CommandHandler(cmd, start_activity))
    app.add_handler(CommandHandler("kembali", kembali))

    # Job reset harian
    job_queue: JobQueue = app.job_queue
    job_queue.run_daily(reset_data, time=datetime.strptime("00:00", "%H:%M").time())

    app.run_polling()

if __name__ == "__main__":
    main()
