import os
import shutil
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup

bot = Client(
    "Arnet Report Generator",
    api_id=27678267,
    api_hash="c08a0892e705880cdda74668455b676b",
    bot_token="7392002890:AAGFnEO9PI2hEtKZ__YPz4W1KFj7bbpQOHI",
)

ADMIN_IMG_DIR = "D:/Arnet-TelBot/admin_storage/daily-reports"
ADMIN_DIR = "D:/Arnet-TelBot/admin_storage"
BASE_TEMP_DIR = "D:/Arnet-TelBot/temp"
TEMPLATE_PATH = "D:/Arnet-TelBot/template/review_template.jpg"
SPLIT_TEMPLATE_PATH = "D:/Arnet-TelBot/template/split_review_template.jpg"
BASE_TEMPLATES = "D:/Arnet-TelBot/template"

# Define stages

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


# Initialize user data dictionary
user_data = {}


def get_navigation_buttons(stage, user, message):
    user_id = message.from_user.id
    saved_user_id = load_user_id(user_id, "userdata.txt")
    buttons = []

    # Baris pertama: selanjutnya dan sebelumnya
    line1 = []
    if stage > STAGE_TEAM:
        line1.append(KeyboardButton("/sebelumnya"))
    if stage < SPLIT_STAGE_SUBMIT:  # Updated to include Final Result
        line1.append(KeyboardButton("/selanjutnya"))
    buttons.append(line1)

    # Baris kedua: bersihkan dan bantuan
    if saved_user_id == True:
        line2 = [
            KeyboardButton("/bersihkan"),
            KeyboardButton("/display"),
            KeyboardButton("/bantuan"),
        ]
        buttons.append(line2)
    else:
        line2 = [KeyboardButton("/bersihkan"), KeyboardButton("/bantuan")]
        buttons.append(line2)

    # Baris ketiga: Restart
    line3 = [KeyboardButton("/restart")]
    buttons.append(line3)

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


