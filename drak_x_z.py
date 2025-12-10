import os, json, time, random, threading, datetime, sys, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pywhatkit as kit

# ================== KONFIG ==================
BOT_NAME = "DRAK X Z"
DATA_FILE = "users.json"
TOKEN_FILE = "token.txt"
ADMIN_ID = 6712825044
STEALTH_MODE = False

# ================== TOKEN AUTO ==================
def load_token():
    """Muat token bot dari file token.txt"""
    if not os.path.exists(TOKEN_FILE):
        print(f"⚠️  File {TOKEN_FILE} tidak ditemukan!")
        print("📝 Membuat file token.txt baru...")
        
        token = input("🔑 Masukkan Token Bot Telegram Anda: ").strip()
        
        # Validasi token
        if not token or len(token) < 30:
            print("❌ Token tidak valid! Token harus memiliki minimal 30 karakter.")
            token = "ISI_TOKEN_BOT_KAMU_DI_SINI"
        
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        
        print(f"✅ Token disimpan di {TOKEN_FILE}")
        return token
    else:
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
        
        # Cek apakah token default masih ada
        if token == "ISI_TOKEN_BOT_KAMU_DI_SINI" or len(token) < 30:
            print("⚠️  Token belum diatur atau tidak valid!")
            print("Silakan edit file token.txt dan masukkan token bot Telegram Anda.")
            print("Atau tekan Enter untuk menggunakan token default (tidak berfungsi)...")
            input("Tekan Enter untuk melanjutkan...")
        
        return token

# Load token saat startup
TOKEN = load_token()

# ================== USERS ==================
def load_users():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================== UTIL ==================
def now_date():
    return datetime.datetime.now()

