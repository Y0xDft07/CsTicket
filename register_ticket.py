# ruff: noqa
# Python 3.13.9

import streamlit as st
from datetime import datetime
from tools.sheet_connector import get_pending_sheet

# ======================================================
# 🧩 KONFIGURASI HALAMAN
# ======================================================
st.set_page_config(
    page_title="📩 Kirim Tiket Bantuan",
    page_icon="📩",
    layout="centered",
    initial_sidebar_state="auto",
)

# ======================================================
# 🎨 GAYA (CSS KUSTOM)
# ======================================================
st.markdown(
    """
<style>
    .main {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
        border: none;
    }
    .stTextInput, .stTextArea, .stSelectbox {
        background-color: #ffffff !important;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ======================================================
# 🧾 JUDUL HALAMAN
# ======================================================
st.title("📩 Formulir Tiket Bantuan")
st.markdown(
    "Silakan isi formulir berikut agar tim dukungan kami dapat membantu Anda secepatnya."
)


# ======================================================
# 💾 FUNGSI PENYIMPANAN DATA KE GOOGLE SHEET
# ======================================================
def append_ticket_to_pending(
    name: str, email: str, issue_type: str, message: str
) -> bool:
    """
    Menambahkan tiket baru ke Google Sheet 'PendingTickets'.

    Args:
        name (str): Nama lengkap pengirim tiket.
        email (str): Alamat email pengirim tiket.
        issue_type (str): Jenis masalah yang dilaporkan.
        message (str): Pesan atau deskripsi masalah.

    Returns:
        bool: True jika tiket berhasil dikirim, False jika terjadi kesalahan.
    """
    sheet = get_pending_sheet()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Menambahkan baris baru ke sheet dengan kolom tambahan kosong
        sheet.append_row([timestamp, name, email, issue_type, message, "", "", ""])
        return True
    except Exception as e:
        st.error(f"Gagal mengirim tiket ke PendingTickets: {e!s}")
        return False


# ======================================================
# 🧠 FORM INPUT UTAMA
# ======================================================
with st.form("ticket_form"):
    st.subheader("📝 Informasi Tiket")

    # Kolom input dibagi dua
    col1, col2 = st.columns(2)
    with col1:
        name: str = st.text_input("Nama Lengkap", placeholder="Contoh: Andi Pratama")
    with col2:
        email: str = st.text_input("Alamat Email", placeholder="Contoh: andi@example.com")

    issue_type: str = st.selectbox(
        "Pilih Jenis Masalah", ["Tagihan", "Teknis", "Masalah Login", "Lainnya"]
    )

    message: str = st.text_area(
        "Deskripsikan masalah Anda secara detail",
        height=200,
        placeholder="Tuliskan masalah atau kendala yang Anda alami...",
    )

    submitted: bool = st.form_submit_button("📨 Kirim Tiket")

    # ==================================================
    # 🧩 VALIDASI & PENYIMPANAN
    # ==================================================
    if submitted:
        # Cek input wajib
        if not all([name.strip(), email.strip(), message.strip()]):
            st.error("⚠️ Harap isi semua kolom yang wajib diisi sebelum mengirim.")
        else:
            success: bool = append_ticket_to_pending(
                name.strip(), email.strip(), issue_type, message.strip()
            )
            if success:
                st.success("✅ Tiket Anda berhasil dikirim! Tim kami akan segera menghubungi Anda.")
            else:
                st.error("❌ Terjadi kesalahan saat mengirim tiket. Silakan coba lagi nanti.")