@bot.on_message(filters.text & filters.private)
def handle_stage(client, message):
    user_id = message.from_user.id
    user_team_verification = None
    saved_user_id = load_user_id(user_id, "userdata.txt")
    user_team = load_text_from_file("role.txt", str(user_id), str("role"))
    user_team_verification = load_user_id(user_team, "userteam.txt")

    if user_team_verification == True:
        if user_id not in user_data:
            user_data[user_id] = {
                "stage": SPLIT_STAGE_PROGRESS,
                "photo_saving_active": False,
            }

        stage = user_data[user_id]["stage"]

        if message.text == "/selanjutnya":
            if stage == 0:
                user_data[user_id]["stage"] += 11
                user_data[user_id]["photo_saving_active"] = False
            elif stage < 19:  # Include the final result stage
                user_data[user_id]["stage"] += 1
                user_data[user_id]["photo_saving_active"] = False
        elif message.text == "/sebelumnya":
            if stage > 11:
                user_data[user_id]["stage"] -= 1
        elif message.text == "/bersihkan":
            clear_current_stage_photos(user_id, stage)
        elif message.text == "/restart":
            # Reset to initial stage and clear any stage-specific data
            user_data[user_id]["stage"] = STAGE_TEAM
            user_data[user_id]["team"] = None  # Clear previously selected team
            user_team_verification = None
            # Clean up the directory after sending the image
            user_directory = os.path.join(BASE_TEMP_DIR, str(user_id))
            clear_download_directory(user_directory)
            client.send_message(
                chat_id=user_id,
                text="Proses telah dimulai dari awal.",
                reply_markup=get_navigation_buttons(STAGE_TEAM, user_id, message),
            )
            client.send_message(
                chat_id=user_id, text="Terjadi kesalahan. /restart untuk mengulangi"
            )
        elif message.text == "/bantuan":
            handle_help(bot, message)
        elif message.text == "/iya":
            handle_submit_stage(client, message)
        elif message.text == "/tidak":
            handle_submit_stage(client, message)
        elif message.text == "/display":
            if saved_user_id == True:
                send_all_images(client, message.chat.id, ADMIN_IMG_DIR)
        elif message.text == "/requestadminauthorization":
            handle_save_user_id(client, message)

        stage = user_data[user_id]["stage"]

        if stage == 11:
            handle_photo_stage(client, message, "1", SPLIT_STAGE_PROGRESS, 4)
        elif stage == 12:
            handle_photo_stage(client, message, "2", SPLIT_STAGE_AFTER, 4)
        elif stage == 13:
            handle_stage_review(client, message)
        elif stage == 14:
            handle_empty_stage(client, message, "Kegiatan")
        elif stage == 15:
            handle_empty_stage(client, message, "Lokasi")
        elif stage == 16:
            handle_empty_stage(client, message, "Tanggal")
        elif stage == 17:
            handle_empty_stage(client, message, "Team")
        elif stage == 18:
            handle_final_result(client, message)

    else:
        if user_id not in user_data:
            user_data[user_id] = {
                "stage": STAGE_TEAM,
                "photo_saving_active": False,
            }

        stage = user_data[user_id]["stage"]

        if message.text == "/selanjutnya":
            if stage < 10:  # Include the final result stage
                user_data[user_id]["stage"] += 1
                user_data[user_id]["photo_saving_active"] = False

        elif message.text == "/sebelumnya":
            if stage > STAGE_TEAM:
                user_data[user_id]["stage"] -= 1

        elif message.text == "/bersihkan":
            clear_current_stage_photos(user_id, stage)

        elif message.text == "/restart":
            # Reset to initial stage and clear any stage-specific data
            user_data[user_id]["stage"] = STAGE_TEAM
            user_data[user_id]["team"] = None  # Clear previously selected team
            # Clean up the directory after sending the image
            user_directory = os.path.join(BASE_TEMP_DIR, str(user_id))
            clear_download_directory(user_directory)
            client.send_message(
                chat_id=user_id,
                text="Proses telah dimulai dari awal.",
                reply_markup=get_navigation_buttons(STAGE_TEAM, user_id, message),
            )

        elif message.text == "/bantuan":
            handle_help(bot, message)

        elif message.text == "/iya":
            handle_submit_stage(client, message)

        elif message.text == "/tidak":
            handle_submit_stage(client, message)

        elif message.text == "/display":
            if saved_user_id == True:
                send_all_images(client, message.chat.id, ADMIN_IMG_DIR)

        elif message.text == "/requestadminauthorization":
            handle_save_user_id(client, message)

        stage = user_data[user_id]["stage"]

        if stage == STAGE_TEAM:
            handle_stage_team(client, message, stage)
        elif stage == STAGE_BEFORE:
            handle_stage_before(client, message)
        elif stage == STAGE_PROGRESS:
            handle_stage_progress(client, message)
        elif stage == STAGE_AFTER:
            handle_stage_after(client, message)
        elif stage == STAGE_REVIEW:
            handle_stage_review(client, message)
        elif stage == KEGIATAN:
            handle_empty_stage(client, message, "Kegiatan")
        elif stage == LOKASI:
            handle_empty_stage(client, message, "Lokasi")
        elif stage == TANGGAL:
            handle_empty_stage(client, message, "Tanggal")
        elif stage == TEAM:
            handle_empty_stage(client, message, "Team")
        elif stage == 9:
            handle_final_result(client, message)

@bot.on_message(filters.command("input") & filters.private)
def handle_input_tanggal(client, message):
    user_id = message.from_user.id

    # Periksa format perintah
    if len(message.command) > 1 and message.command[1].lower() == "tanggal":
        client.send_message(
            message.chat.id,
            "Masukkan tanggal kegiatan dengan format DD-MM-YYYY:"
        )
        user_dates[user_id] = None  # Tandai bahwa pengguna sedang memasukkan tanggal
    else:
        client.send_message(
            message.chat.id,
            "Gunakan perintah yang benar: `/input tanggal`."
        )

