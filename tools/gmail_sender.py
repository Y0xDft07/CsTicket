#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📧 gmail_sender.py — Python 3.13.9
-----------------------------------
Modul ini menangani proses pengiriman email otomatis
melalui SMTP Gmail menggunakan kredensial dari file .env.
"""

# ==============================================================
# 📦 1. Import Modul
# ==============================================================
from __future__ import annotations
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv


# ==============================================================
# ⚙️ 2. Inisialisasi & Validasi Variabel Lingkungan
# ==============================================================
# Pastikan terminal dapat menampilkan karakter Unicode
sys.stdout.reconfigure(encoding="utf-8")

# Tentukan lokasi file .env secara dinamis
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

if not ENV_PATH.exists():
    sys.exit("🚫 File .env tidak ditemukan. Harap pastikan file .env ada di direktori utama proyek.")

# Muat variabel dari file .env
load_dotenv(dotenv_path=ENV_PATH)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

# Validasi kredensial email
if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
    sys.exit("❌ EMAIL_ADDRESS atau EMAIL_APP_PASSWORD tidak ditemukan di file .env!")

print("🔐 Kredensial Gmail berhasil dimuat.")
print(f"📧 Akun: {EMAIL_ADDRESS}")
print(f"🔑 Panjang App Password: {len(EMAIL_APP_PASSWORD)} karakter")


# ==============================================================
# ✉️ 3. Fungsi Utama: Kirim Email SMTP
# ==============================================================
def send_email_smtp(to: str, subject: str, body: str) -> dict[str, str]:
    """
    Mengirim email teks sederhana melalui server SMTP Gmail.

    Args:
        to (str): Alamat email penerima.
        subject (str): Judul email.
        body (str): Isi pesan dalam format teks biasa.

    Returns:
        dict[str, str]: Status dan pesan hasil pengiriman.
    """
    try:
        # ------------------------------------------------------
        # 🧩 Membangun struktur email MultiPart
        # ------------------------------------------------------
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # ------------------------------------------------------
        # 📡 Membuka koneksi ke server SMTP Gmail
        # ------------------------------------------------------
        print(f"\n📨 Menghubungkan ke smtp.gmail.com untuk mengirim email ke {to} ...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.set_debuglevel(0)  # Ganti ke 1 jika ingin log SMTP detail

            # 🔒 Mulai koneksi TLS (aman) dan login
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)

            # 📤 Kirim email
            server.send_message(msg)

        # ------------------------------------------------------
        # ✅ Jika berhasil
        # ------------------------------------------------------
        print(f"✅ Email berhasil dikirim ke {to}")
        return {"status": "success", "message": f"Email berhasil dikirim ke {to}"}

    except smtplib.SMTPAuthenticationError:
        print("❌ Autentikasi SMTP gagal. Periksa App Password Gmail Anda.")
        return {"status": "error", "message": "Autentikasi gagal. Cek App Password Gmail."}

    except smtplib.SMTPConnectError:
        print("❌ Gagal terhubung ke server Gmail SMTP.")
        return {"status": "error", "message": "Tidak dapat terhubung ke server SMTP Gmail."}

    except smtplib.SMTPException as e:
        print(f"⚠️ Kesalahan SMTP umum: {e}")
        return {"status": "error", "message": f"Kesalahan SMTP: {e}"}

    except Exception as e:
        print(f"⚠️ Kesalahan tidak terduga saat mengirim email: {e}")
        return {"status": "error", "message": f"Gagal mengirim email: {e}"}


# ==============================================================
# 🧪 4. Mode Uji Mandiri (Opsional)
# ==============================================================
if __name__ == "__main__":
    print("🧪 Mode Uji Kirim Email".center(60, "-"))
    recipient = input("Masukkan alamat email penerima: ").strip()
    subject = input("Judul email: ").strip()
    message = input("Isi pesan: ").strip()

    result = send_email_smtp(recipient, subject, message)
    print("\n📊 Hasil Pengiriman:", result)
