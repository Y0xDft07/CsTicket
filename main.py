"""
🤖 Aplikasi Manajer Tiket Layanan Pelanggan (AI)
Diperbarui untuk Python 3.13.9
"""

from __future__ import annotations
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from typing import Dict, Any, List

# ---------- Import Modul Internal ----------
from tools.sheet_connector import (
    fetch_new_tickets,             # Ambil tiket baru dari Google Sheet
    update_ticket,                 # Update data tiket setelah diproses
    append_processed_ticket,       # Tambahkan ke sheet tiket yang sudah diproses
    delete_ticket_from_pending,    # Hapus tiket dari daftar pending
    fetch_processed_tickets        # Ambil data tiket yang sudah dianalisis
)
from tools.classify_ticket import classify_ticket     # AI klasifikasi pesan tiket
from tools.generate_reply import generate_reply       # AI buat balasan otomatis
from tools.gmail_sender import send_email_smtp        # Kirim email otomatis

# ---------- Muat file konfigurasi (.env) ----------
load_dotenv()

# ---------- Desain & Tema UI ----------
st.markdown("""
<style>
div[data-testid="stSidebar"] > div:first-child {
    width: 350px;
    font-size: 20px;
}
.block-container {
    max-width: 1500px;
    padding: 2rem 2rem;
}
.centered-header {
    text-align: center;
    font-size: 3.4rem;
    font-weight: 800;
    color: #0f172a;
    margin-top: 1rem;
    margin-bottom: 2rem;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.ticket-box {
    background-color: #ffffff;
    border-left: 6px solid #3b82f6;
    padding: 1rem 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-top: 1rem;
    margin-bottom: 1rem;
    font-size: 18px;
}
.ticket-details {
    background-color: #f9fafb;
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 1rem;
}
.ticket-header {
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.3rem;
}
.ticket-category {
    font-size: 0.9rem;
    color: #2563eb;
    margin-bottom: 0.6rem;
}
.ticket-message {
    white-space: pre-wrap;
    color: #374151;
}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar Navigasi ----------
st.sidebar.title("📌 Navigasi Utama")
tab_selection: str = st.sidebar.radio(
    "Pilih Halaman:",
    ["📋 Tiket Belum Diproses", "📂 Tiket Sudah Dianalisis", "📊 Dashboard Analisis"]
)

# ---------- Header Utama ----------
st.markdown(
    "<div class='centered-header'>🤖 Dashboard Manajemen Tiket Layanan Pelanggan AI</div>",
    unsafe_allow_html=True
)

# ---------- Ambil Data ----------
pending_tickets: List[Dict[str, Any]] = fetch_new_tickets()
processed_tickets: List[Dict[str, Any]] = fetch_processed_tickets()


# ================== Fungsi Bantu ==================
def format_ticket_label(ticket: Dict[str, Any], idx: int) -> str:
    """Format label tampilan tiket."""
    return f"#{idx} - {ticket.get('Name', 'Tanpa Nama')} ({ticket.get('Email', '-')})"


def filter_by_date_range(df: pd.DataFrame, date_col: str, label: str) -> pd.DataFrame:
    """Filter dataframe berdasarkan rentang tanggal."""
    df = df.dropna(subset=[date_col])
    if df.empty:
        st.info(f"Tidak ada data tanggal valid untuk {label}.")
        return df

    min_date, max_date = df[date_col].min().date(), df[date_col].max().date()
    if min_date == max_date:
        max_date += datetime.timedelta(days=1)

    selected_range = st.date_input(
        f"Filter {label} berdasarkan rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    start, end = (
        selected_range if isinstance(selected_range, tuple)
        else (selected_range, selected_range)
    )

    return df[
        (df[date_col].dt.date >= start) &
        (df[date_col].dt.date <= end)
    ]


# ================== TAB 1: Tiket Belum Diproses ==================
if tab_selection == "📋 Tiket Belum Diproses":
    st.subheader("📋 Daftar Tiket Belum Diproses")

    if not pending_tickets:
        st.success("✅ Semua tiket sudah diproses.")
    else:
        # Klasifikasi otomatis tiket baru
        for ticket in pending_tickets:
            if not ticket.get("IssueType_Label"):
                klasifikasi = classify_ticket(ticket["Message"])
                ticket["IssueType_Label"] = klasifikasi.get("issue_type", "Tidak Diketahui")
                ticket["Sentiment"] = klasifikasi.get("sentiment", "Netral")

        analyzed = [t for t in pending_tickets if t.get("IssueType_Label")]
        unanalyzed = [t for t in pending_tickets if not t.get("IssueType_Label")]

        col1, col2 = st.columns(2)

        # Kolom Tiket Belum Dianalisis
        with col1:
            st.markdown("### ⏳ Tiket Menunggu Analisis")
            if not unanalyzed:
                st.success("Tidak ada tiket baru untuk dianalisis.")
            else:
                for i, t in enumerate(unanalyzed, start=1):
                    st.markdown(
                        f"""
                        <div class='ticket-box'>
                            <strong>📩 Tiket #{i}</strong><br>
                            <strong>Nama:</strong> {t['Name']}<br>
                            <strong>Email:</strong> {t['Email']}<br>
                            <strong>Pesan:</strong><br>{t['Message']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # Kolom Tiket Sudah Dianalisis (Belum Dikirim)
        with col2:
            st.markdown("### ✅ Tiket Sudah Dianalisis (Belum Dikirim)")
            if not analyzed:
                st.info("Belum ada tiket yang dianalisis.")
            else:
                kategori = sorted({t["IssueType_Label"] for t in analyzed})
                pilih_kategori = st.multiselect("🎯 Pilih Kategori", kategori, default=kategori)
                filtered = [t for t in analyzed if t["IssueType_Label"] in pilih_kategori]

                selected_to_send: Dict[int, bool] = {}

                for i, t in enumerate(filtered, start=1):
                    col_a, col_b = st.columns([0.05, 0.95])
                    with col_a:
                        selected_to_send[i] = st.checkbox("", key=f"send_ticket_{i}")
                    with col_b:
                        st.markdown(
                            f"""
                            <div class='ticket-details'>
                                <div class='ticket-header'>📨 Tiket #{i} - {t['Name']} ({t['Email']})</div>
                                <div class='ticket-category'>Kategori: {t['IssueType_Label']}</div>
                                <div class='ticket-message'>{t['Message']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                # Tombol Kirim Email
                if st.button("✉️ Kirim Balasan ke Tiket yang Dipilih"):
                    to_send = [t for i, t in enumerate(filtered, start=1) if selected_to_send.get(i)]
                    if not to_send:
                        st.warning("Pilih minimal satu tiket untuk dikirim.")
                    else:
                        for t in to_send:
                            reply = t.get("AutoReply") or generate_reply(t["Name"], t["Message"])
                            t["AutoReply"] = reply
                            send_email_smtp(t["Email"], "Balasan Tiket Dukungan", reply)
                            update_ticket(t.get("RowNumber"), t["Sentiment"], t["IssueType_Label"], reply)
                            append_processed_ticket(t, t["Sentiment"], t["IssueType_Label"], reply)
                            delete_ticket_from_pending(t.get("RowNumber"))

                        st.success(f"✅ Berhasil mengirim {len(to_send)} balasan tiket.")


# ================== TAB 2: Tiket Sudah Dianalisis ==================
elif tab_selection == "📂 Tiket Sudah Dianalisis":
    st.subheader("📂 Daftar Tiket yang Sudah Diproses")

    if not processed_tickets:
        st.info("Belum ada tiket yang dianalisis.")
    else:
        df = pd.DataFrame(processed_tickets)
        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

        jenis_issue = sorted(df["IssueType_Label"].dropna().unique().tolist())
        pilih_issue = st.multiselect("Filter berdasarkan Jenis Masalah", jenis_issue, default=jenis_issue)

        if "Timestamp" in df.columns:
            df = filter_by_date_range(df, "Timestamp", "Tiket yang Sudah Diproses")

        df = df[df["IssueType_Label"].isin(pilih_issue)]

        if df.empty:
            st.info("Tidak ada tiket sesuai filter.")
        else:
            pilihan = [format_ticket_label(t, i) for i, t in enumerate(df.to_dict("records"), start=1)]
            pilih_tiket = st.selectbox("Pilih tiket untuk dilihat", pilihan)
            idx = pilihan.index(pilih_tiket)
            tiket = df.to_dict("records")[idx]

            st.markdown(f"<div class='ticket-box'><strong>📝 Pesan:</strong><br>{tiket['Message']}</div>", unsafe_allow_html=True)
            st.markdown(f"**Sentimen:** `{tiket.get('Sentiment', '')}`")
            st.markdown(f"**Jenis Masalah:** `{tiket.get('IssueType_Label', '')}`")
            st.markdown("**📬 Balasan yang Dikirim:**")
            st.text_area("Balasan Otomatis", tiket.get("AutoReply", ""), height=140, disabled=True)


# ================== TAB 3: Dashboard Analisis ==================
elif tab_selection == "📊 Dashboard Analisis":
    st.subheader("📊 Analisis Data Tiket")

    if not processed_tickets:
        st.info("Belum ada data tiket untuk ditampilkan.")
    else:
        df = pd.DataFrame(processed_tickets)
        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

        df = filter_by_date_range(df, "Timestamp", "Dashboard")

        col1, col2 = st.columns(2)

        # Grafik Sentimen
        with col1:
            st.subheader("📊 Distribusi Sentimen")
            data_sentimen = df["Sentiment"].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(data_sentimen, labels=data_sentimen.index, autopct="%1.1f%%")
            ax1.axis("equal")
            st.pyplot(fig1)

        # Grafik Jenis Masalah
        with col2:
            st.subheader("🗂️ Distribusi Jenis Masalah")
            data_issue = df["IssueType_Label"].value_counts()
            fig2, ax2 = plt.subplots()
            ax2.bar(data_issue.index, data_issue.values)
            ax2.set_ylabel("Jumlah Tiket")
            ax2.set_xlabel("Jenis Masalah")
            st.pyplot(fig2)