@bot.on_message(filters.text & filters.private)
def handle_tanggal_input(client, message):
    user_id = message.from_user.id

    # Periksa apakah pengguna sedang memasukkan tanggal
    if user_id in user_dates and user_dates[user_id] is None:
        try:
            # Validasi format tanggal
            tanggal = datetime.strptime(message.text, "%d-%m-%Y")
            formatted_tanggal = tanggal.strftime("%d-%m-%Y")
            user_dates[user_id] = formatted_tanggal  # Simpan tanggal yang diformat
            client.send_message(
                message.chat.id,
                f"Tanggal kegiatan {formatted_tanggal} telah disimpan!"
            )
        except ValueError:
            client.send_message(
                message.chat.id,
                "Format tanggal salah. Harap masukkan dengan format DD-MM-YYYY."
            )

@bot.on_message(filters.command("bantuan") & filters.private)
def handle_help(client, message):
    client.send_message(
        message.chat.id,
        "Langkah-langkah:\n"
        "1. Gunakan `/input tanggal` untuk memasukkan tanggal kegiatan manual.\n"
        "2. Masukkan tanggal dalam format DD-MM-YYYY.\n"
        "3. Jika tidak diinput, sistem akan menggunakan tanggal saat ini.\n"
        "4. Proses laporan seperti biasa.\n"
    )

def clear_current_stage_photos(user_id, stage):
    stage_map = {
        STAGE_BEFORE: "before",
        STAGE_PROGRESS: "progress",
        STAGE_AFTER: "after",
    }
    stage_name = stage_map.get(stage)
    if stage_name:
        user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), stage_name)
        if os.path.exists(user_dir):
            for filename in os.listdir(user_dir):
                file_path = os.path.join(user_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)


def handle_stage_before(client, message):
    handle_photo_stage(client, message, "before", STAGE_BEFORE, 4)


def handle_stage_progress(client, message):
    handle_photo_stage(client, message, "progress", STAGE_PROGRESS, 4)


def handle_stage_after(client, message):
    handle_photo_stage(client, message, "after", STAGE_AFTER, 4)


def handle_photo_stage(client, message, stage_name, stage, max_photos=None):
    user_id = message.from_user.id
    user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), stage_name)

    user_data[user_id]["download_dir"] = user_dir
    user_data[user_id]["photo_saving_active"] = True

    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    prompt_message = f"Stage {stage}: {stage_name.capitalize()} - Unggah foto kegiatan."
    # if stage_name > str(10) :
    # else:
    #     prompt_message = f"Stage {stage}: - Unggah foto kegiatan."

    if max_photos:
        prompt_message += f" Anda bisa mengunggah maksimal {max_photos} foto."
    prompt_message += " Tekan '/selanjutnya' untuk langkah berikutnya."

    client.send_message(
        message.chat.id,
        prompt_message,
        reply_markup=get_navigation_buttons(stage, user_id, message),
    )


