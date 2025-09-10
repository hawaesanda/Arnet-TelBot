import threading
import time
import os
import shutil
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import calendar

# ====================================================================
# CONFIGURATIONS AND PATHS
# ====================================================================
LOGIN_PASSWORD = "arnet123"  # Password untuk admin
ADMIN_USERNAME = "adminreport" # Username untuk admin
PASSWORD_TEKNISI = "akuteknisi" # Password untuk pendaftaran teknisi

# ====================================================================
# BOT CLIENT & USER DATA
# ====================================================================


bot = Client(
    "arnettryBot",
    api_id=21604277,
    api_hash="5320799e4addb26b8117972b3c959440",
    bot_token="8045860894:AAFP6fI3OkWCq1ChdlN1qXq90hobSc9tWJM",
)

ADMIN_DIR = r"C:\Users\hawa\Documents\Hawa\Magang Telkom\Arnet-TelBot\admin_storage"
BASE_TEMP_DIR = r"C:\Users\hawa\Documents\Hawa\Magang Telkom\Arnet-TelBot\temp"
TEMPLATE_PATH = r"C:\Users\hawa\Documents\Hawa\Magang Telkom\Arnet-TelBot\template\review_template.jpg"
SPLIT_TEMPLATE_PATH = r"C:\Users\hawa\Documents\Hawa\Magang Telkom\Arnet-TelBot\template\split_review_template.jpg"
BASE_TEMPLATES = r"C:\Users\hawa\Documents\Hawa\Magang Telkom\Arnet-TelBot\template"
ADMIN_DAILY_DIR = r"C:\Users\hawa\Documents\Hawa\Magang Telkom\Arnet-TelBot\admin_storage\daily-reports"

# Paths for storing user profiles and admin IDs
PROFILE_PATH = os.path.join(ADMIN_DIR, "profile.txt")
ADMIN_USER_PATH = os.path.join(ADMIN_DIR, "useradmin.txt")
ARCHIVE_DIR = os.path.join(ADMIN_DIR, "archive")

# Ensure directories exist
os.makedirs(ADMIN_DIR, exist_ok=True)
os.makedirs(ADMIN_DAILY_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# ====================================================================
# HELPER FUNCTIONS
# ====================================================================

def get_year_inline_buttons():
    current_year = datetime.now().year
    years = [current_year + i for i in range(6)]
    buttons = []
    row = []
    for i, year in enumerate(years):
        label = f"{year} "
        row.append(InlineKeyboardButton(label, callback_data=f"year:{year}"))
        if (i + 1) % 2 == 0 or i == len(years) - 1:
            buttons.append(row)
            row = []
    return InlineKeyboardMarkup(buttons)

def get_month_inline_buttons():
    months = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    buttons = []
    row = []
    for i, m in enumerate(months):
        row.append(InlineKeyboardButton(m, callback_data=f"month_num:{i + 1}"))
        if (i + 1) % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

def get_day_inline_buttons(year, month):
    num_days = calendar.monthrange(year, month)[1]
    days = [str(i) for i in range(1, num_days + 1)]
    buttons = []
    row = []
    for i, d in enumerate(days):
        label = f"{d} "
        row.append(InlineKeyboardButton(label, callback_data=f"day:{d}"))
        if (i + 1) % 5 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)
    
def get_edit_year_inline_buttons():
    current_year = datetime.now().year
    years = [current_year + i for i in range(6)]
    buttons = []
    row = []
    for i, year in enumerate(years):
        label = f"{year} "
        row.append(InlineKeyboardButton(label, callback_data=f"edit_year:{year}"))
        if (i + 1) % 2 == 0 or i == len(years) - 1:
            buttons.append(row)
            row = []
    return InlineKeyboardMarkup(buttons)

def get_edit_month_inline_buttons():
    months = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    buttons = []
    row = []
    for i, m in enumerate(months):
        row.append(InlineKeyboardButton(m, callback_data=f"edit_month_num:{i + 1}"))
        if (i + 1) % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

def get_edit_day_inline_buttons(year, month):
    num_days = calendar.monthrange(year, month)[1]
    days = [str(i) for i in range(1, num_days + 1)]
    buttons = []
    row = []
    for i, d in enumerate(days):
        label = f"{d} "
        row.append(InlineKeyboardButton(label, callback_data=f"edit_day:{d}"))
        if (i + 1) % 5 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

def is_date_in_valid_range(selected_date):
    """
    Memeriksa apakah tanggal yang dipilih berada dalam rentang +/- 7 hari dari hari ini.
    """
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)
    seven_days_later = today + timedelta(days=7)
    
    # Membandingkan hanya bagian tanggal (tanpa waktu)
    return seven_days_ago <= selected_date.date() <= seven_days_later

def is_registered(user_id):
    if not os.path.exists(PROFILE_PATH):
        return False
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return any(line.startswith(str(user_id) + "|") for line in f)

def save_profile(user_id, nama, posisi):
    with open(PROFILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{user_id}|{nama}|{posisi}\n")

def get_profile(user_id):
    if not os.path.exists(PROFILE_PATH):
        return None, None
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if parts[0] == str(user_id):
                if len(parts) >= 3:
                    return parts[1], parts[2]
    return None, None

def is_admin_user(user_id):
    if not os.path.exists(ADMIN_USER_PATH):
        return False
    with open(ADMIN_USER_PATH, "r", encoding="utf-8") as f:
        return str(user_id) in f.read().splitlines()

def save_user_as_admin(user_id):
    file_path = ADMIN_USER_PATH
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            saved_user_ids = file.read().splitlines()
    else:
        saved_user_ids = []
    if str(user_id) not in saved_user_ids:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(str(user_id) + "\n")
        print(f"User ID {user_id} telah disimpan di {file_path} sebagai admin.")
    else:
        print(f"User ID {user_id} sudah terdaftar sebagai admin di {file_path}.")

def get_navigation_buttons(stage, user_id):
    is_admin = is_admin_user(user_id)
    buttons = []
    line1 = []
    if stage > STAGE_TEAM:
        line1.append(KeyboardButton("/sebelumnya"))
    if stage not in [FINAL_RESULT, SPLIT_FINAL_RESULT, STAGE_SUBMIT, SPLIT_STAGE_SUBMIT]:
        line1.append(KeyboardButton("/selanjutnya"))
    buttons.append(line1)
    if is_admin:
        line2 = [
            KeyboardButton("/bersihkan"),
            
            KeyboardButton("/bantuan"),
        ]
        buttons.append(line2)
    else:
        line2 = [KeyboardButton("/bersihkan"), KeyboardButton("/bantuan")]
        buttons.append(line2)

    line3 = [KeyboardButton("/restart")]
    buttons.append(line3)
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_login_navigation_buttons():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("/restart")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_admin_menu():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("/remind"), KeyboardButton("/display")],
            [KeyboardButton("/sendreport")]
        ],
        resize_keyboard=True
    )

