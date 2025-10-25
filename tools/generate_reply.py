#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💬 generate_reply.py — Python 3.13.9
------------------------------------
Modul ini menghasilkan balasan otomatis kepada pelanggan menggunakan model AI Groq (LLaMA 3).
Balasan dibuat dengan bahasa yang sopan, empatik, dan profesional.
"""

# ==============================================================
# 📦 1. Import Modul
# ==============================================================
from __future__ import annotations
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq


# ==============================================================
# ⚙️ 2. Inisialisasi Variabel Lingkungan (.env)
# ==============================================================
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

if not ENV_PATH.exists():
    sys.exit("🚫 File .env tidak ditemukan! Pastikan file .env berada di direktori utama proyek.")

load_dotenv(dotenv_path=ENV_PATH)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    sys.exit("🚫 GROQ_API_KEY tidak ditemukan di file .env — harap tambahkan kunci API Groq Anda!")

# Membuat instance client Groq
client = Groq(api_key=GROQ_API_KEY)


# ==============================================================
# 🤖 3. Fungsi Utama: Generate Reply
# ==============================================================
def generate_reply(name: str, text: str) -> str:
    """
    Menghasilkan balasan pelanggan yang sopan dan empatik menggunakan model AI.

    Args:
        name (str): Nama pelanggan.
        text (str): Isi pesan atau keluhan pelanggan.

    Returns:
        str: Balasan otomatis yang dihasilkan oleh model AI.
    """
    if not text.strip():
        return f"Halo {name},\n\nPesan Anda kosong atau tidak terbaca. Mohon kirim ulang pertanyaan Anda.\n\nHormat kami,\nTim Dukungan Pelanggan"

    # 🧠 Prompt untuk model AI
    prompt = f"""
Anda adalah agen dukungan pelanggan yang ramah dan profesional.

Balas keluhan atau pertanyaan berikut dengan empati, penjelasan yang jelas, 
dan saran yang membantu. Sertakan salam pembuka dengan nama pelanggan, 
dan akhiri dengan kalimat penutup sopan.

Format penutup pesan:
Hormat kami,
Tim Dukungan Pelanggan

Nama Pelanggan: {name}

Isi Pesan:
\"\"\"{text}\"\"\"

Kembalikan HANYA isi pesan balasan akhir.
"""

    try:
        # 🧩 Mengirim prompt ke model Groq
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,     # Kreativitas balasan
            max_tokens=500,      # Panjang maksimal jawaban
            top_p=1,             # Sampling parameter
            stream=True,         # Streaming agar output bertahap
        )
    except Exception as e:
        print(f"⚠️ Gagal menghubungi API Groq: {e}")
        return (
            f"Halo {name},\n\n"
            "Saat ini sistem kami mengalami gangguan. Silakan coba lagi beberapa saat.\n\n"
            "Hormat kami,\nTim Dukungan Pelanggan"
        )

    # ==========================================================
    # 📨 4. Menerima dan Menyusun Hasil Streaming Balasan
    # ==========================================================
    reply_text = ""

    try:
        # Looping hasil streaming dari API
        for chunk in completion:
            if hasattr(chunk, "choices") and chunk.choices:
                delta_content = getattr(chunk.choices[0].delta, "content", None)

                if delta_content:
                    print(delta_content, end="", flush=True)  # tampil real-time
                    reply_text += delta_content
            else:
                print("\n⚠️ Format data AI tidak sesuai atau kosong.", flush=True)
                break

    except Exception as e:
        print(f"\n⚠️ Terjadi kesalahan saat menerima respons AI: {e}", flush=True)

    print()  # baris kosong setelah streaming
    return reply_text.strip()


# ==============================================================
# 🧪 5. Mode Pengujian Manual (Opsional)
# ==============================================================
if __name__ == "__main__":
    print("🧪 Mode Uji Balasan AI".center(50, "-"))
    customer_name = input("Nama pelanggan: ").strip()
    message_text = input("Isi pesan pelanggan: ").strip()

    print("\n🎯 Hasil Balasan Otomatis:\n")
    result = generate_reply(customer_name, message_text)
    print("\n" + "-" * 50)
    print(result)