def calc_expired(days):
    return (now_date() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

def is_expired(exp):
    return now_date().strftime("%Y-%m-%d") > exp

def log_activity(text):
    with open("activity.log", "a") as f:
        f.write(f"[{now_date()}] {text}\n")

def auto_backup():
    if not os.path.exists("backup"):
        os.mkdir("backup")
    name = f"backup/users_{now_date().strftime('%Y%m%d_%H%M%S')}.json"
    with open(DATA_FILE) as a, open(name, "w") as b:
        b.write(a.read())
    print(f"✅ Backup dibuat: {name}")

def reset_sessions():
    users = load_users()
    today = now_date().strftime("%Y-%m-%d")
    for u in users:
        users[u]["today_sent"] = 0
        users[u]["last_date"] = today
        if "expired" in users[u] and is_expired(users[u]["expired"]):
            users[u]["blocked"] = True
        else:
            users[u]["blocked"] = False
    save_users(users)
    print("✅ Reset sesi harian selesai")

# ================== TELEGRAM SPM ==================
def send_telegram_message(token, chat_id, message):
    """Mengirim pesan ke Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "✅ Pesan terkirim"
        else:
            return False, f"❌ Gagal: {response.json().get('description', 'Unknown error')}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def telegram_spam():
    """Menu untuk mengirim pesan spam Telegram"""
    os.system("clear")
    print("""
    ╔══════════════════════════════════════════╗
    ║         🚀 SPM TELEGRAM MESSENGER       ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Input data
    target_name = input("📛 Nama Target: ").strip()
    
    try:
        jumlah = int(input("🔢 Jumlah Pesan: ").strip())
    except:
        print("❌ Jumlah harus angka!")
        input("Tekan Enter untuk kembali...")
        return
    
    if jumlah <= 0:
        print("❌ Jumlah harus lebih dari 0!")
        input("Tekan Enter untuk kembali...")
        return
    
    message = input("💬 Pesan yang dikirim: ").strip()
    
    # Cek token bot
    print("\n🔑 Token Bot:")
    print("1. Gunakan token dari file token.txt")
    print("2. Masukkan token manual")
    token_choice = input("Pilihan (1/2): ").strip()
    
    if token_choice == "2":
        bot_token = input("Masukkan Token Bot: ").strip()
        if not bot_token or len(bot_token) < 30:
            print("❌ Token tidak valid!")
            input("Tekan Enter untuk kembali...")
            return
    else:
        bot_token = TOKEN
        if bot_token == "ISI_TOKEN_BOT_KAMU_DI_SINI" or len(bot_token) < 30:
            print("❌ Token di token.txt tidak valid!")
            print("Silakan edit file token.txt terlebih dahulu")
            input("Tekan Enter untuk kembali...")
            return
    
    # Input user ID
    user_id = input("👤 ID User Telegram: ").strip()
    
    # Konfirmasi
    print("\n" + "="*50)
    print(f"📛 Target: {target_name}")
    print(f"🔢 Jumlah: {jumlah} pesan")
    print(f"💬 Pesan: {message[:50]}..." if len(message) > 50 else f"💬 Pesan: {message}")
    print(f"👤 ID: {user_id}")
    print("="*50)
    
    confirm = input("\n🚀 Lanjutkan spam? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Dibatalkan!")
        input("Tekan Enter untuk kembali...")
        return
    
    # Proses spam
    print("\n" + "═"*50)
    print("🚀 MULAI MENGIRIM PESAN...")
    print("═"*50)
    
    success_count = 0
    failed_count = 0
    delay = 1  # Delay antara pesan (detik)
    
    for i in range(1, jumlah + 1):
        print(f"\r📤 Mengirim pesan {i}/{jumlah}...", end="")
        success, result = send_telegram_message(bot_token, user_id, message)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
            print(f"\n⚠️  Pesan {i} gagal: {result}")
        
        # Delay untuk menghindari rate limit
        if i < jumlah:
            time.sleep(delay)
    
    print("\n" + "═"*50)
    print("📊 HASIL SPAM TELEGRAM:")
    print(f"✅ Berhasil: {success_count} pesan")
    print(f"❌ Gagal: {failed_count} pesan")
    print(f"📊 Total: {jumlah} pesan")
    print("═"*50)
    
    # Log aktivitas
    log_activity(f"SPM TELEGRAM: {target_name} - {jumlah} pesan ke {user_id}")
    
    input("\n🏁 Selesai! Tekan Enter untuk kembali...")

# ================== WHATSAPP SPM ==================
def whatsapp_spam_pywhatkit(phone_number, message, jumlah):
    """Mengirim spam WhatsApp menggunakan pywhatkit"""
    try:
        # Format nomor telepon (harus dengan kode negara)
        if not phone_number.startswith("+"):
            phone_number = "+62" + phone_number.lstrip("0")
        
        success_count = 0
        failed_count = 0
        
        for i in range(jumlah):
            try:
                # Kirim pesan dengan delay 15 detik antar pesan
                kit.sendwhatmsg_instantly(
                    phone_no=phone_number,
                    message=message,
                    wait_time=15,
                    tab_close=True
                )
                success_count += 1
                print(f"\r📱 WhatsApp: Pesan {i+1}/{jumlah} terkirim", end="")
                time.sleep(2)  # Delay tambahan
            except Exception as e:
                failed_count += 1
                print(f"\n⚠️  Pesan {i+1} gagal: {str(e)}")
        
        return success_count, failed_count
        
    except Exception as e:
        return 0, jumlah, f"Error: {str(e)}"

def whatsapp_spam_selenium(phone_number, message, jumlah):
    """Mengirim spam WhatsApp menggunakan Selenium (lebih stabil)"""
    print("\n🚀 Menggunakan metode Selenium...")
    print("⚠️  Pastikan WhatsApp Web sudah login di browser!")
    
    driver = None
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=./chrome_profile")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")
        
        # Tunggu hingga WhatsApp Web siap
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]')))
        
        success_count = 0
        failed_count = 0
        
        for i in range(jumlah):
            try:
                # Temukan input box
                input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
                
                # Clear dan ketik pesan
                input_box.clear()
                input_box.send_keys(message)
                input_box.send_keys(Keys.ENTER)
                
                success_count += 1
                print(f"\r📱 WhatsApp: Pesan {i+1}/{jumlah} terkirim", end="")
                
                # Delay antara pesan
                time.sleep(1.5)
                
            except Exception as e:
                failed_count += 1
                print(f"\n⚠️  Pesan {i+1} gagal: {str(e)}")
                # Coba reload halaman
                driver.refresh()
                time.sleep(3)
        
        driver.quit()
        return success_count, failed_count
        
    except Exception as e:
        if driver:
            driver.quit()
        return 0, jumlah