def send_custom_reminder(client, message):
    now = datetime.now()
    tanggal_hari_ini = now.strftime('%d%m%Y')
    base_dir = os.path.join(ADMIN_DAILY_DIR, tanggal_hari_ini)
    team_list = ['SKSO', 'CME', 'IOTA']
    sudah_submit = []
    belum_submit = []
    for team in team_list:
        team_dir = os.path.join(base_dir, team)
        if os.path.exists(team_dir):
            count = len([
                f for f in os.listdir(team_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf'))
            ])
            if count > 0:
                sudah_submit.append((team, count))
            else:
                belum_submit.append(team)
        else:
            belum_submit.append(team)
    notif = f"⏰ Reminder Laporan Harian\nHari ini: {now.strftime('%d-%m-%Y')}\n\n"
    if sudah_submit:
        notif += "✅ Tim yang sudah submit:\n" + "\n".join([f"✔ {team} ({cnt} laporan)" for team, cnt in sudah_submit]) + "\n\n"
    if belum_submit:
        notif += "🔴 Tim yang belum submit:\n" + "\n".join([f"🔴 {team}" for team in belum_submit]) + "\n"
    if not sudah_submit and not belum_submit:
        notif += "Semua tim belum submit hari ini.\n"
    notif += "\nMohon segera disubmit sebelum jam 15.00!\n"
    try:
        custom = message.text.split(" ", 1)[1]
        notif += f"\n📣 Pesan dari admin:\n{custom}"
    except IndexError:
        notif += "\n📣 Tidak ada pesan tambahan dari admin."
    all_ids = set()
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if parts and parts[0].isdigit():
                    all_ids.add(int(parts[0]))
    if os.path.exists(ADMIN_USER_PATH):
        with open(ADMIN_USER_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().isdigit():
                    all_ids.add(int(line.strip()))
    for uid in all_ids:
        try:
            client.send_message(uid, notif)
        except Exception as e:
            print(f"Gagal kirim ke {uid}: {e}")


user_data = {}

# ====================================================================
# STAGE DEFINITIONS
# ====================================================================
TECH_RE_REGISTER_NAME = "tech_re_register_name"
TECH_RE_REGISTER_POSITION = "tech_re_register_position"
ADMIN_AUTH_USERNAME = "admin_auth_username"
ADMIN_AUTH_PASSWORD = "admin_auth_password"
TECH_AUTH_TOKEN = "tech_auth_token"


STAGE_TEAM = 0
STAGE_BEFORE = 1
STAGE_PROGRESS = 2
STAGE_AFTER = 3
STAGE_REVIEW = 4
KEGIATAN = 5
LOKASI = 6
TANGGAL = 7
TEAM = 8
FINAL_RESULT = 9
STAGE_SUBMIT = 10

SPLIT_STAGE_PROGRESS = 11
SPLIT_STAGE_AFTER = 12
SPLIT_STAGE_REVIEW = 13
SPLIT_KEGIATAN = 14
SPLIT_LOKASI = 15
SPLIT_TANGGAL = 16
SPLIT_TEAM = 17
SPLIT_FINAL_RESULT = 18
SPLIT_STAGE_SUBMIT = 19

ADMIN_CHOOSE_REPORT_TYPE = 20
ADMIN_CHOOSE_TEAM = 21
ADMIN_REPORT_START = 22
ADMIN_REPORT_END = 30
ADMIN_BACK_TO_MENU = 31

# State untuk alur edit laporan admin
ADMIN_EDIT_CHOOSE_DATE = 40
ADMIN_EDIT_CHOOSE_REPORT = 41
ADMIN_EDIT_CHOOSE_FIELD = 42
ADMIN_EDIT_INPUT_LOKASI = 43
ADMIN_EDIT_INPUT_TANGGAL = 44
ADMIN_EDIT_INPUT_KEGIATAN = 45
ADMIN_EDIT_CONFIRM = 46

# State transition maps for technician and admin
TECH_MAINTENANCE_FLOW = {
    STAGE_TEAM: STAGE_BEFORE,
    STAGE_BEFORE: STAGE_PROGRESS,
    STAGE_PROGRESS: STAGE_AFTER,
    STAGE_AFTER: STAGE_REVIEW,
    STAGE_REVIEW: KEGIATAN,
    KEGIATAN: LOKASI,
    LOKASI: TANGGAL,
    TANGGAL: TEAM,
    TEAM: FINAL_RESULT,
    FINAL_RESULT: STAGE_SUBMIT,
    STAGE_SUBMIT: STAGE_TEAM,
}

TECH_PATROLI_FLOW = {
    STAGE_TEAM: SPLIT_STAGE_PROGRESS,
    SPLIT_STAGE_PROGRESS: SPLIT_STAGE_AFTER,
    SPLIT_STAGE_AFTER: SPLIT_STAGE_REVIEW,
    SPLIT_STAGE_REVIEW: SPLIT_KEGIATAN,
    SPLIT_KEGIATAN: SPLIT_LOKASI,
    SPLIT_LOKASI: SPLIT_TANGGAL,
    SPLIT_TANGGAL: SPLIT_TEAM,
    SPLIT_TEAM: SPLIT_FINAL_RESULT,
    SPLIT_FINAL_RESULT: SPLIT_STAGE_SUBMIT,
    SPLIT_STAGE_SUBMIT: STAGE_TEAM,
}

ADMIN_MAINTENANCE_FLOW = {
    ADMIN_CHOOSE_REPORT_TYPE: ADMIN_CHOOSE_TEAM,
    ADMIN_CHOOSE_TEAM: STAGE_BEFORE,
    STAGE_BEFORE: STAGE_PROGRESS,
    STAGE_PROGRESS: STAGE_AFTER,
    STAGE_AFTER: STAGE_REVIEW,
    STAGE_REVIEW: KEGIATAN,
    KEGIATAN: LOKASI,
    LOKASI: TANGGAL,
    TANGGAL: TEAM,
    TEAM: FINAL_RESULT,
    FINAL_RESULT: STAGE_SUBMIT,
    STAGE_SUBMIT: ADMIN_BACK_TO_MENU,
}

ADMIN_PATROLI_FLOW = {
    ADMIN_CHOOSE_REPORT_TYPE: ADMIN_CHOOSE_TEAM,
    ADMIN_CHOOSE_TEAM: SPLIT_STAGE_PROGRESS,
    SPLIT_STAGE_PROGRESS: SPLIT_STAGE_AFTER,
    SPLIT_STAGE_AFTER: SPLIT_STAGE_REVIEW,
    SPLIT_STAGE_REVIEW: SPLIT_KEGIATAN,
    SPLIT_KEGIATAN: SPLIT_LOKASI,
    SPLIT_LOKASI: SPLIT_TANGGAL,
    SPLIT_TANGGAL: SPLIT_TEAM,
    SPLIT_TEAM: SPLIT_FINAL_RESULT,
    SPLIT_FINAL_RESULT: SPLIT_STAGE_SUBMIT,
    SPLIT_STAGE_SUBMIT: ADMIN_BACK_TO_MENU,
}

def clear_text_file(user_id, stage_name):
    """Deletes the text file for a given stage."""
    file_path = os.path.join(BASE_TEMP_DIR, str(user_id), stage_name, f"{stage_name}.txt")
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")

def get_current_flow(user_id):
    is_admin = is_admin_user(user_id)
    activity_type = user_data[user_id].get("current_activity_type")
    
    if is_admin and user_data[user_id].get("admin_report_team"):
        if activity_type == "MAINTENANCE":
            return ADMIN_MAINTENANCE_FLOW
        elif activity_type == "PATROLI":
            return ADMIN_PATROLI_FLOW
    else:
        if activity_type == "MAINTENANCE":
            return TECH_MAINTENANCE_FLOW
        elif activity_type == "PATROLI":
            return TECH_PATROLI_FLOW
    return {}

def _handle_navigation(client, message, is_next):
    user_id = message.from_user.id
    current_stage = user_data[user_id]["stage"]
    flow = get_current_flow(user_id)
    
    # Mapping stages to their folder names for cleaning
    text_stage_map = {
        KEGIATAN: "Kegiatan", LOKASI: "Lokasi", TANGGAL: "Tanggal", TEAM: "Team",
        SPLIT_KEGIATAN: "Kegiatan", SPLIT_LOKASI: "Lokasi", SPLIT_TANGGAL: "Tanggal", SPLIT_TEAM: "Team"
    }

    if is_next:
        next_stage = flow.get(current_stage)
        if next_stage:
            user_data[user_id]["stage"] = next_stage
    else:
        # Hapus file teks dari stage saat ini saat mundur
        stage_name_to_clear = text_stage_map.get(current_stage)
        if stage_name_to_clear:
            clear_text_file(user_id, stage_name_to_clear)

        prev_stage = None
        for k, v in flow.items():
            if v == current_stage:
                prev_stage = k
                
                # Hapus file foto dari stage yang dituju saat mundur
                photo_stage_map = {
                    STAGE_PROGRESS: "before", STAGE_AFTER: "progress", STAGE_REVIEW: "after",
                    SPLIT_STAGE_AFTER: "1", SPLIT_STAGE_REVIEW: "2"
                }
                stage_name_to_clear = photo_stage_map.get(prev_stage)
                if stage_name_to_clear:
                    clear_current_stage_photos(user_id, prev_stage)

                break
        if prev_stage:
            user_data[user_id]["stage"] = prev_stage
    
    user_data[user_id]["photo_saving_active"] = False
    new_stage = user_data[user_id]["stage"]
    
    if new_stage == STAGE_BEFORE:
        handle_photo_stage(client, message, "before", STAGE_BEFORE, 4)
    elif new_stage == STAGE_PROGRESS:
        handle_photo_stage(client, message, "progress", STAGE_PROGRESS, 4)
    elif new_stage == STAGE_AFTER:
        handle_photo_stage(client, message, "after", STAGE_AFTER, 4)
    elif new_stage == SPLIT_STAGE_PROGRESS:
        handle_photo_stage(client, message, "1", SPLIT_STAGE_PROGRESS, 4)
    elif new_stage == SPLIT_STAGE_AFTER:
        handle_photo_stage(client, message, "2", SPLIT_STAGE_AFTER, 4)
    elif new_stage in [STAGE_REVIEW, SPLIT_STAGE_REVIEW]:
        handle_stage_review(client, message)
    elif new_stage in [KEGIATAN, SPLIT_KEGIATAN]:
        handle_empty_stage(client, message, "Kegiatan")
    elif new_stage in [LOKASI, SPLIT_LOKASI]:
        handle_empty_stage(client, message, "Lokasi")
    elif new_stage in [TANGGAL, SPLIT_TANGGAL]:
        handle_empty_stage(client, message, "Tanggal")
    elif new_stage in [TEAM, SPLIT_TEAM]:
        handle_empty_stage(client, message, "Team")
    elif new_stage in [FINAL_RESULT, SPLIT_FINAL_RESULT]:
        handle_final_result(client, message)
    
# ====================================================================
# CORE MESSAGE HANDLERS
# ====================================================================

@bot.on_message(filters.private & filters.command("start"))
def start_command_handler(client, message):
    user_id = message.from_user.id
    if is_admin_user(user_id):
        client.send_message(user_id, "Selamat datang kembali, Admin!", reply_markup=get_admin_menu())
        user_data[user_id] = {"stage": ADMIN_BACK_TO_MENU}
    elif is_registered(user_id):
        nama, posisi = get_profile(user_id)
        client.send_message(user_id, f"Selamat datang kembali {nama} dari tim {posisi}! Pilih jenis kegiatan:\n/MAINTENANCE atau /PATROLI.",
            reply_markup=get_navigation_buttons(STAGE_TEAM, user_id))
        user_data[user_id] = {
            "stage": STAGE_TEAM,
            "photo_saving_active": False,
            "profile": {"name": nama, "position": posisi}
        }
    else:
        keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("Login sebagai Admin")],
                [KeyboardButton("Login sebagai Teknisi")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        client.send_message(user_id, "Halo 👋! Silakan pilih jenis login Anda:", reply_markup=keyboard)
        user_data[user_id] = {"stage": "choose_login_type"}

@bot.on_message(filters.text & filters.private)
def handle_all_text_messages(client, message):
    user_id = message.from_user.id
    text = message.text.strip()
    if user_id not in user_data:
        user_data[user_id] = {"stage": "initial"}
    current_stage = user_data[user_id].get("stage")

    if current_stage == "choose_login_type":
        if text == "Login sebagai Admin":
            user_data[user_id]["stage"] = ADMIN_AUTH_USERNAME
            client.send_message(user_id, "Masukkan username admin:", reply_markup=get_login_navigation_buttons())
            return
        elif text == "Login sebagai Teknisi":
            user_data[user_id]["stage"] = "teknisi_token_input"
            client.send_message(user_id, "Masukkan password teknisi:", reply_markup=get_login_navigation_buttons())
            return

    if is_admin_user(user_id):
        if text.startswith("/remind"):
            send_custom_reminder(client, message)
            client.send_message(user_id, "Reminder berhasil dikirim.", reply_markup=get_admin_menu())
            return
        elif text == "/display":
            user_data[user_id]["stage"] = ADMIN_REPORT_START
            date_buttons = []
            for i in range(7):
                date_to_show = datetime.now() - timedelta(days=i)
                date_str = date_to_show.strftime('%d-%m-%Y')
                callback_data = date_to_show.strftime('%d%m%Y')
                date_buttons.append([InlineKeyboardButton(date_str, callback_data=f"display_date:{callback_data}")])
    
            date_buttons.append([InlineKeyboardButton("Kembali", callback_data="display_cancel")])
    
            keyboard = InlineKeyboardMarkup(date_buttons)
            client.send_message(user_id, "Pilih tanggal laporan yang ingin Anda tampilkan:", reply_markup=keyboard)
            return
        elif text == "/sendreport":
            user_data[user_id]["stage"] = ADMIN_CHOOSE_REPORT_TYPE
            report_type_kb = ReplyKeyboardMarkup(
                [
                    [KeyboardButton("/maintenance"), KeyboardButton("/patroli")],
                    [KeyboardButton("/kembali")]
                ], resize_keyboard=True, one_time_keyboard=True
            )
            client.send_message(user_id, "Silakan pilih jenis laporan yang akan dikirim:", reply_markup=report_type_kb)
            return
        elif text == "/kembali":
            user_data[user_id]["stage"] = ADMIN_BACK_TO_MENU
            client.send_message(user_id, "Anda kembali ke menu admin.", reply_markup=get_admin_menu())
            return
        elif text == "/jaditeknisi":
            if user_data[user_id].get("stage") not in [ADMIN_BACK_TO_MENU, "initial"]:
                client.send_message(user_id, "⚠ Proses laporan Anda akan dibatalkan untuk beralih peran. Jika ingin melanjutkan, tekan /jaditeknisi lagi.")
                user_data[user_id]["stage"] = "confirm_jaditeknisi"
                return
            
            user_data[user_id]["stage"] = TECH_AUTH_TOKEN
            client.send_message(user_id, "Anda beralih peran. Masukkan password teknisi untuk melanjutkan:", reply_markup=get_login_navigation_buttons())
            return
        elif current_stage == "confirm_jaditeknisi" and text == "/jaditeknisi":
            archive_directory(os.path.join(BASE_TEMP_DIR, str(user_id)))
            user_data[user_id]["stage"] = TECH_AUTH_TOKEN
            client.send_message(user_id, "Proses laporan dibatalkan. Masukkan password teknisi untuk melanjutkan:", reply_markup=get_login_navigation_buttons())
            return
        elif text == "/restart":
            user_data.pop(user_id, None)
            user_data[user_id] = {"stage": ADMIN_BACK_TO_MENU}
            archive_directory(os.path.join(BASE_TEMP_DIR, str(user_id)))
            client.send_message(user_id, "Proses laporan admin telah dibatalkan. Kembali ke menu admin.", reply_markup=get_admin_menu())
            return
        elif text in ["/MAINTENANCE", "/PATROLI"]:
            client.send_message(user_id, "❌ Anda terdaftar sebagai Admin. Gunakan perintah admin seperti /sendreport.")
            return

    if current_stage == TECH_AUTH_TOKEN:
        if text == PASSWORD_TEKNISI:
            user_data[user_id]["stage"] = "re_register_name"
            client.send_message(user_id, "✅ Password benar. Masukkan nama Anda untuk kembali ke akun teknisi:", reply_markup=get_login_navigation_buttons())
            remove_admin(user_id)
        else:
            client.send_message(user_id, "❌ Password salah. Proses dibatalkan. Silakan ketik /jaditeknisi lagi untuk mencoba.", reply_markup=get_admin_menu())
            user_data[user_id]["stage"] = ADMIN_BACK_TO_MENU
        return
        
    if current_stage == "re_register_name":
        nama = text
        user_data[user_id]["temp_name"] = nama
        user_data[user_id]["stage"] = "re_register_position"
        posisi_kb = ReplyKeyboardMarkup([
            [KeyboardButton("CME"), KeyboardButton("IOTA"), KeyboardButton("SKSO")]
        ], resize_keyboard=True, one_time_keyboard=True)
        client.send_message(user_id, "Masukkan posisi Anda (CME, IOTA, SKSO):", reply_markup=posisi_kb)
        return
    elif current_stage == "re_register_position":
        posisi = text.upper()
        if posisi in ["CME", "IOTA", "SKSO"]:
            nama = user_data[user_id]["temp_name"]
            if is_registered(user_id):
                remove_profile(user_id)
            save_profile(user_id, nama, posisi)
            user_data[user_id] = {
                "stage": STAGE_TEAM,
                "photo_saving_active": False,
                "profile": {"name": nama, "position": posisi}
            }
            client.send_message(user_id, f"✅ Anda berhasil beralih ke peran teknisi sebagai {nama} dari tim {posisi}! Pilih jenis kegiatan:\n/MAINTENANCE atau /PATROLI.",
                                reply_markup=get_navigation_buttons(STAGE_TEAM, user_id))
        else:
            client.send_message(user_id, "❌ Posisi tidak valid. Masukkan CME, IOTA, atau SKSO.", reply_markup=get_login_navigation_buttons())
        return

    if current_stage == ADMIN_AUTH_USERNAME:
        if text == ADMIN_USERNAME:
            user_data[user_id]["temp_username"] = text
            user_data[user_id]["stage"] = ADMIN_AUTH_PASSWORD
            client.send_message(user_id, "✅Username benar . Masukkan password admin:", reply_markup=get_login_navigation_buttons())
        else:
            client.send_message(user_id, "❌ Username salah. Proses dibatalkan. Silakan ketik /jadiadmin lagi untuk mencoba.", reply_markup=get_navigation_buttons(STAGE_TEAM, user_id))
            user_data[user_id]["stage"] = STAGE_TEAM
        return
    elif current_stage == ADMIN_AUTH_PASSWORD:
        if text == LOGIN_PASSWORD:
            if is_registered(user_id):
                remove_profile(user_id)
            save_user_as_admin(user_id)
            client.send_message(user_id, "✅ Otentikasi berhasil! Anda sekarang adalah Admin.", reply_markup=get_admin_menu())
            user_data[user_id] = {"stage": ADMIN_BACK_TO_MENU}  
        else:
            client.send_message(user_id, "❌ Password salah. Masukkan password admin:", reply_markup=get_login_navigation_buttons())
        return
    elif current_stage == "teknisi_token_input":
        if text == PASSWORD_TEKNISI:
            user_data[user_id]["stage"] = "teknisi_name_input"
            client.send_message(user_id, "✅ Password valid. Masukkan nama Anda:", reply_markup=get_login_navigation_buttons())
        else:
            client.send_message(user_id, "❌ Password tidak valid. Masukkan password teknisi Anda:", reply_markup=get_login_navigation_buttons())
        return
    elif current_stage == "teknisi_name_input":
        user_data[user_id]["temp_name"] = text
        user_data[user_id]["stage"] = "teknisi_position_input"
        posisi_kb = ReplyKeyboardMarkup([
            [KeyboardButton("CME"), KeyboardButton("IOTA"), KeyboardButton("SKSO")],
            [KeyboardButton("/kembali")]
        ], resize_keyboard=True, one_time_keyboard=True)
        client.send_message(user_id, "Masukkan posisi Anda (CME, IOTA, SKSO):", reply_markup=posisi_kb)
        return
    elif current_stage == "teknisi_position_input":
        posisi = text.upper()
        if posisi in ["CME", "IOTA", "SKSO"]:
            nama = user_data[user_id]["temp_name"]
            if is_registered(user_id):
                remove_profile(user_id)
            save_profile(user_id, nama, posisi)
            user_data[user_id] = {
                "stage": STAGE_TEAM,
                "photo_saving_active": False,
                "profile": {"name": nama, "position": posisi}
            }
            client.send_message(user_id, f"✅ Pendaftaran selesai, selamat datang {nama} dari tim {posisi}! Pilih jenis kegiatan:\n/MAINTENANCE atau /PATROLI.",
                                reply_markup=get_navigation_buttons(STAGE_TEAM, user_id))
        else:
            client.send_message(user_id, "❌ Posisi tidak valid. Masukkan CME, IOTA, atau SKSO.", reply_markup=get_login_navigation_buttons())
        return

    if text == "/jadiadmin":
        # Kalau belum teknisi, gak bisa lanjut
        if not is_registered(user_id):
            client.send_message(user_id, "Anda harus terdaftar sebagai teknisi terlebih dahulu.")
            return

        # Kalau sudah admin, langsung info
        if is_admin_user(user_id):
            client.send_message(user_id, "Anda sudah terdaftar sebagai admin.", reply_markup=get_admin_menu())
            return

        # Kalau sekarang masih proses laporan teknisi (bukan admin)
        if user_data[user_id].get("stage") not in [STAGE_TEAM, "initial"]:
            client.send_message(user_id, "⚠ Laporan Anda akan dibatalkan untuk beralih peran. Jika ingin melanjutkan, tekan /jadiadmin lagi.")
            user_data[user_id]["stage"] = "confirm_jadiadmin"
            return

        # Kalau aman, langsung mulai proses login admin
        user_data[user_id]["stage"] = ADMIN_AUTH_USERNAME
        client.send_message(user_id, "Anda telah memulai proses alih peran ke admin. Masukkan username admin:", reply_markup=get_login_navigation_buttons())
        return

    elif current_stage == "confirm_jadiadmin" and text == "/jadiadmin":
        archive_directory(os.path.join(BASE_TEMP_DIR, str(user_id)))
        user_data[user_id] = {"stage": ADMIN_AUTH_USERNAME}
        client.send_message(user_id, "Proses laporan dibatalkan. Masukkan username admin untuk melanjutkan:", reply_markup=get_login_navigation_buttons())
        return
    
    if text == "/jaditeknisi":
        if not is_admin_user(user_id):
            client.send_message(user_id, "Anda harus terdaftar sebagai admin terlebih dahulu untuk bisa beralih peran.")
            return
        
        if user_data[user_id].get("stage") not in [ADMIN_BACK_TO_MENU, "initial"]:
            client.send_message(user_id, "⚠ Proses laporan Anda akan dibatalkan untuk beralih peran. Jika ingin melanjutkan, tekan /jaditeknisi lagi.")
            user_data[user_id]["stage"] = "confirm_jaditeknisi"
            return
        
        user_data[user_id]["stage"] = TECH_AUTH_TOKEN
        client.send_message(user_id, "Anda beralih peran. Masukkan password teknisi untuk melanjutkan:", reply_markup=get_login_navigation_buttons())
        return
    elif current_stage == "confirm_jaditeknisi" and text == "/jaditeknisi":
        archive_directory(os.path.join(BASE_TEMP_DIR, str(user_id)))
        user_data[user_id]["stage"] = TECH_AUTH_TOKEN
        client.send_message(user_id, "Proses laporan dibatalkan. Masukkan password teknisi untuk melanjutkan:", reply_markup=get_login_navigation_buttons())
        return

    # --- Logika navigasi utama dan perintah lainnya ---
    if text == "/selanjutnya":
        _handle_navigation(client, message, True)
        return
    elif text == "/sebelumnya":
        _handle_navigation(client, message, False)
        return
    elif text == "/bersihkan":
        clear_current_stage_photos(user_id, user_data[user_id]["stage"])
        client.send_message(user_id, "Foto pada tahap ini telah dibersihkan.")
        return
    elif text == "/restart":
        user_data[user_id]["stage"] = STAGE_TEAM
        user_directory = os.path.join(BASE_TEMP_DIR, str(user_id))
        archive_directory(user_directory)
        client.send_message(
            chat_id=user_id,
            text="Proses laporan telah dimulai dari awal. Silakan pilih jenis kegiatan:\n/MAINTENANCE\n/PATROLI",
            reply_markup=get_navigation_buttons(STAGE_TEAM, user_id),
        )
        return
    elif text == "/bantuan":
        handle_help(client, message)
        return
    elif text == "/iya":
        current_stage = user_data[user_id]["stage"]
        if current_stage in [STAGE_SUBMIT, SPLIT_STAGE_SUBMIT]:
            handle_submit_stage(client, message, True)
        elif current_stage == ADMIN_EDIT_CONFIRM:
            save_edited_report_and_clean_up(client, user_id)
        else:
            client.send_message(user_id, "Perintah /iya tidak valid di tahap ini.")
        return
    elif text == "/tidak":
        current_stage = user_data[user_id]["stage"]
        if current_stage in [STAGE_SUBMIT, SPLIT_STAGE_SUBMIT]:
            handle_submit_stage(client, message, False)
        elif current_stage == ADMIN_EDIT_CONFIRM:
            client.send_message(user_id, "Pengeditan dibatalkan. Silakan pilih field lain untuk diedit atau tekan /restart.", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Kegiatan", callback_data="edit_field:Kegiatan")],
                [InlineKeyboardButton("Lokasi", callback_data="edit_field:Lokasi")],
                [InlineKeyboardButton("Tanggal", callback_data="edit_field:Tanggal")],
                [InlineKeyboardButton("✅ Selesai Edit", callback_data="edit_finish")]
            ]))
            user_data[user_id]["stage"] = ADMIN_EDIT_CHOOSE_FIELD
        else:
            client.send_message(user_id, "Perintah /tidak tidak valid di tahap ini.")
        return
    
    if is_admin_user(user_id) and text in ["/MAINTENANCE", "/PATROLI"]:
        client.send_message(user_id, "❌ Anda terdaftar sebagai Admin. Gunakan perintah admin seperti /sendreport.")
        return

    # --- Logika penanganan input teks untuk alur edit admin ---
    # --- Logika penanganan input teks untuk alur edit admin ---
    if is_admin_user(user_id) and "edit_target" in user_data[user_id]:
        edit_target = user_data[user_id]["edit_target"]
        
        # Langkah 1: Menerima input KEGIATAN baru
        if current_stage == ADMIN_EDIT_INPUT_KEGIATAN:
            report_data = edit_target.get("report_data", {})
            report_data["Kegiatan"] = text
            edit_target["report_data"] = report_data
            
            # Langsung ubah state dan minta LOKASI
            user_data[user_id]["stage"] = ADMIN_EDIT_INPUT_LOKASI
            client.send_message(user_id, f"✅ Kegiatan diubah menjadi '{text}'.\n\nSekarang, masukkan lokasi baru:")
            return

        # Langkah 2: Menerima input LOKASI baru
        elif current_stage == ADMIN_EDIT_INPUT_LOKASI:
            report_data = edit_target.get("report_data", {})
            report_data["Lokasi"] = text
            edit_target["report_data"] = report_data
            
            # Langsung ubah state dan minta TANGGAL
            user_data[user_id]["stage"] = ADMIN_EDIT_INPUT_TANGGAL
            client.send_message(user_id, f"✅ Lokasi diubah menjadi '{text}'.\n\nTerakhir, pilih tanggal baru untuk laporan:")
            client.send_message(user_id, "Pilih Tahun:", reply_markup=get_edit_year_inline_buttons())
            return

    if is_registered(user_id):
        if user_id not in user_data or "stage" not in user_data[user_id] or user_data[user_id].get("stage") == "initial":
            nama, posisi = get_profile(user_id)
            user_data[user_id] = {
                "stage": STAGE_TEAM,
                "photo_saving_active": False,
                "profile": {"name": nama, "position": posisi}
            }
            client.send_message(user_id, f"Selamat datang kembali {nama} dari tim {posisi}! Pilih jenis kegiatan:\n/MAINTENANCE atau /PATROLI.",
                                reply_markup=get_navigation_buttons(STAGE_TEAM, user_id))
            return
            
        stage = user_data[user_id]["stage"]
        if text == "/MAINTENANCE":
            user_data[user_id]["current_activity_type"] = "MAINTENANCE"
            user_data[user_id]["stage"] = STAGE_BEFORE
            archive_directory(os.path.join(BASE_TEMP_DIR, str(user_id)))
            handle_photo_stage(client, message, "before", STAGE_BEFORE, 4)
            return

        elif text == "/PATROLI":
            user_data[user_id]["current_activity_type"] = "PATROLI"
            user_data[user_id]["stage"] = SPLIT_STAGE_PROGRESS
            archive_directory(os.path.join(BASE_TEMP_DIR, str(user_id)))
            handle_photo_stage(client, message, "1", SPLIT_STAGE_PROGRESS, 4)
            return
        
        if user_data[user_id].get("current_activity_type") == "MAINTENANCE":
            if stage in [KEGIATAN, LOKASI, TANGGAL, TEAM]:
                handle_empty_stage(client, message, {KEGIATAN: "Kegiatan", LOKASI: "Lokasi", TANGGAL: "Tanggal", TEAM: "Team"}[current_stage])
                return
        elif user_data[user_id].get("current_activity_type") == "PATROLI":
            if stage in [SPLIT_KEGIATAN, SPLIT_LOKASI, SPLIT_TANGGAL, SPLIT_TEAM]:
                handle_empty_stage(client, message, {SPLIT_KEGIATAN: "Kegiatan", SPLIT_LOKASI: "Lokasi", SPLIT_TANGGAL: "Tanggal", SPLIT_TEAM: "Team"}[current_stage])
                return
    
    elif is_admin_user(user_id):
        if user_data[user_id].get("stage") == ADMIN_CHOOSE_REPORT_TYPE:
            if text == "/maintenance":
                user_data[user_id]["current_activity_type"] = "MAINTENANCE"
                user_data[user_id]["stage"] = ADMIN_CHOOSE_TEAM
                team_kb = ReplyKeyboardMarkup([
                    [KeyboardButton("CME"), KeyboardButton("IOTA"), KeyboardButton("SKSO")],
                    [KeyboardButton("/kembali")]
                ], resize_keyboard=True, one_time_keyboard=True)
                client.send_message(user_id, "Pilih tim untuk laporan ini:", reply_markup=team_kb)
                return
            elif text == "/patroli":
                user_data[user_id]["current_activity_type"] = "PATROLI"
                user_data[user_id]["stage"] = ADMIN_CHOOSE_TEAM
                team_kb = ReplyKeyboardMarkup([
                    [KeyboardButton("CME"), KeyboardButton("IOTA"), KeyboardButton("SKSO")],
                    [KeyboardButton("/kembali")]
                ], resize_keyboard=True, one_time_keyboard=True)
                client.send_message(user_id, "Pilih tim untuk laporan ini:", reply_markup=team_kb)
                return
        elif user_data[user_id].get("stage") == ADMIN_CHOOSE_TEAM:
            if text.upper() in ["CME", "IOTA", "SKSO"]:
                user_data[user_id]["admin_report_team"] = text.upper()
                _handle_navigation(client, message, True)
            else:
                client.send_message(user_id, "Nama tim tidak valid. Pilih dari CME, IOTA, SKSO.")
            return

        if user_data[user_id].get("current_activity_type") == "MAINTENANCE":
            if current_stage in [KEGIATAN, LOKASI, TANGGAL, TEAM]:
                handle_empty_stage(client, message, {KEGIATAN: "Kegiatan", LOKASI: "Lokasi", TANGGAL: "Tanggal", TEAM: "Team"}[current_stage])
                return
        elif user_data[user_id].get("current_activity_type") == "PATROLI":
            if current_stage in [SPLIT_KEGIATAN, SPLIT_LOKASI, SPLIT_TANGGAL, SPLIT_TEAM]:
                handle_empty_stage(client, message, {SPLIT_KEGIATAN: "Kegiatan", SPLIT_LOKASI: "Lokasi", SPLIT_TANGGAL: "Tanggal", SPLIT_TEAM: "Team"}[current_stage])
                return

    client.send_message(user_id, "Anda perlu login atau mendaftar untuk menggunakan bot. Silakan ketik /start.")
    user_data[user_id] = {"stage": "choose_login_type"}

