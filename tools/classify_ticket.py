#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 classify_ticket.py — Python 3.13.9
------------------------------------
Modul ini berfungsi untuk mengklasifikasikan tiket pelanggan menggunakan
model LLM dari Groq API. Hasil berupa sentimen dan jenis masalah pelanggan.
"""

# ==============================================================
# 📦 Import Modul Standar dan Eksternal
# ==============================================================
from __future__ import annotations  # Memastikan dukungan type hint forward
import json
import sys
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv
from groq import Groq
import os


# ==============================================================
# ⚙️ 1. Inisialisasi Lingkungan dan API Key
# ==============================================================
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

if not ENV_PATH.exists():
    sys.exit("🚫 File .env tidak ditemukan! Pastikan .env berada di root project.")

load_dotenv(dotenv_path=ENV_PATH)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    sys.exit("🚫 GROQ_API_KEY tidak ditemukan di file .env — tambahkan kunci API Groq Anda!")

# Inisialisasi client Groq API
client = Groq(api_key=GROQ_API_KEY)


# ==============================================================
# 🧠 2. Fungsi Utama: Klasifikasi Tiket
# ==============================================================
def classify_ticket(text: str) -> Dict[str, str]:
    """
    Mengklasifikasikan teks tiket pelanggan menjadi:
    - Sentimen: Positif, Negatif, atau Netral
    - Jenis Masalah: Tagihan, Teknis, Login, Umum, atau Lainnya

    Args:
        text (str): Isi tiket pelanggan.

    Returns:
        dict: Hasil klasifikasi, misal:
            {
                "sentiment": "Negatif",
                "issue_type": "Tagihan"
            }
    """
    if not text.strip():
        return {"sentiment": "Tidak Dikenal", "issue_type": "Umum"}

    # 🧾 Prompt instruksi ke model
    prompt = f"""
Anda adalah sistem pintar untuk mengklasifikasikan tiket pelanggan.

Dari isi tiket pelanggan, klasifikasikan menjadi:
- Sentimen: Positif, Negatif, Netral
- Jenis Masalah: Tagihan, Teknis, Login, Umum, Lainnya

Jawablah HANYA dalam format JSON seperti berikut:
{{
  "sentiment": "Negatif",
  "issue_type": "Tagihan"
}}

Teks Tiket Pelanggan:
\"\"\"{text}\"\"\"
"""

    try:
        # 🔗 3. Memanggil model LLM Groq untuk analisis tiket
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
            stream=False,
        )

        # 📨 4. Mengambil hasil respon teks dari model
        content: str = completion.choices[0].message.content.strip()
        print(f"📨 [DEBUG] Respons Mentah Groq:\n{content}\n")

        # 🧩 5. Parsing hasil JSON dari model
        parsed: Dict[str, Any] = json.loads(content)

        # ✅ 6. Kembalikan hasil terstruktur
        return {
            "sentiment": parsed.get("sentiment", "Tidak Dikenal"),
            "issue_type": parsed.get("issue_type", "Umum"),
        }

    except json.JSONDecodeError:
        print("⚠️ [ERROR] Format JSON dari model tidak valid.")
        return {"sentiment": "Tidak Dikenal", "issue_type": "Umum"}

    except Exception as e:
        print(f"⚠️ [ERROR] Gagal mengklasifikasikan tiket: {e}")
        return {"sentiment": "Tidak Dikenal", "issue_type": "Umum"}


# ==============================================================
# 🧪 3. Mode Uji Langsung (Opsional)
# ==============================================================
if __name__ == "__main__":
    sample_text = input("🧾 Masukkan teks tiket pelanggan: ").strip()
    result = classify_ticket(sample_text)
    print("\n🎯 Hasil Klasifikasi:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