def whatsapp_spam():
    """Menu untuk mengirim pesan spam WhatsApp"""
    os.system("clear")
    print("""
    ╔══════════════════════════════════════════╗
    ║         📱 SPM WHATSAPP MESSENGER       ║
    ╚══════════════════════════════════════════╝
    """)
    
    print("📋 Pilih metode:")
    print("1. PyWhatKit (Simple, but needs internet)")
    print("2. Selenium (Powerful, needs Chrome)")
    
    method_choice = input("Pilihan (1/2): ").strip()
    
    if method_choice not in ['1', '2']:
        print("❌ Pilihan tidak valid!")
        input("Tekan Enter untuk kembali...")
        return
    
    # Input data
    target_name = input("\n📛 Nama Target: ").strip()
    phone_number = input("📞 Nomor WhatsApp (contoh: 8123456789): ").strip()
    
    try:
        jumlah = int(input("🔢 Jumlah Pesan: ").strip())
    except:
        print("❌ Jumlah harus angka!")
        input("Tekan Enter untuk kembali...")
        return
    
    if jumlah <= 0 or jumlah > 100:
        print("❌ Jumlah harus antara 1-100!")
        input("Tekan Enter untuk kembali...")
        return
    
    message = input("💬 Pesan yang dikirim: ").strip()
    
    # Konfirmasi
    print("\n" + "="*50)
    print(f"📛 Target: {target_name}")
    print(f"📞 Nomor: {phone_number}")
    print(f"🔢 Jumlah: {jumlah} pesan")
    print(f"💬 Pesan: {message[:50]}..." if len(message) > 50 else f"💬 Pesan: {message}")
    print(f"🛠️  Metode: {'PyWhatKit' if method_choice == '1' else 'Selenium'}")
    print("="*50)
    
    print("\n⚠️  PERINGATAN:")
    print("• Jangan gunakan untuk spam berlebihan")
    print("• Anda bertanggung jawab atas penggunaan tool ini")
    print("• WhatsApp mungkin memblokir akun jika spam berlebihan")
    
    confirm = input("\n🚀 Lanjutkan spam WhatsApp? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Dibatalkan!")
        input("Tekan Enter untuk kembali...")
        return
    
    # Proses spam
    print("\n" + "═"*50)
    print("🚀 MULAI MENGIRIM PESAN WHATSAPP...")
    print("═"*50)
    
    start_time = time.time()
    
    if method_choice == '1':
        # PyWhatKit method
        print("\n📡 Menggunakan PyWhatKit...")
        print("⚠️  Pastikan terkoneksi internet dan WhatsApp Web terbuka!")
        success_count, failed_count = whatsapp_spam_pywhatkit(phone_number, message, jumlah)
    else:
        # Selenium method
        print("\n🌐 Menggunakan Selenium...")
        print("⚠️  Chrome akan terbuka, pastikan login WhatsApp Web!")
        time.sleep(2)
        success_count, failed_count = whatsapp_spam_selenium(phone_number, message, jumlah)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "═"*50)
    print("📊 HASIL SPAM WHATSAPP:")
    print(f"✅ Berhasil: {success_count} pesan")
    print(f"❌ Gagal: {failed_count} pesan")
    print(f"📊 Total: {jumlah} pesan")
    print(f"⏱️  Durasi: {duration:.2f} detik")
    print(f"⚡ Kecepatan: {success_count/duration:.2f} pesan/detik" if duration > 0 else "")
    print("═"*50)
    
    # Log aktivitas
    log_activity(f"SPM WHATSAPP: {target_name} - {jumlah} pesan ke {phone_number}")
    
    input("\n🏁 Selesai! Tekan Enter untuk kembali...")

# ================== LOADING + HACK EFFECT ==================
def startup_loading():
    if STEALTH_MODE:
        os.system("clear")
        return
    print("Loading...")
    for i in range(1, 101):
        sys.stdout.write(f"\r{i}%")
        sys.stdout.flush()
        time.sleep(0.02)
    print("\nBot ingin metal? Y/N")
    input("> ")
    os.system("clear")

def hack_effect_green(duration=5):
    end = time.time() + duration
    while time.time() < end:
        line = "".join(random.choice("01 ") for _ in range(80))
        print("\033[92m" + line + "\033[0m")
        time.sleep(0.03)
    os.system("clear")