# ====================================================================
# ORIGINAL FUNCTIONS (MODIFIED AS NECESSARY)
# ====================================================================

@bot.on_message(filters.command("/bantuan"))
def handle_help(client, message):
    message.reply_text(
        "langkah langkah membuat laporan:\n1. Stage before: anda dapat mengunggah foto laporan sebelum kegiatan berlangsung, anda dapat mengunggah maks 4 foto\n2. Stage progress.\n3. Stage after\n4. Preview: hasil sementara dari foto laporan yang telah diunggah,\nanda masih bisa mengganti foto dengan menekan tombol sebelumnya,\nhingga pada stage yang diinginkan dan mengunggah ulang foto kegiatan.\n5. Deskripsi kegiatan: anda dapat memberikan keterangan deskripsi kegiatan \npada laporan anda.\n6. Lokasi: anda dapat memberikan keterangan lokasi kegiatan,\npada laporan anda.\n7. Tanggal: berikan informasi tanggal kegiatan berlangsung.\n8. Team: anda dapat memberikan informasi Team yang melakukan kegiatan.\n\nKeterangan kegunaan tombol:\n1. /selanjutnya: lanjut ke tahap berikutnya.\n2. /sebelumnya: kembali ke tahap sebelumnya.\n3. /bersihkan: hapus semua foto yang telah diunggah pada tahap tersebut.\n4. /restart: mulai ulang pembuatan laporan.",
    )