def handle_stage_review(client, message):
    user_id = message.from_user.id
    user_team = load_text_from_file("role.txt", str(user_id), str("role"))
    user_team_verification = load_user_id(user_team, "userteam.txt")

    # Kirim pesan "Stage 4: Review" terlebih dahulu
    client.send_message(
        message.chat.id,
        "Stage 4: Review",
        reply_markup=get_navigation_buttons(STAGE_REVIEW, user_id, message),
    )

    # Directory for collages and review
    collage_review_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "collage_review")

    # Buat direktori jika belum ada
    if not os.path.exists(collage_review_dir):
        os.makedirs(collage_review_dir)

    # Directories for each stage
    before_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "before")
    progress_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "progress")
    after_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "after")

    split_progress_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "1")
    split_after_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "2")

    if user_team_verification == True:
        # Paths to save the collages
        collage_paths = {
            "progress": create_collage_for_stage(
                split_progress_dir, "progress", user_id
            ),
            "after": create_collage_for_stage(split_after_dir, "after", user_id),
        }

        # Load the template image
        template_image = Image.open(SPLIT_TEMPLATE_PATH)

        # Paste collages onto the template
        positions = {
            "progress": (204, 173),
            "after": (687, 173),
        }
    else:
        collage_paths = {
            "before": create_collage_for_stage(before_dir, "before", user_id),
            "progress": create_collage_for_stage(progress_dir, "progress", user_id),
            "after": create_collage_for_stage(after_dir, "after", user_id),
        }

        # Load the template image
        template_image = Image.open(TEMPLATE_PATH)

        # Paste collages onto the template
        positions = {
            "before": (28, 173),
            "progress": (445, 173),
            "after": (861, 173),
        }

    for stage, collage_path in collage_paths.items():
        if collage_path:
            collage_image = Image.open(collage_path)
            template_image.paste(collage_image, positions[stage])

    # Save the final review image in the collage_review directory
    review_image_path = os.path.join(collage_review_dir, "review_image.jpg")
    template_image.save(review_image_path)

    # Send the review image to the user
    client.send_photo(message.chat.id, photo=review_image_path)


def create_collage_for_stage(folder_path, stage_name, user_id):
    collage_width = 400  # Set desired collage width
    image_files = [
        f for f in os.listdir(folder_path) if f.lower().endswith(("png", "jpg", "jpeg"))
    ]

    if not image_files:
        return None

    images = []
    for image_file in image_files[-4:]:  # Use the latest 4 images
        img_path = os.path.join(folder_path, image_file)
        img = Image.open(img_path)
        images.append(img)

    collage = create_collage(images, collage_width)

    # Resize the collage to 390x390
    collage = collage.resize((390, 390), Image.LANCZOS)

    # Paste the corresponding padding image on top of the collage
    padding_image = get_padding_image(len(images))
    if padding_image:
        collage.paste(padding_image, (0, 0), padding_image)

    # Save the collage
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
        return Image.open(padding_image_path).convert(
            "RGBA"
        )  # Ensure it has alpha channel for transparency
    return None