def hack_breach():
    for i in range(1, 101):
        bar = "█" * (i // 2)
        print(f"[BREACHING] {i}% {bar}", end="\r")
        time.sleep(0.02)
    os.system("clear")

def hack_target_scan():
    targets = [
        "Bypass firewall...",
        "Injecting payload...",
        "Root access granted...",
        "Dumping database..."
    ]
    for _ in range(15):
        print(random.choice(targets))
        time.sleep(0.2)
    os.system("clear")

# ================== DRAGON TOOLS MENU ==================
def dragon_menu():
    while True:
        os.system("clear")
        print("""██████╗ ██████╗  █████╗ ██╗  ██╗    ██╗  ██╗    ███████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ╚██╗██╔╝    ╚══███╔╝
██║  ██║██████╔╝███████║█████╔╝      ╚███╔╝       ███╔╝ 
██║  ██║██╔══██╗██╔══██╗██╔═██╗      ██╔██╗      ███╔╝  
██████╔╝██║  ██║██║  ██║██║  ██╗    ██╔╝ ██╗    ███████╗
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝    ╚══════╝

        🔥 D R A K  X  Z  -  D R A G O N  T O O L 🔥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] ➕ Add Reseller          [2] ❌ Delete Reseller
[3] ⏳ Extend Expired        [4] ⚙️  Change Limit
[5] 🔑 Update Token SPM      [6] 👁️  View All Users
[7] 📱 Spam Message (WHATSAPP) [8] 📨 Spam Message (TELEGRAM)
[9] 🔄 Update Bot Token     [10] 💾 Backup Data
[0] 🚪 Exit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

        ch = input("PILIH MENU >> ")
        users = load_users()

        if ch == "1":
            u = input("Username: ")
            p = input("Password: ")
            n = input("Nama: ")
            tid = input("Telegram ID: ")
            tkn = input("Token SPM: ")
            d = int(input("Hari aktif: "))
            l = int(input("Limit: "))

            users[u] = {
                "password": p,
                "role": "RESELLER",
                "nama": n,
                "telegram_id": tid,
                "token": tkn,
                "expired": calc_expired(d),
                "limit_perhari": l,
                "today_sent": 0,
                "blocked": False
            }

            save_users(users)
            log_activity(f"Tambah reseller {u}")
            input("✅ DONE...")

        elif ch == "2":
            u = input("Username: ")
            if u in users:
                del users[u]
                save_users(users)
                log_activity(f"Hapus reseller {u}")
                print("✅ DIHAPUS")
            else:
                print("❌ USER TIDAK ADA")
            input("ENTER...")

        elif ch == "3":
            u = input("Username: ")
            if u in users:
                d = int(input("Tambah hari: "))
                old = datetime.datetime.strptime(users[u]["expired"], "%Y-%m-%d")
                new = old + datetime.timedelta(days=d)
                users[u]["expired"] = new.strftime("%Y-%m-%d")
                users[u]["blocked"] = False
                save_users(users)
                print("✅ EXTEND BERHASIL")
            else:
                print("❌ USER TIDAK ADA")
            input("ENTER...")

        elif ch == "4":
            u = input("Username: ")
            if u in users:
                l = int(input("Limit baru: "))
                users[u]["limit_perhari"] = l
                save_users(users)
                print("✅ LIMIT DIUBAH")
            else:
                print("❌ USER TIDAK ADA")
            input("ENTER...")

        elif ch == "5":
            u = input("Username: ")
            if u in users:
                t = input("Token baru: ")
                users[u]["token"] = t
                save_users(users)
                print("✅ TOKEN DIUPDATE")
            else:
                print("❌ USER TIDAK ADA")
            input("ENTER...")

        elif ch == "6":
            print("\n" + "="*60)
            print(f"{'USERNAME':<15} {'EXPIRED':<12} {'LIMIT':<8} {'STATUS':<10}")
            print("="*60)
            for u in users:
                status = "✅ AKTIF" if not users[u].get("blocked", False) else "❌ BLOKIR"
                print(f"{u:<15} {users[u].get('expired','-'):<12} {users[u].get('limit_perhari',0):<8} {status:<10}")
            print("="*60)
            input("\nENTER untuk kembali...")

        elif ch == "7":
            whatsapp_spam()

        elif ch == "8":
            telegram_spam()

        elif ch == "9":
            print("\n🔄 UPDATE BOT TOKEN")
            print(f"Token saat ini: {TOKEN[:15]}...")
            new_token = input("Masukkan token baru: ").strip()
            
            if new_token and len(new_token) >= 30:
                with open(TOKEN_FILE, "w") as f:
                    f.write(new_token)
                print("✅ Token berhasil diupdate!")
                print("⚠️  Restart bot untuk menggunakan token baru")
            else:
                print("❌ Token tidak valid!")
            input("ENTER...")

        elif ch == "10":
            print("\n💾 BACKUP DATA")
            auto_backup()
            input("ENTER...")

        elif ch == "0":
            print("🚪 EXIT...")
            break

        else:
            print("❌ PILIHAN TIDAK VALID")
            time.sleep(1)

# ================== TELEGRAM BOT ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ DRAK X Z BOT ACTIVE")

async def mykey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()
    for u in users:
        if users[u].get("telegram_id") == uid:
            d = users[u]
            await update.message.reply_text(
                f"User: {u}\nExpired: {d['expired']}\nLimit: {d['limit_perhari']}"
            )
            return
    await update.message.reply_text("❌ Akun belum terdaftar.")

def run_telegram_bot():
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("mykey", mykey))
        print(f"🤖 Bot Telegram berjalan deng