def clear_current_stage_photos(user_id, stage):
    stage_map = {
        STAGE_BEFORE: "before", STAGE_PROGRESS: "progress", STAGE_AFTER: "after",
        SPLIT_STAGE_PROGRESS: "1", SPLIT_STAGE_AFTER: "2",
    }
    stage_name = stage_map.get(stage)
    if stage_name:
        user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), stage_name)
        if os.path.exists(user_dir):
            for filename in os.listdir(user_dir):
                file_path = os.path.join(user_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

def handle_photo_stage(client, message, stage_name, stage, max_photos=None):
    user_id = message.from_user.id
    user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), stage_name)
    user_data[user_id]["download_dir"] = user_dir
    user_data[user_id]["photo_saving_active"] = True
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    prompt_message = f"Stage {stage_name.capitalize()}: Unggah foto kegiatan."
    if max_photos:
        prompt_message += f" Anda bisa mengunggah maksimal {max_photos} foto."
    prompt_message += " Tekan '/selanjutnya' untuk langkah berikutnya."
    
    client.send_message(
        message.chat.id,
        prompt_message,
        reply_markup=get_navigation_buttons(stage, user_id),
    )

def handle_stage_review(client, message):
    user_id = message.from_user.id
    activity_type = user_data[user_id].get("current_activity_type")
    
    client.send_message(
        message.chat.id,
        "Stage Review",
        reply_markup=get_navigation_buttons(user_data[user_id]["stage"], user_id),
    )
    collage_review_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "collage_review")
    if not os.path.exists(collage_review_dir):
        os.makedirs(collage_review_dir)

    if activity_type == "PATROLI":
        split_progress_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "1")
        split_after_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "2")
        collage_paths = {
            "progress": create_collage_for_stage(split_progress_dir, "progress", user_id),
            "after": create_collage_for_stage(split_after_dir, "after", user_id),
        }
        template_image = Image.open(SPLIT_TEMPLATE_PATH)
        positions = {
            "progress": (204, 173),
            "after": (687, 173),
        }
    else: # MAINTENANCE
        before_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "before")
        progress_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "progress")
        after_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "after")
        collage_paths = {
            "before": create_collage_for_stage(before_dir, "before", user_id),
            "progress": create_collage_for_stage(progress_dir, "progress", user_id),
            "after": create_collage_for_stage(after_dir, "after", user_id),
        }
        template_image = Image.open(TEMPLATE_PATH)
        positions = {
            "before": (28, 173),
            "progress": (445, 173),
            "after": (861, 173),
        }
    for stage_key, collage_path in collage_paths.items():
        if collage_path:
            collage_image = Image.open(collage_path)
            template_image.paste(collage_image, positions[stage_key])
    review_image_path = os.path.join(collage_review_dir, "review_image.jpg")
    template_image.save(review_image_path)
    client.send_photo(message.chat.id, photo=review_image_path)

