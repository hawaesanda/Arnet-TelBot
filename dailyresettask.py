import shutil
import time
from datetime import datetime, timedelta

import pytz
import schedule

# Zona waktu GMT+7 (WIB)
tz = pytz.timezone("Asia/Jakarta")
ADMIN_IMG_DIR = "D:/Arnet-TelBot/admin_storage/daily-reports"
TEMP_DIR = "D:/Arnet-TelBot/temp"
CLEAR_TIME = "23:59"  # Waktu GMT+7 untuk penghapusan


def clear_download_directory(directory):
    try:
        shutil.rmtree(directory)
        print(f"Deleted directory {directory}")
    except Exception as e:
        print(f"Error cleaning download directory: {str(e)}")


def get_time_until_deletion():
    now = datetime.now(tz)  # Waktu saat ini dengan zona waktu GMT+7
    deletion_time = now.replace(hour=23, minute=59, second=0, microsecond=0)

    if now >= deletion_time:
        deletion_time += timedelta(
            days=1
        )  # Jika sudah lewat jam 11:00, jadwalkan untuk besok

    time_remaining = deletion_time - now

    days = time_remaining.days
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return (
        f"{days} day(s), {hours} hour(s), {minutes} minute(s), {seconds} second(s)",
        now,
        deletion_time,
    )


def schedule_tasks():
    # Jadwalkan penghapusan direktori setiap hari pada jam 11:00
    schedule.every().day.at(CLEAR_TIME).do(
        lambda: clear_download_directory(ADMIN_IMG_DIR),
        lambda: clear_download_directory(TEMP_DIR)
    )

    while True:
        time_remaining_str, now, deletion_time = get_time_until_deletion()
        print(f"Waktu saat ini: {now.strftime('%Y-%m-%d %H:%M:%S')} (GMT+7)")
        print(f"Waktu tersisa untuk penghapusan: {time_remaining_str}")

        schedule.run_pending()
        time.sleep(10)  # Tunggu 1 detik sebelum mengecek lagi


# Panggil fungsi untuk memulai penjadwalan
print("Daily clear is active!")
schedule_tasks()
