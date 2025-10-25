import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# =============================================================
# 🔐 1. Konfigurasi akses Google Sheets API
# =============================================================

# Menentukan scope agar script bisa membaca & menulis ke Google Sheets dan Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Membaca kredensial dari file JSON (Service Account Google)
# Catatan: pastikan file "google_cred.json" ada di root folder project
creds = Credentials.from_service_account_file("google_cred.json", scopes=SCOPES)

# Mengotorisasi koneksi ke Google Sheets
gs_client = gspread.authorize(creds)

# =============================================================
# 🗂️ 2. Inisialisasi nama spreadsheet dan sheet
# =============================================================

SPREADSHEET_NAME = "SupportTickets"
PENDING_SHEET_NAME = "PendingTickets"
PROCESSED_SHEET_NAME = "ProcessedTickets"

# =============================================================
# 📋 3. Mendapatkan (atau membuat) sheet PendingTickets
# =============================================================

def get_pending_sheet():
    workbook = gs_client.open(SPREADSHEET_NAME)
    try:
        sheet = workbook.worksheet(PENDING_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        # Jika belum ada, buat sheet baru dengan header
        sheet = workbook.add_worksheet(title=PENDING_SHEET_NAME, rows="1000", cols="10")
        sheet.append_row([
            "timestamp", "Name", "Email", "IssueType",
            "Message", "Sentiment", "IssueType_Label", "AutoReply"
        ])
        print("📄 Sheet 'PendingTickets' baru dibuat otomatis.")
    return sheet

# =============================================================
# 📋 4. Mendapatkan (atau membuat) sheet ProcessedTickets
# =============================================================

def get_processed_sheet():
    workbook = gs_client.open(SPREADSHEET_NAME)
    try:
        sheet = workbook.worksheet(PROCESSED_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        sheet = workbook.add_worksheet(title=PROCESSED_SHEET_NAME, rows="1000", cols="10")
        sheet.append_row([
            "timestamp", "Name", "Email", "IssueType",
            "Message", "Sentiment", "IssueType_Label", "AutoReply"
        ])
        print("📄 Sheet 'ProcessedTickets' baru dibuat otomatis.")
    return sheet

# =============================================================
# 🔍 5. Mengambil tiket baru (belum ada Sentiment/AutoReply)
# =============================================================

def fetch_new_tickets():
    sheet = get_pending_sheet()
    data = sheet.get_all_records()
    tickets = []
    for idx, row in enumerate(data, start=2):
        if not row.get('Sentiment') or not row.get('AutoReply'):
            row['RowNumber'] = idx
            tickets.append(row)
    print(f"📬 {len(tickets)} tiket baru ditemukan untuk diproses.")
    return tickets

# =============================================================
# 📝 6. Memperbarui tiket di sheet PendingTickets
# =============================================================

def update_ticket(row_number: int, sentiment: str, issue_type: str, reply: str):
    sheet = get_pending_sheet()
    try:
        sheet.update_cell(row_number, 6, sentiment)
        sheet.update_cell(row_number, 7, issue_type)
        sheet.update_cell(row_number, 8, reply)
        print(f"✅ Baris {row_number} diperbarui di PendingTickets.")
    except Exception as e:
        print(f"❌ Gagal memperbarui baris {row_number}: {e}")

# =============================================================
# 📤 7. Menyalin tiket yang telah diproses ke ProcessedTickets
# =============================================================

def append_processed_ticket(ticket: dict, sentiment: str, issue_type: str, reply: str):
    sheet = get_processed_sheet()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([
            timestamp,
            ticket.get("Name", ""),
            ticket.get("Email", ""),
            ticket.get("IssueType", issue_type),
            ticket.get("Message", ""),
            sentiment,
            issue_type,
            reply
        ])
        print("📦 Tiket dipindahkan ke ProcessedTickets.")
    except Exception as e:
        print(f"❌ Gagal memindahkan tiket ke ProcessedTickets: {e}")

# =============================================================
# 🗑️ 8. Menghapus tiket dari PendingTickets setelah diproses
# =============================================================

def delete_ticket_from_pending(row_number: int):
    sheet = get_pending_sheet()
    try:
        sheet.delete_rows(row_number)
        print(f"🗑️ Tiket baris {row_number} dihapus dari PendingTickets.")
    except Exception as e:
        print(f"❌ Gagal menghapus tiket baris {row_number}: {e}")

# =============================================================
# 📂 9. Mengambil semua tiket yang sudah diproses
# =============================================================

def fetch_processed_tickets():
    sheet = get_processed_sheet()
    try:
        data = sheet.get_all_records()
        print(f"📊 {len(data)} tiket berhasil diambil dari ProcessedTickets.")
        return data
    except Exception as e:
        print(f"❌ Gagal mengambil data tiket yang sudah diproses: {e}")
        return []