def create_collage_for_stage(folder_path, stage_name, user_id):
    collage_width = 400
    image_files = [
        f for f in os.listdir(folder_path) if f.lower().endswith(("png", "jpg", "jpeg"))
    ]
    if not image_files:
        return None
    images = []
    for image_file in image_files[-4:]:
        img_path = os.path.join(folder_path, image_file)
        img = Image.open(img_path)
        images.append(img)
    collage = create_collage(images, collage_width)
    collage = collage.resize((390, 390), Image.LANCZOS)
    padding_image = get_padding_image(len(images))
    if padding_image:
        collage.paste(padding_image, (0, 0), padding_image)
    collage_output_path = os.path.join(
        BASE_TEMP_DIR, str(user_id), "collage_review", f"{stage_name}_collage.jpg"
    )
    collage.save(collage_output_path)
    return collage_output_path

def get_padding_image(num_images):
    padding_files = {
        1: "oneimagepadding.png",
        2: "twoimagepadding.png",
        3: "triimagepadding.png",
        4: "fourimagepadding.png",
    }
    padding_file = padding_files.get(num_images)
    if padding_file:
        padding_image_path = os.path.join(BASE_TEMPLATES, padding_file)
        return Image.open(padding_image_path).convert("RGBA")
    return None

def create_collage(images, collage_width):
    num_images = len(images)
    if num_images == 1:
        square_size = collage_width
        collage_height = square_size
    elif num_images == 2:
        rect_width = collage_width // 2
        collage_height = rect_width * 2
    else:
        square_size = collage_width // 2
        vertical_rect_height = collage_width
        collage_height = vertical_rect_height
    collage_image = Image.new("RGB", (collage_width, collage_height), (255, 255, 255))
    def crop_to_aspect(image, target_width, target_height):
        width, height = image.size
        target_ratio = target_width / target_height
        image_ratio = width / height
        if image_ratio > target_ratio:
            new_width = int(target_ratio * height)
            left = (width - new_width) // 2
            right = left + new_width
            top, bottom = 0, height
        else:
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            bottom = top + new_height
            left, right = 0, width
        return image.crop((left, top, right, bottom))
    if num_images == 1:
        img = images[0]
        img = crop_to_aspect(img, collage_width, collage_width)
        img = img.resize((collage_width, collage_width), Image.LANCZOS)
        collage_image.paste(img, (0, 0))
    elif num_images == 2:
        for i in range(2):
            img = images[i]
            img = crop_to_aspect(img, collage_width // 2, collage_height)
            img = img.resize((collage_width // 2, collage_height), Image.LANCZOS)
            collage_image.paste(img, (i * (collage_width // 2), 0))
    elif num_images == 3:
        img = images[0]
        img = crop_to_aspect(img, collage_width // 2, collage_width)
        img = img.resize((collage_width // 2, collage_width), Image.LANCZOS)
        collage_image.paste(img, (0, 0))
        for i in range(1, 3):
            img = images[i]
            img = crop_to_aspect(img, collage_width // 2, collage_width // 2)
            img = img.resize((collage_width // 2, collage_width // 2), Image.LANCZOS)
            collage_image.paste(img, (collage_width // 2, (i - 1) * (collage_width // 2)))
    elif num_images == 4:
        x_offset = 0
        y_offset = 0
        for i, img in enumerate(images):
            img = crop_to_aspect(img, collage_width // 2, collage_width // 2)
            img = img.resize((collage_width // 2, collage_width // 2), Image.LANCZOS)
            collage_image.paste(img, (x_offset, y_offset))
            x_offset += collage_width // 2
            if (i + 1) % 2 == 0:
                x_offset = 0
                y_offset += collage_width // 2
    return collage_image

@bot.on_message(filters.photo & filters.private)
def save_photo(client, message):
    user_id = message.from_user.id
    if user_id not in user_data or not user_data[user_id].get("photo_saving_active", False):
        return
    user_dir = user_data[user_id]["download_dir"]
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    current_photo_count = len([name for name in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, name))])
    remaining_slots = 4 - current_photo_count
    if remaining_slots <= 0:
        client.send_message(message.chat.id, "Anda tidak bisa mengunggah lebih dari 4 foto.")
        return
    file_path = client.download_media(
        message.photo.file_id,
        file_name=os.path.join(user_dir, f"{message.photo.file_id}.jpg"),
    )
    client.send_message(message.chat.id, f"Foto berhasil disimpan.")

@bot.on_callback_query()
def handle_date_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id
    if user_id not in user_data:
        user_data[user_id] = {}

    # --- Bagian untuk Display Laporan Admin (Tidak Diubah) ---
    if data.startswith("display_date:"):
        selected_date_str = data.split(":")[1]
        send_all_images_by_date(client, chat_id, selected_date_str)
        client.edit_message_text(chat_id, message_id, f"Laporan untuk tanggal {datetime.strptime(selected_date_str, '%d%m%Y').strftime('%d-%m-%Y')} telah dikirim.")
        user_data[user_id]["stage"] = ADMIN_BACK_TO_MENU
        return
    elif data == "display_cancel":
        client.edit_message_text(chat_id, message_id, "Pemilihan tanggal dibatalkan. Kembali ke menu admin.", reply_markup=get_admin_menu())
        user_data[user_id]["stage"] = ADMIN_BACK_TO_MENU
        return

    # --- Alur Pembuatan Laporan Baru ---
    if data.startswith("year:"):
        year = int(data.split(":")[1])
        current_year = datetime.now().year
        if year != current_year:
            client.answer_callback_query(callback_query.id, f"❌ Tahun tidak valid! Hanya tahun {current_year} yang diizinkan.", show_alert=True)
            return
        user_data[user_id]["selected_year"] = year
        client.edit_message_text(chat_id, message_id, f"Tahun {year} dipilih. Pilih bulan:", reply_markup=get_month_inline_buttons())
    elif data.startswith("month_num:"):
        month_number = int(data.split(":")[1])
        today = datetime.now()
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=7)
        valid_months = {start_date.month, end_date.month}
        if month_number not in valid_months:
            client.answer_callback_query(callback_query.id, "❌ Bulan di luar rentang yang diizinkan.", show_alert=True)
            return
        user_data[user_id]["selected_month"] = month_number
        year = user_data[user_id].get("selected_year")
        months_indonesian = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        month_name_display = months_indonesian[month_number - 1]
        client.edit_message_text(chat_id, message_id, f"Bulan {month_name_display} dipilih. Pilih tanggal:", reply_markup=get_day_inline_buttons(year, month_number))
    elif data.startswith("day:"):
        day = int(data.split(":")[1])
        year = user_data[user_id].get("selected_year")
        month_num = user_data[user_id].get("selected_month")
        
        try:
            selected_dt = datetime(year, month_num, day)
        except (ValueError, TypeError):
            client.send_message(chat_id, "Terjadi kesalahan tanggal. Coba lagi.")
            return

        # Validasi tanggal: harus dalam rentang +/- 7 hari
        if not is_date_in_valid_range(selected_dt):
            client.answer_callback_query(callback_query.id, "❌ Tanggal di luar rentang yang diizinkan (7 hari sebelum/sesudah hari ini).", show_alert=True)
            return

        full_date_str = selected_dt.strftime("%d-%m-%Y")
        user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "Tanggal")
        os.makedirs(user_dir, exist_ok=True)
        text_filename = os.path.join(user_dir, "Tanggal.txt")
        with open(text_filename, "w", encoding="utf-8") as f:
            f.write(full_date_str + "\n")
        user_data[user_id]["Tanggal"] = full_date_str
        client.edit_message_text(chat_id, message_id, f"Tanggal {full_date_str} telah disimpan. Tekan '/selanjutnya' untuk melanjutkan.")

    # --- Alur Edit Laporan ---
    elif data.startswith("edit_report:"):
        if not is_admin_user(user_id):
            client.answer_callback_query(callback_query.id, "Anda tidak memiliki izin.")
            return

        parts = data.split(":")
        if len(parts) == 4:
            _, date, team, filename = parts
            original_report_path = os.path.join(ADMIN_DAILY_DIR, date, team, filename)
            if not os.path.exists(original_report_path):
                client.answer_callback_query(callback_query.id, "File laporan tidak ditemukan.")
                return
            
            # Persiapan data untuk edit...
            temp_user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "editing_report")
            os.makedirs(temp_user_dir, exist_ok=True)
            edited_filename = f"edited_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            edited_report_path = os.path.join(temp_user_dir, edited_filename)
            shutil.copy(original_report_path, edited_report_path)
            report_data_dict = extract_text_from_image(original_report_path)
            report_data_dict["Kegiatan"] = report_data_dict.get("Kegiatan", "N/A")
            report_data_dict["Lokasi"] = report_data_dict.get("Lokasi", "N/A")
            report_data_dict["Tanggal"] = datetime.now().strftime("%d-%m-%Y")
            report_data_dict["Team"] = team
            try:
                with Image.open(original_report_path) as img:
                    report_type = "PATROLI" if img.width < 1000 else "MAINTENANCE"
            except Exception:
                report_type = "MAINTENANCE"
            user_data[user_id]["edit_target"] = {
                "original_path": original_report_path, "temp_path": edited_report_path,
                "team": team, "date": date, "report_data": report_data_dict,
                "report_type": report_type
            }
            
            # Memulai alur edit sekuensial
            user_data[user_id]["stage"] = ADMIN_EDIT_INPUT_KEGIATAN
            client.edit_message_caption(chat_id, message_id, caption="📝 Proses Edit Dimulai.")
            client.send_message(chat_id, "Masukkan deskripsi kegiatan baru:")
        else:
            client.answer_callback_query(callback_query.id, "Data callback tidak valid.")

    elif data == "edit_cancel":
        if not is_admin_user(user_id):
            client.answer_callback_query(callback_query.id, "Anda tidak memiliki izin.")
            return
        user_data[user_id].pop("edit_target", None)
        temp_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "editing_report")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        client.delete_messages(chat_id, message_id)
        client.send_message(chat_id, "Pengeditan laporan dibatalkan.")
        user_data[user_id]["stage"] = ADMIN_BACK_TO_MENU

    elif user_data[user_id].get("stage") == ADMIN_EDIT_INPUT_TANGGAL and data.startswith("edit_year:"):
        year = int(data.split(":")[1])
        current_year = datetime.now().year
        if year != current_year:
            client.answer_callback_query(callback_query.id, f"❌ Tahun tidak valid! Hanya tahun {current_year} yang diizinkan.", show_alert=True)
            return
        user_data[user_id]["edit_target"]["report_data"]["year"] = year
        client.edit_message_text(chat_id, message_id, f"Tahun {year} dipilih. Pilih bulan:", reply_markup=get_edit_month_inline_buttons())
    elif user_data[user_id].get("stage") == ADMIN_EDIT_INPUT_TANGGAL and data.startswith("edit_month_num:"):
        month_number = int(data.split(":")[1])

        # Menambahkan validasi rentang bulan, sama seperti pada alur pembuatan laporan baru
        today = datetime.now()
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=7)
        valid_months = {start_date.month, end_date.month} # Ambil bulan awal dan akhir dari rentang
        
        if month_number not in valid_months:
            client.answer_callback_query(callback_query.id, "❌ Bulan di luar rentang yang diizinkan (7 hari sebelum/sesudah hari ini).", show_alert=True)
            return

        user_data[user_id]["edit_target"]["report_data"]["month"] = month_number
        year = user_data[user_id]["edit_target"]["report_data"].get("year")
        months_indonesian = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        month_name_display = months_indonesian[month_number - 1]
        client.edit_message_text(chat_id, message_id, f"Bulan {month_name_display} dipilih. Pilih hari:", reply_markup=get_edit_day_inline_buttons(year, month_number))
        
    elif user_data[user_id].get("stage") == ADMIN_EDIT_INPUT_TANGGAL and data.startswith("edit_day:"):
        day = int(data.split(":")[1])
        year = user_data[user_id]["edit_target"]["report_data"].get("year")
        month_num = user_data[user_id]["edit_target"]["report_data"].get("month")
        
        try:
            selected_dt = datetime(year, month_num, day)
        except (ValueError, TypeError):
            client.send_message(chat_id, "Terjadi kesalahan tanggal. Coba lagi.")
            return

        # Validasi tanggal: harus dalam rentang +/- 7 hari
        if not is_date_in_valid_range(selected_dt):
            client.answer_callback_query(callback_query.id, "❌ Tanggal di luar rentang yang diizinkan (7 hari sebelum/sesudah hari ini).", show_alert=True)
            return
            
        new_date_str = selected_dt.strftime("%d-%m-%Y")
        report_data = user_data[user_id]["edit_target"].get("report_data", {})
        report_data["Tanggal"] = new_date_str
        user_data[user_id]["edit_target"]["report_data"] = report_data
        
        temp_path = user_data[user_id]["edit_target"]["temp_path"]
        draw_on_report_image(temp_path, report_data, user_id)
        
        client.delete_messages(chat_id, message_id)
        
        final_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Simpan Perubahan", callback_data="final_save_edit"),
                InlineKeyboardButton("✏️ Edit Ulang", callback_data="restart_edit_flow")
            ],
            [InlineKeyboardButton("❌ Batalkan Semua", callback_data="edit_cancel")]
        ])

        client.send_photo(
            user_id, 
            photo=temp_path, 
            caption="Berikut adalah hasil akhir laporan yang diedit. Silakan simpan perubahan atau edit ulang dari awal.",
            reply_markup=final_keyboard
        )
        user_data[user_id]["stage"] = ADMIN_EDIT_CONFIRM

    elif data == "final_save_edit":
        if not is_admin_user(user_id) or "edit_target" not in user_data[user_id]:
            client.answer_callback_query(callback_query.id, "Terjadi kesalahan.")
            return
        save_edited_report_and_clean_up(client, user_id)
        client.delete_messages(chat_id, message_id)
        
    elif data == "restart_edit_flow":
        if not is_admin_user(user_id) or "edit_target" not in user_data[user_id]:
            client.answer_callback_query(callback_query.id, "Terjadi kesalahan.")
            return
        user_data[user_id]["stage"] = ADMIN_EDIT_INPUT_KEGIATAN
        client.delete_messages(chat_id, message_id)
        client.send_message(chat_id, "📝 Proses edit dimulai dari awal.\nSilakan masukkan kembali deskripsi kegiatan:")

def send_all_images_by_date(client, chat_id, report_date_str):
    base_dir = os.path.join(ADMIN_DAILY_DIR, report_date_str)
    
    if not os.path.exists(base_dir):
        client.send_message(chat_id, f"Laporan tidak tersedia untuk tanggal {datetime.strptime(report_date_str, '%d%m%Y').strftime('%d-%m-%Y')}.")
        return

    team_folders = ["SKSO", "CME", "IOTA"]
    found_reports = False

    for team in team_folders:
        team_dir = os.path.join(base_dir, team)
        if os.path.exists(team_dir):
            image_files = [f for f in os.listdir(team_dir) if os.path.isfile(os.path.join(team_dir, f)) and f.lower().endswith((".jpg", ".jpeg", ".png"))]
            if image_files:
                found_reports = True
                client.send_message(chat_id, f"📁 Laporan TIM {team} ({datetime.strptime(report_date_str, '%d%m%Y').strftime('%d-%m-%Y')}):")
                for f in image_files:
                    path = os.path.join(team_dir, f)
                    
                    edit_button = InlineKeyboardMarkup([
                        [InlineKeyboardButton("✏️ Edit Laporan", callback_data=f"edit_report:{report_date_str}:{team}:{f}")]
                    ])
                    try:
                        client.send_photo(chat_id, photo=path, reply_markup=edit_button)
                    except Exception as e:
                        print(f"Failed to send photo: {e}")
    
    if not found_reports:
        client.send_message(chat_id, f"Tidak ada laporan yang ditemukan untuk tanggal {datetime.strptime(report_date_str, '%d%m%Y').strftime('%d-%m-%Y')}.")
    else:
        client.send_message(chat_id, f"✅ Semua laporan untuk tanggal {datetime.strptime(report_date_str, '%d%m%Y').strftime('%d-%m-%Y')} telah dikirim.")


def handle_empty_stage(client, message, stage_name):
    user_id = message.from_user.id
    user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), stage_name)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    text_filename = os.path.join(user_dir, f"{stage_name}.txt")
    
    if message.text == "/bersihkan":
        clear_text_file(user_id, stage_name)
        client.send_message(message.chat.id, f"Teks telah dibersihkan dari {stage_name}.")
        if stage_name == "Tanggal":
            client.send_message(message.chat.id, "Pilih tahun:", reply_markup=get_year_inline_buttons())
        return
    elif stage_name == "Tanggal":
        if os.path.exists(text_filename) and os.stat(text_filename).st_size > 0:
            with open(text_filename, "r", encoding="utf-8") as text_file:
                content = text_file.read().strip()
            client.send_message(message.chat.id, f"Tanggal sudah terisi: '{content}'. Tekan /selanjutnya untuk melanjutkan.")
        else:
            client.send_message(message.chat.id, "Pilih tahun:", reply_markup=get_year_inline_buttons())
        return
    elif stage_name == "Team":
        if is_admin_user(user_id):
            team_pos = user_data[user_id].get("admin_report_team", "N/A")
        else:
            _, team_pos = get_profile(user_id)
        
        user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "Team")
        os.makedirs(user_dir, exist_ok=True)
        text_filename = os.path.join(user_dir, "Team.txt")
        with open(text_filename, "w", encoding="utf-8") as text_file:
            text_file.write(team_pos + "\n")
        client.send_message(message.chat.id, f"Tim Anda secara otomatis terdeteksi sebagai {team_pos}. Tekan /selanjutnya untuk melanjutkan.",
                            reply_markup=get_navigation_buttons(user_data[user_id]["stage"], user_id))
        return
    
    elif message.text not in ["/start", "/bantuan", "/selanjutnya", "/sebelumnya", "/bersihkan", "/jadiadmin", "/jaditeknisi", "/kembali"]:
        with open(text_filename, "w", encoding="utf-8") as text_file:
            text_file.write(message.text + "\n")
        
        client.send_message(
            message.chat.id,
            f"{stage_name} telah disimpan!. Tekan '/selanjutnya' untuk melanjutkan.",
            reply_markup=get_navigation_buttons(user_data[user_id]["stage"], user_id)
        )
    else:
        client.send_message(message.chat.id, f"Masukkan {stage_name}:", reply_markup=get_navigation_buttons(user_data[user_id]["stage"], user_id))

def handle_submit_stage(client, message, confirm_submit):
    user_id = message.from_user.id
    user_directory = os.path.join(BASE_TEMP_DIR, str(user_id))
    review_image_path = os.path.join(
        BASE_TEMP_DIR, str(user_id), "collage_review", "final_result.jpg"
    )

    if not os.path.exists(review_image_path):
        client.send_message(message.chat.id, "Tidak ada laporan untuk disubmit. Silakan mulai laporan baru.")
        # Membersihkan sisa folder jika ada
        if os.path.exists(user_directory):
            shutil.rmtree(user_directory)
        
        if is_admin_user(user_id):
            user_data[user_id]["stage"] = ADMIN_BACK_TO_MENU
            client.send_message(user_id, "Kembali ke menu admin.", reply_markup=get_admin_menu())
        else:
            if user_id in user_data:
                user_data[user_id]["stage"] = STAGE_TEAM
        return

    if confirm_submit:
        image = Image.open(review_image_path)
        save_image_admin(image, user_id, is_admin_user(user_id))
        client.send_message(message.chat.id, "✅ Laporan berhasil disubmit!")
        # Setelah berhasil submit, direktori diarsipkan seperti biasa
        archive_directory(user_directory)
    else:
        # =======================================================
        # MODIFIKASI DIMULAI DI SINI (Koreksi dari Bily on the Wall)
        # =======================================================
        client.send_message(message.chat.id, "Laporan dibatalkan dan semua file sementara telah dihapus.")
        
        # Hapus direktori temporary pengguna secara permanen
        if os.path.exists(user_directory):
            try:
                shutil.rmtree(user_directory)
                print(f"Direktori temp untuk user {user_id} telah dihapus karena pembatalan.")
            except OSError as e:
                print(f"Error saat menghapus direktori temp {user_id}: {e}")

        # Cari dan hapus juga folder yang mungkin sudah terarsip dari sesi ini
        # Ini untuk kasus jika pengguna sempat /restart sebelumnya
        for item in os.listdir(ARCHIVE_DIR):
            if item.startswith(str(user_id) + "_"):
                path_to_delete = os.path.join(ARCHIVE_DIR, item)
                try:
                    shutil.rmtree(path_to_delete)
                    print(f"Direktori arsip {item} telah dihapus karena pembatalan.")
                except OSError as e:
                    print(f"Error saat menghapus direktori arsip {item}: {e}")
    
    # Atur ulang state pengguna setelah proses selesai (baik submit maupun batal)
    if is_admin_user(user_id):
        user_data[user_id] = {"stage": ADMIN_BACK_TO_MENU}
        client.send_message(user_id, "Kembali ke menu admin.", reply_markup=get_admin_menu())
    else:
        user_data[user_id] = {"stage": STAGE_TEAM}
        client.send_message(
            chat_id=user_id,
            text="Proses selesai. Klik /restart untuk membuat laporan baru.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("/restart")]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )

def handle_final_result(client, message):
    user_id = message.from_user.id
    review_image_path = os.path.join(
        BASE_TEMP_DIR, str(user_id), "collage_review", "review_image.jpg"
    )
    if not os.path.exists(review_image_path):
        client.send_message(
            message.chat.id, "Review image tidak ditemukan. Silakan ulangi proses atau /restart."
        )
        return
    image = Image.open(review_image_path)
    draw = ImageDraw.Draw(image)
    font_path = "arialbd.ttf"
    font_size = 16
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font file not found at {font_path}. Using default font.")
        font = ImageFont.load_default()
    labels = ["KEGIATAN :", "LOKASI :", "TANGGAL :", "TEAM :"]
    text_items = ["Kegiatan", "Lokasi", "Tanggal", "Team"]
    y_coordinates = [625, 649, 671, 694]
    
    is_admin_report = is_admin_user(user_id) and user_data[user_id].get("admin_report_team")

    for label, text_item, y in zip(labels, text_items, y_coordinates):
        content = "N/A"
        if is_admin_report and text_item == "Team":
            content = user_data[user_id].get("admin_report_team", "N/A")
        elif text_item == "Team":
            _, team_pos = get_profile(user_id)
            content = team_pos if team_pos else "N/A"
        else:
            text_path = os.path.join(
                BASE_TEMP_DIR, str(user_id), text_item, f"{text_item}.txt"
            )
            if os.path.exists(text_path):
                with open(text_path, "r", encoding="utf-8") as file:
                    content = file.read().strip()
        combined_text = f"{label} {content}"
        text_bbox = draw.textbbox((0, 0), combined_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x_coordinate = (image.width - text_width) // 2
        draw.text((x_coordinate, y), combined_text, fill="black", font=font)
    final_image_path = os.path.join(
        BASE_TEMP_DIR, str(user_id), "collage_review", "final_result.jpg"
    )
    image.save(final_image_path)
    client.send_photo(message.chat.id, photo=final_image_path)
    
    kb = ReplyKeyboardMarkup([
        [KeyboardButton("/iya"), KeyboardButton("/tidak")]
    ], resize_keyboard=True, one_time_keyboard=True)
    
    if is_admin_report:
        client.send_message(message.chat.id, "Submit laporan ini atas nama tim yang dipilih ke admin?\n /iya      /tidak", reply_markup=kb)
        user_data[user_id]["stage"] = STAGE_SUBMIT
    else:
        client.send_message(message.chat.id, "Submit ke admin?\n /iya      /tidak", reply_markup=kb)
        user_data[user_id]["stage"] = STAGE_SUBMIT

def save_image_admin(image, user_id, is_admin_submitting):
    # MODIFIKASI: Baca tanggal dari file sementara, bukan dari tanggal sistem
    try:
        tanggal_path = os.path.join(BASE_TEMP_DIR, str(user_id), "Tanggal", "Tanggal.txt")
        with open(tanggal_path, "r", encoding="utf-8") as f:
            tanggal_laporan_str = f.read().strip()
        # Ubah format tanggal dari DD-MM-YYYY menjadi DDMMYYYY untuk nama folder
        report_date_folder_name = datetime.strptime(tanggal_laporan_str, '%d-%m-%Y').strftime('%d%m%Y')
    except (FileNotFoundError, ValueError):
        # Fallback jika file tidak ada atau formatnya salah, gunakan tanggal hari ini
        print(f"Peringatan: File Tanggal.txt tidak ditemukan untuk user {user_id}. Menggunakan tanggal hari ini sebagai fallback.")
        report_date_folder_name = datetime.now().strftime('%d%m%Y')

    if is_admin_submitting and "admin_report_team" in user_data[user_id]:
        team_name = user_data[user_id]["admin_report_team"]
    else:
        _, team_name = get_profile(user_id)
        if team_name not in ["SKSO", "CME", "IOTA"]:
            team_name = "UNCLASSIFIED"
            
    # Gunakan nama folder tanggal yang sudah ditentukan dari input pengguna
    admin_dir = os.path.join(ADMIN_DAILY_DIR, report_date_folder_name, team_name)
    os.makedirs(admin_dir, exist_ok=True)
    
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d%m%Y-%H%M%S")
    file_name = f"final_result_{formatted_time}.jpg"
    file_path = os.path.join(admin_dir, file_name)
    image.save(file_path)

def archive_directory(directory):
    try:
        if os.path.exists(directory):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_dir_name = os.path.basename(directory) + f"_{timestamp}"
            archive_path = os.path.join(ARCHIVE_DIR, new_dir_name)
            shutil.move(directory, archive_path)
            print(f"Moved directory {directory} to archive {archive_path}")
    except Exception as e:
        print(f"Error archiving directory: {str(e)}")

def clear_old_archives():
    while True:
        try:
            now = datetime.now()
            for item in os.listdir(ARCHIVE_DIR):
                item_path = os.path.join(ARCHIVE_DIR, item)
                if os.path.isdir(item_path):
                    try:
                        # Asumsi format nama folder: original_name_YYYYMMDD_HHMMSS
                        date_str = item.split('_')[-2]
                        archive_date = datetime.strptime(date_str, "%Y%m%d")
                        if now - archive_date > timedelta(days=7):
                            shutil.rmtree(item_path)
                            print(f"Deleted old archive: {item_path}")
                    except (ValueError, IndexError):
                        print(f"Could not parse date from archive name: {item}")
        except Exception as e:
            print(f"Error clearing old archives: {str(e)}")
        time.sleep(3600)  # Cek setiap jam


def send_all_images(client, chat_id):
    admin_img_path = datetime.now().strftime('%d%m%Y')
    base_dir = os.path.join(ADMIN_DAILY_DIR, admin_img_path)
    weekly_reset(ADMIN_DAILY_DIR)
    if not os.path.exists(base_dir):
        client.send_message(chat_id, "Laporan harian tidak tersedia untuk hari ini.")
        return
    team_folders = ["SKSO", "CME", "IOTA", "UNCLASSIFIED"]
    main_files = [
        f for f in os.listdir(base_dir)
        if os.path.isfile(os.path.join(base_dir, f)) and f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    if main_files:
        client.send_message(chat_id, f"📁 Laporan TANPA TIM ({admin_img_path}):")
        for f in main_files:
            path = os.path.join(base_dir, f)
            client.send_photo(chat_id, photo=path)
    for team in team_folders:
        team_dir = os.path.join(base_dir, team)
        if os.path.exists(team_dir):
            image_files = [
                f for f in os.listdir(team_dir)
                if os.path.isfile(os.path.join(team_dir, f)) and f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
            if image_files:
                client.send_message(chat_id, f"📁 Laporan TIM {team} ({admin_img_path}):")
                for f in image_files:
                    client.send_photo(chat_id, photo=os.path.join(team_dir, f))
    client.send_message(chat_id, "✅ Semua laporan telah dikirim.")

def load_text_from_file(data_filename, user_id, folder_name):
    file_path = os.path.join(BASE_TEMP_DIR, str(user_id), folder_name, data_filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            return content
    return None

def img_verification(dir):
    for file in os.listdir(dir):
        if file.lower().endswith('.jpg'):
            return True
    return False

def weekly_reset(admin_dir):
    today = datetime.now().strftime('%d%m%Y')
    
    # Hitung tanggal 7 hari yang lalu
    seven_days_ago = datetime.now() - timedelta(days=7)

    for folder_name in os.listdir(admin_dir):
        folder_path = os.path.join(admin_dir, folder_name)

        if os.path.isdir(folder_path):
            try:
                # Coba ubah nama folder menjadi format tanggal
                # Folder_name format: DDMMYYYY
                folder_date = datetime.strptime(folder_name, '%d%m%Y')

                # Cek apakah tanggal folder lebih lama dari 7 hari yang lalu
                if folder_date < seven_days_ago:
                    shutil.rmtree(folder_path)
                    print(f'Folder {folder_name} (lebih dari 7 hari) telah dihapus.')
                else:
                    # Jika folder masih dalam rentang 7 hari atau merupakan folder hari ini, jangan dihapus
                    print(f'Folder {folder_name} masih dalam periode penyimpanan.')

            except ValueError:
                # Abaikan folder yang namanya tidak sesuai format tanggal
                print(f'Mengabaikan folder {folder_name} karena format nama tidak valid.')
    
    print(f'Pembersihan folder laporan lama (lebih dari 7 hari) telah selesai.')

def reminder_tim_belum_lapor():
    while True:
        now = datetime.now()
        if now.strftime('%H:%M') == '14:30':
            tanggal_hari_ini = now.strftime('%d%m%Y')
            base_dir = os.path.join(ADMIN_DAILY_DIR, tanggal_hari_ini)
            team_list = ['SKSO', 'CME', 'IOTA']
            sudah_submit = []
            belum_submit = []
            for team in team_list:
                team_dir = os.path.join(base_dir, team)
                if os.path.exists(team_dir):
                    jumlah = len([
                        f for f in os.listdir(team_dir)
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                    ])
                    if jumlah > 0:
                        sudah_submit.append((team, jumlah))
                    else:
                        belum_submit.append(team)
                else:
                    belum_submit.append(team)
            notif = f"⏰ Reminder Laporan Harian\nHari ini: {now.strftime('%d-%m-%Y')}\n\n"
            if sudah_submit:
                notif += "✅ Tim yang sudah submit:\n"
                for team, count in sudah_submit:
                    notif += f"✔ {team} ({count} laporan)\n"
                notif += "\n"
            if belum_submit:
                notif += "🔴 Tim yang belum submit:\n"
                for team in belum_submit:
                    notif += f"🔴 {team}\n"
            if not sudah_submit and not belum_submit:
                notif += "Semua tim belum submit hari ini."
            notif += "\n\nMohon segera disubmit sebelum jam 15.00!"
            user_ids = set()
            if os.path.exists(PROFILE_PATH):
                with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("|")
                        if parts and parts[0].isdigit():
                            user_ids.add(int(parts[0]))
            if os.path.exists(ADMIN_USER_PATH):
                with open(ADMIN_USER_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().isdigit():
                            user_ids.add(int(line.strip()))
            for uid in user_ids:
                try:
                    msg = bot.send_message(uid, notif)
                    try:
                        chat_info = bot.get_chat(uid)
                        username = chat_info.username if chat_info.username else 'N/A'
                        print(f"[BERHASIL] Notif dikirim ke ID: {uid}, Username: @{username}")
                    except Exception as chat_e:
                        print(f"[BERHASIL] Notif dikirim ke ID: {uid}, Gagal dapat username: {chat_e}")
                except Exception as e:
                    print(f"[GAGAL] Kirim ke {uid}: {e}")
            time.sleep(61)
        else:
            time.sleep(30)

def remove_profile(user_id):
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            for line in lines:
                if not line.startswith(str(user_id) + "|"):
                    f.write(line)

def remove_admin(user_id):
    if os.path.exists(ADMIN_USER_PATH):
        with open(ADMIN_USER_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open(ADMIN_USER_PATH, "w", encoding="utf-8") as file:
            for line in lines:
                if line.strip() != str(user_id):
                    file.write(line)
        print(f"User ID {user_id} telah dihapus dari {ADMIN_USER_PATH} sebagai admin.")

                    
def save_edited_report_and_clean_up(client, user_id):
    edit_info = user_data[user_id].get("edit_target")
    if not edit_info:
        client.send_message(user_id, "Terjadi kesalahan saat menyimpan. Mohon coba lagi.")
        return
        
    original_report_path = edit_info["original_path"]
    temp_edited_path = edit_info["temp_path"]
    final_report_data = edit_info.get("report_data", {})

    # MODIFIKASI: Tentukan folder tujuan baru berdasarkan tanggal yang diedit
    try:
        new_date_str = final_report_data.get("Tanggal")
        team_name = final_report_data.get("Team")
        
        # Ubah format tanggal dari DD-MM-YYYY menjadi DDMMYYYY untuk nama folder
        new_date_folder_name = datetime.strptime(new_date_str, '%d-%m-%Y').strftime('%d%m%Y')
        
        # Buat path folder tujuan yang baru
        new_destination_folder = os.path.join(ADMIN_DAILY_DIR, new_date_folder_name, team_name)
        os.makedirs(new_destination_folder, exist_ok=True)

    except (ValueError, TypeError):
        client.send_message(user_id, "Terjadi kesalahan format tanggal saat menyimpan. Laporan disimpan di folder tanggal asli.")
        # Fallback: simpan ke folder asli jika ada error
        new_destination_folder = os.path.dirname(original_report_path)

    # Hapus file laporan lama dari lokasi aslinya
    if os.path.exists(original_report_path):
        os.remove(original_report_path)
    
    # Buat nama file baru dan pindahkan file dari temp ke folder tujuan baru
    new_filename = f"edited_report_{datetime.now().strftime('%d%m%Y-%H%M%S')}.jpg"
    final_path = os.path.join(new_destination_folder, new_filename)
    shutil.move(temp_edited_path, final_path)
    
    # Bersihkan sisa data edit
    temp_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "editing_report")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    user_data[user_id].pop("edit_target", None)
    client.send_message(user_id, f"✅ Perubahan berhasil disimpan ke folder tanggal {new_date_str}!")
    client.send_message(user_id, "Kembali ke menu admin.", reply_markup=get_admin_menu())

def extract_text_from_image(image_path):
    report_data = {
        "Kegiatan": "N/A",
        "Lokasi": "N/A",
        "Tanggal": "N/A",
        "Team": "N/A"
    }

    image_name = os.path.basename(image_path)
    try:
        date_part = image_name.split('_')[-1].split('-')[0]
        report_data["Tanggal"] = datetime.strptime(date_part, '%d%m%Y').strftime('%d-%m-%Y')
    except (IndexError, ValueError):
        pass
    
    try:
        team_part = os.path.basename(os.path.dirname(image_path))
        if team_part in ["SKSO", "CME", "IOTA", "UNCLASSIFIED"]:
            report_data["Team"] = team_part
    except:
        pass
        
    return report_data

def draw_on_report_image(output_path, report_data, user_id):
    # Dapatkan tipe laporan yang sedang diedit
    report_type = user_data[user_id].get("edit_target", {}).get("report_type", "MAINTENANCE")
    
    if report_type == "PATROLI":
        template_path = SPLIT_TEMPLATE_PATH
        positions = {
            "before": None,
            "progress": (204, 173),
            "after": (687, 173),
        }
    else: # MAINTENANCE
        template_path = TEMPLATE_PATH
        positions = {
            "before": (28, 173),
            "progress": (445, 173),
            "after": (861, 173),
        }

    image_base = Image.open(template_path).copy()
    draw = ImageDraw.Draw(image_base)
    font_path = "arialbd.ttf"
    font_size = 16
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    labels = ["KEGIATAN :", "LOKASI :", "TANGGAL :", "TEAM :"]
    text_items = ["Kegiatan", "Lokasi", "Tanggal", "Team"]
    y_coordinates = [625, 649, 671, 694]
    
    # Mendapatkan path laporan asli dari user_data
    original_report_path = user_data[user_id].get("edit_target", {}).get("original_path")
    if original_report_path:
        try:
            original_image = Image.open(original_report_path)
            if report_type == "PATROLI":
                # Mengambil bagian atas yang berisi foto dari laporan asli Patroli
                image_to_paste = original_image.crop((0, 0, original_image.width, 600))
                image_to_paste = image_to_paste.resize((854, 600), Image.LANCZOS)
            else: # MAINTENANCE
                # Mengambil bagian atas yang berisi foto dari laporan asli Maintenance
                image_to_paste = original_image.crop((0, 0, original_image.width, 600))
                image_to_paste = image_to_paste.resize((1280, 600), Image.LANCZOS)
                
            image_base.paste(image_to_paste, (0,0))
        except Exception as e:
            print(f"Gagal memuat foto asli dari laporan lama: {e}")

    # Menggambar ulang semua teks di atas template
    for label, text_item, y in zip(labels, text_items, y_coordinates):
        content = report_data.get(text_item, "N/A")
        combined_text = f"{label} {content}"
        text_bbox = draw.textbbox((0, 0), combined_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x_coordinate = (image_base.width - text_width) // 2
        draw.text((x_coordinate, y), combined_text, fill="black", font=font)
    
    image_base.save(output_path)


threading.Thread(target=reminder_tim_belum_lapor, daemon=True).start()
threading.Thread(target=clear_old_archives, daemon=True).start()

print("Bot aktif.")
bot.run()