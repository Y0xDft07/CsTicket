# Python 3.13.9
# ruff: noqa

"""
MCP Server untuk sistem AI Customer Support Ticket Resolver.

Modul ini bertugas menjalankan server MCP (Model Context Protocol)
yang memproses tiket bantuan pelanggan secara otomatis:
1. Menganalisis pesan pelanggan menggunakan AI (klasifikasi & sentimen)
2. Menghasilkan balasan otomatis
3. Menyimpan hasil ke Google Sheet
4. Mengirim email balasan ke pelanggan
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from tools.sheet_connector import update_ticket, append_processed_ticket
from tools.classify_ticket import classify_ticket
from tools.generate_reply import generate_reply
from tools.gmail_sender import send_email_smtp


# ==========================================================
# 🚀 Inisialisasi Server MCP
# ==========================================================
mcp = FastMCP("AICustomerSupportTicketResolver")


# ==========================================================
# 🧠 Fungsi Utama: resolve_ticket
# ==========================================================
@mcp.tool(
    name="resolve_ticket",
    description=(
        "Mengklasifikasi, membalas, memperbarui, dan mengirimkan tiket bantuan pelanggan "
        "secara otomatis menggunakan AI."
    ),
)
def resolve_ticket(name: str, email: str, message: str) -> dict[str, str]:
    """
    Memproses tiket bantuan pelanggan melalui langkah-langkah otomatis.

    Args:
        name (str): Nama pelanggan yang mengirim tiket.
        email (str): Alamat email pelanggan.
        message (str): Isi pesan atau keluhan pelanggan.

    Returns:
        dict[str, str]: Hasil akhir pemrosesan tiket, mencakup status, sentimen,
                        jenis masalah, balasan AI, dan status pengiriman email.
    """
    try:
        # ------------------------------------------------------
        # 1️⃣ Analisis Pesan Menggunakan AI
        # ------------------------------------------------------
        classification = classify_ticket(message)
        sentiment: str = classification.get("sentiment", "Tidak Diketahui")
        issue_type: str = classification.get("issue_type", "Umum")

        # ------------------------------------------------------
        # 2️⃣ Membuat Balasan Otomatis
        # ------------------------------------------------------
        reply: str = generate_reply(name, message)

        # ------------------------------------------------------
        # 3️⃣ Menyimpan Data ke Google Sheet
        # ------------------------------------------------------
        fake_ticket: dict[str, str] = {
            "Name": name,
            "Email": email,
            "IssueType": issue_type,
            "Message": message,
        }
        append_processed_ticket(fake_ticket, sentiment, issue_type, reply)

        # ------------------------------------------------------
        # 4️⃣ Mengirimkan Email Balasan ke Pelanggan
        # ------------------------------------------------------
        mail_result: dict[str, str] = send_email_smtp(
            to=email,
            subject="Terkait Tiket Bantuan Anda",
            body=reply,
        )

        # ------------------------------------------------------
        # 5️⃣ Mengembalikan Status Akhir ke Sistem Utama
        # ------------------------------------------------------
        return {
            "status": "sukses",
            "sentimen": sentiment,
            "jenis_masalah": issue_type,
            "balasan": reply,
            "status_email": mail_result.get("status", "ok"),
            "pesan_email": mail_result.get(
                "message", "✅ Email berhasil dikirim ke pelanggan."
            ),
        }

    except Exception as e:
        # ------------------------------------------------------
        # ❌ Penanganan Error
        # ------------------------------------------------------
        return {
            "status": "gagal",
            "pesan": f"Terjadi kesalahan saat memproses tiket: {e!s}",
        }


# ==========================================================
# 🏁 Jalankan Server MCP
# ==========================================================
if __name__ == "__main__":
    print("🚀 Menjalankan MCP Server...")
    mcp.run()