def create_collage(images, collage_width):
    num_images = len(images)

    # Tentukan ukuran gambar sesuai dengan jumlah gambar
    if num_images == 1:
        square_size = collage_width
        collage_height = square_size
    elif num_images == 2:
        rect_width = collage_width // 2
        collage_height = rect_width * 2  # Tinggi untuk rasio 1:2
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
        collage_image.paste(img, (0, 0))  # Menghapus padding

    elif num_images == 2:
        for i in range(2):
            img = images[i]
            img = crop_to_aspect(
                img, collage_width // 2, collage_height
            )  # Crop gambar dengan rasio 1:2
            img = img.resize((collage_width // 2, collage_height), Image.LANCZOS)
            collage_image.paste(img, (i * (collage_width // 2), 0))  # Menghapus padding

    elif num_images == 3:
        img = images[0]
        img = crop_to_aspect(
            img, collage_width // 2, collage_width
        )  # Gambar pertama di-crop dengan rasio 1:2
        img = img.resize((collage_width // 2, collage_width), Image.LANCZOS)
        collage_image.paste(img, (0, 0))  # Menghapus padding

        for i in range(1, 3):
            img = images[i]
            img = crop_to_aspect(img, collage_width // 2, collage_width // 2)
            img = img.resize((collage_width // 2, collage_width // 2), Image.LANCZOS)
            collage_image.paste(
                img, (collage_width // 2, (i - 1) * (collage_width // 2))
            )  # Menghapus padding

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


def crop_longest_side(image, target_size):
    width, height = image.size
    new_size = min(width, height)
    left = (width - new_size) // 2
    top = (height - new_size) // 2
    right = (width + new_size) // 2
    bottom = (height + new_size) // 2
    return image.crop((left, top, right, bottom)).resize(
        (target_size, target_size), Image.LANCZOS
    )


@bot.on_message(filters.photo & filters.private)
def save_photo(client, message):
    user_id = message.from_user.id

    if user_id not in user_data or not user_data[user_id].get(
        "photo_saving_active", False
    ):
        return

    user_dir = user_data[user_id]["download_dir"]

    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    current_photo_count = len(
        [
            name
            for name in os.listdir(user_dir)
            if os.path.isfile(os.path.join(user_dir, name))
        ]
    )

    remaining_slots = 4 - current_photo_count

    if remaining_slots <= 0:
        client.send_message(message.chat.id, "You cannot upload more than 4 photos.")
        return

    file_path = client.download_media(
        message.photo.file_id,
        file_name=os.path.join(user_dir, f"{message.photo.file_id}.jpg"),
    )

    current_photo_count = len(
        [
            name
            for name in os.listdir(user_dir)
            if os.path.isfile(os.path.join(user_dir, name))
        ]
    )

    client.send_message(message.chat.id, f"Photo saved successfully.")


def handle_empty_stage(client, message, stage_name):
    user_id = message.from_user.id
    user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), stage_name)

    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    text_filename = os.path.join(user_dir, f"{stage_name}.txt")

    if message.text == "/bersihkan":
        # Hapus isi file .txt
        with open(text_filename, "w", encoding="utf-8") as text_file:
            text_file.write("")  # Kosongkan file
        client.send_message(message.chat.id, f"Teks telah dibersihkan dari {stage_name}.")

    elif message.text in ["/selanjutnya", "/sebelumnya"]:
        # Menyimpan file .txt meskipun kosong
        with open(text_filename, "a", encoding="utf-8") as text_file:
            text_file.write("")  # Pastikan file ada meskipun kosong
        
        if stage_name == "Tanggal":
            client.send_message(message.chat.id, f"Masukkan tanggal secara manual (format: DD-MM-YYYY) atau gunakan tanggal /saat_ini")
        else:
            client.send_message(message.chat.id, f"Masukkan {stage_name} secara manual atau gunakan perintah.")

    elif message.text == "/saat_ini" and stage_name == "Tanggal":
        current_date = datetime.now().strftime("%d-%m-%Y")
        with open(text_filename, "w", encoding="utf-8") as text_file:
            text_file.write(current_date)  # Menyimpan tanggal saat ini ke file .txt
        client.send_message(
            message.chat.id,
            f"Tanggal saat ini {current_date} telah disimpan!\n/selanjutnya untuk melanjutkan."
        )

    else:
        # Jika pengguna memasukkan tanggal secara manual
        if stage_name == "Tanggal":
            try:
                # Validasi apakah format tanggal benar (DD-MM-YYYY)
                datetime.strptime(message.text, "%d-%m-%Y")
                with open(text_filename, "w", encoding="utf-8") as text_file:
                    text_file.write(message.text)  # Simpan tanggal manual ke file
                client.send_message(
                    message.chat.id,
                    f"Tanggal {message.text} telah disimpan! /selanjutnya untuk melanjutkan."
                )
            except ValueError:
                client.send_message(message.chat.id, "Format tanggal salah, masukkan dalam format DD-MM-YYYY.")
        else:
            # Simpan input manual lainnya
            with open(text_filename, "w", encoding="utf-8") as text_file:
                text_file.write(message.text + "\n")  # Simpan teks ke file
            client.send_message(message.chat.id, f"{stage_name} telah disimpan! /selanjutnya untuk melanjutkan.")

def handle_submit_stage(client, message):
    user_id = message.from_user.id
    user_directory = os.path.join(BASE_TEMP_DIR, str(user_id))
    review_image_path = os.path.join(
        BASE_TEMP_DIR, str(user_id), "collage_review", "final_result.jpg"
    )

    image = Image.open(review_image_path)

    if message.text == "/tidak":
        # Clean up the directory after sending the image
        savetopreventbug(image, user_id)
        client.send_message(message.chat.id, "Laporan dihapus")
        clear_download_directory(user_directory)

    elif message.text == "/iya":
        # Save the final image to the admin directory with a sequential file name
        save_image_admin(image, user_id)
        client.send_message(message.chat.id, "Laporan berhasil disubmit")
        clear_download_directory(user_directory)

    else:
        # Menyimpan teks yang diterima
        client.send_message(
            # message.chat.id, f"{stage_name} telah disimpan!. /next untuk melanjutkan"
        )


def handle_final_result(client, message):
    user_id = message.from_user.id
    review_image_path = os.path.join(
        BASE_TEMP_DIR, str(user_id), "collage_review", "review_image.jpg"
    )

    if not os.path.exists(review_image_path):
        client.send_message(
            message.chat.id, "proses telah selesai /restart untuk mengulang"
        )
        return

    # Load the review image
    image = Image.open(review_image_path)
    draw = ImageDraw.Draw(image)

    # Load bold font
    font_path = "arialbd.ttf"  # Update this path to the location of your bold font file
    font_size = 16
    font = ImageFont.truetype(font_path, font_size)

    # Define the text to be placed
    labels = ["• KEGIATAN :", "• LOKASI :", "• TANGGAL :", "• TEAM :"]
    text_items = ["kegiatan", "lokasi", "tanggal", "team"]
    y_coordinates = [625, 649, 671, 694]

    for label, text_item, y in zip(labels, text_items, y_coordinates):
        # Load the text from the corresponding .txt file
        text_path = os.path.join(
            BASE_TEMP_DIR, str(user_id), text_item, f"{text_item}.txt"
        )
        if os.path.exists(text_path):
            with open(text_path, "r", encoding="utf-8") as file:
                content = file.read().strip()

            # Combine the label with the actual content
            combined_text = f"{label} {content}"

            # Calculate the text bounding box to center it horizontally
            text_bbox = draw.textbbox((0, 0), combined_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            x_coordinate = (image.width - text_width) // 2

            # Draw the text on the image
            draw.text((x_coordinate, y), combined_text, fill="black", font=font)

    # Save the final image
    final_image_path = os.path.join(
        BASE_TEMP_DIR, str(user_id), "collage_review", "final_result.jpg"
    )

    image.save(final_image_path)
    client.send_photo(message.chat.id, photo=final_image_path)

    client.send_message(message.chat.id, "Submit ke admin?\n /iya         /tidak")


def handle_stage_team(client, message, stage):
    user_id = message.from_user.id
    user_dir = os.path.join(BASE_TEMP_DIR, str(user_id), "role")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    if stage == STAGE_TEAM:
        if message.text in ["/MAINTENANCE", "/PATROLI"]:
            user_data[user_id]["role"] = message.text  # Save selected team
            # user_data[user_id]["stage"] = STAGE_BEFORE  # Move to STAGE_BEFORE
            text_filename = os.path.join(user_dir, "role.txt")
            teaminput = message.text.strip("/")
            with open(text_filename, "w", encoding="utf-8") as text_file:
                text_file.write(teaminput + "\n")  # Simpan teks ke file
            client.send_message(
                chat_id=user_id,
                text=f"Kegiatan {teaminput} telah dipilih. /selanjutnya untuk melanjutkan ke tahap berikutnya.",
                # reply_markup=get_navigation_buttons(STAGE_BEFORE, user_id, message),
            )
        else:
            client.send_message(
                chat_id=user_id,
                text="Silakan pilih jenis kegiatan:\n/MAINTENANCE\n/PATROLI",
                reply_markup=get_navigation_buttons(STAGE_TEAM, user_id, message),
            )


def save_image_admin(image, user_id):
    admin_dir = os.path.join(ADMIN_IMG_DIR)
    os.makedirs(admin_dir, exist_ok=True)

    # Gunakan tanggal manual jika tersedia
    if user_id in user_dates and user_dates[user_id]:
        formatted_date = user_dates[user_id].replace("-", "")  # Format: DDMMYYYY
    else:
        current_time = datetime.now()
        formatted_date = current_time.strftime("%d%m%Y")  # Format: DDMMYYYY

    current_time = datetime.now()
    formatted_time = current_time.strftime("%H%M%S")  # Format waktu

    # Simpan gambar dengan nama file sesuai tanggal dan waktu
    file_name = f"final_result_{formatted_date}-{formatted_time}.jpg"
    file_path = os.path.join(admin_dir, file_name)

    image.save(file_path)

def savetopreventbug(image, user_id):
    admin_dir = os.path.join(BASE_TEMP_DIR, str(user_id))
    os.makedirs(admin_dir, exist_ok=True)

    # Dapatkan daftar semua file di direktori admin
    existing_files = len(
        [name for name in os.listdir(admin_dir) if name.endswith(".jpg")]
    )

    # Simpan foto dengan nama berurutan
    file_name = f"final_result_{existing_files + 1}.jpg"
    file_path = os.path.join(admin_dir, file_name)

    # Simpan gambar ke file
    image.save(file_path)


def clear_download_directory(directory):
    try:
        # Hapus seluruh folder beserta isinya
        shutil.rmtree(directory)
        print(f"Deleted directory {directory}")
    except Exception as e:
        print(f"Error cleaning download directory: {str(e)}")


def send_all_images(client, chat_id, folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        client.send_message(chat_id, "Folder tidak ditemukan.")
        return

    # List all files in the folder
    files = os.listdir(folder_path)

    # Filter out only image files
    image_files = [
        file
        for file in files
        if file.endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))
    ]

    if not image_files:
        client.send_message(chat_id, "Tidak ada gambar di folder ini.")
        return

    # Send each image file to the chat
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        client.send_photo(chat_id, photo=image_path)

    client.send_message(chat_id, "Semua gambar telah dikirim.")


def save_user_id(user_id):
    # Tentukan path untuk file .txt
    file_path = os.path.join(ADMIN_DIR, "userdata.txt")

    # Baca semua user ID yang sudah ada
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            saved_user_ids = file.read().splitlines()
    else:
        saved_user_ids = []

    # Cek apakah user_id sudah ada, jika belum, tambahkan
    if str(user_id) not in saved_user_ids:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(str(user_id) + "\n")
        print(f"User ID {user_id} telah disimpan di {file_path}")
    else:
        print(f"User ID {user_id} sudah ada di {file_path}")


@bot.on_message(filters.text & filters.private)
def handle_save_user_id(client, message):
    user_id = message.from_user.id  # Dapatkan user_id

    # Panggil fungsi untuk menyimpan user_id
    save_user_id(user_id)

    # Kirim konfirmasi ke pengguna
    client.send_message(
        chat_id=message.chat.id, text=f"User ID Anda ({user_id}) telah disimpan."
    )


def load_user_id(user_id, data):
    file_path = os.path.join(ADMIN_DIR, data)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            saved_user_id = file.read().splitlines()
            if str(user_id) in saved_user_id:
                return True  # Jika user_id ditemukan
            else:
                return False  # Jika user_id tidak ditemukan
    else:
        return None


def load_text_from_file(data, user_id, team):
    file_path = os.path.join(BASE_TEMP_DIR, user_id, team, data)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = (
                file.read().strip()
            )  # Membaca seluruh isi file dan menghilangkan spasi/enter di awal/akhir
            return content  # Mengembalikan isi file sebagai string
    else:
        return None  # Jika file tidak ditemukan


print("Connected.")
bot.run()