# Python 3.13.9
# ruff: noqa

"""
AI Customer Support Ticket Manager
-----------------------------------
Aplikasi Streamlit yang memproses tiket pelanggan secara otomatis menggunakan:
- AI untuk klasifikasi dan analisis sentimen
- Gmail API untuk pengiriman balasan otomatis
- Google Sheet untuk penyimpanan dan pencatatan tiket
"""

from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv
from tools.sheet_connector import (
    fetch_new_tickets,        # Mengambil tiket baru dari sheet
    update_ticket,            # Memperbarui tiket dengan hasil analisis
    append_processed_ticket   # Menyimpan tiket ke tab 'ProcessedTickets'
)
from tools.classify_ticket import classify_ticket   # Modul AI klasifikasi
from tools.generate_reply import generate_reply     # Modul AI pembuat balasan
from tools.gmail_sender import send_email_smtp      # Modul pengirim email


# ======================================================
# ⚙️ 1️⃣ Memuat Konfigurasi & Variabel Lingkungan
# ======================================================
load_dotenv()

# ======================================================
# 🧭 2️⃣ Pengaturan Halaman Streamlit
# ======================================================
st.set_page_config(
    page_title="🤖 Manajer Tiket Bantuan AI",
    layout="centered",
)

# ======================================================
# 🧾 3️⃣ Judul dan Deskripsi Halaman
# ======================================================
st.title("🤖 Manajer Tiket Dukungan Pelanggan (AI)")
st.caption(
    "Aplikasi ini menganalisis, mengklasifikasikan, membalas, dan mencatat tiket "
    "pelanggan secara otomatis menggunakan AI & Gmail API."
)

# ======================================================
# 📥 4️⃣ Ambil Data Tiket Baru dari Google Sheet
# ======================================================
tickets: list[dict[str, str]] = fetch_new_tickets()

# ======================================================
# 📭 5️⃣ Kondisi Jika Tidak Ada Tiket Baru
# ======================================================
if not tickets:
    st.success("✅ Tidak ada tiket baru untuk diproses saat ini.")
else:
    # ==================================================
    # 🔁 6️⃣ Looping untuk Memproses Setiap Tiket Baru
    # ==================================================
    for i, ticket in enumerate(tickets, start=1):

        # Lewati tiket yang sudah memiliki hasil analisis sebelumnya
        if ticket.get("Sentiment") and ticket.get("AutoReply"):
            continue

        # ==================================================
        # 📩 7️⃣ Tampilan Tiket dalam Komponen Expander
        # ==================================================
        with st.expander(f"📩 Tiket #{i} dari {ticket['Name']} ({ticket['Email']})"):
            st.markdown("**📝 Pesan Pelanggan:**")
            st.info(ticket["Message"])

            # ==================================================
            # 🧠 8️⃣ Tombol Proses Tiket & Logika AI
            # ==================================================
            if st.button(f"🔍 Analisis & Balas Tiket #{i}"):
                with st.spinner("🤖 AI sedang menganalisis pesan dan membuat balasan..."):
                    try:
                        # Step 1: Analisis isi tiket (klasifikasi & sentimen)
                        classification: dict[str, str] = classify_ticket(ticket["Message"])

                        # Step 2: Buat balasan otomatis menggunakan model AI
                        reply: str = generate_reply(ticket["Message"])

                        # Tampilkan hasil analisis
                        st.success("✅ Analisis AI Selesai!")
                        st.markdown(f"**Sentimen Pelanggan:** `{classification['sentiment']}`")
                        st.markdown(f"**Jenis Masalah:** `{classification['issue_type']}`")
                        st.markdown("**📬 Balasan Otomatis yang Dihasilkan:**")
                        st.text_area("Isi Balasan Otomatis", reply, height=140)

                        # ==================================================
                        # 💾 9️⃣ Simpan Hasil Analisis ke Google Sheet
                        # ==================================================
                        update_ticket(
                            row_number=i + 1,
                            sentiment=classification["sentiment"],
                            issue_type=classification["issue_type"],
                            reply=reply,
                        )

                        append_processed_ticket(
                            ticket=ticket,
                            sentiment=classification["sentiment"],
                            issue_type=classification["issue_type"],
                            reply=reply,
                        )

                        # ==================================================
                        # 📤 🔟 Kirim Email Balasan ke Pelanggan
                        # ==================================================
                        with st.spinner("📤 Mengirim email balasan ke pelanggan..."):
                            success: bool = send_email_smtp(
                                to=ticket["Email"],
                                subject="Balasan Tiket Dukungan Anda",
                                body=reply,
                            )

                        if success:
                            st.success("📬 Email berhasil dikirim ke pelanggan!")
                        else:
                            st.error(
                                "❌ Gagal mengirim email. Periksa konfigurasi SMTP atau App Password Anda."
                            )

                        st.info("📝 Tiket telah diperbarui, dicatat, dan pelanggan sudah diberi notifikasi.")

                    except Exception as e:
                        st.error(f"⚠️ Terjadi kesalahan saat memproses tiket: {e!s}")
