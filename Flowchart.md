## 🧩 **Flowchart Tekstual (Langkah demi Langkah)**

```
┌────────────────────────────┐
│      MULAI PROGRAM         │
│  (Jalankan main_1.py via   │
│  Streamlit di devcontainer)│
└──────────────┬─────────────┘
               │
               ▼
     ┌────────────────────────────┐
     │ Inisialisasi Lingkungan   │
     │ - Load .env               │
     │ - Import tools/           │
     │ - Set judul & layout UI   │
     └──────────────┬────────────┘
                    │
                    ▼
          ┌────────────────────────────┐
          │ Ambil Data Tiket Baru dari │
          │ Google Sheet (Pending)     │
          │ → fetch_new_tickets()      │
          └──────────────┬────────────┘
                         │
                         ▼
            ┌──────────────────────────┐
            │ Apakah ada tiket baru?   │
            ├──────────────┬───────────┤
            │ Tidak         │ Ya        │
            ▼               ▼
  ┌────────────────┐  ┌─────────────────────────┐
  │ Tampilkan info │  │ Tampilkan tiket di UI   │
  │ "Tidak ada"    │  │ (Nama, Email, Pesan)    │
  └────────────────┘  └──────────────┬──────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │ Klik tombol "Analisis &  │
                       │ Tanggapi" oleh pengguna  │
                       └──────────────┬───────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────┐
                   │ Jalankan AI Classifier:        │
                   │ → classify_ticket.py           │
                   │   - Kirim pesan ke model Llama │
                   │   - Terima hasil JSON:         │
                   │     Sentiment + Issue Type     │
                   └────────────────┬───────────────┘
                                    │
                                    ▼
                   ┌────────────────────────────────┐
                   │ Jalankan AI Reply Generator:   │
                   │ → generate_reply.py            │
                   │   - Buat balasan profesional   │
                   │     dgn nama pelanggan         │
                   └────────────────┬───────────────┘
                                    │
                                    ▼
                   ┌────────────────────────────────┐
                   │ Update Data di Google Sheet:   │
                   │ → sheet_connector.py           │
                   │   - update_ticket() (Pending)  │
                   │   - append_processed_ticket()  │
                   │     (Processed + timestamp)    │
                   └────────────────┬───────────────┘
                                    │
                                    ▼
                   ┌────────────────────────────────┐
                   │ Kirim Email Otomatis ke User   │
                   │ → gmail_sender.py              │
                   │   - SMTP Gmail API             │
                   │   - Kirim isi balasan AI       │
                   │   - Tampilkan status sukses    │
                   └────────────────┬───────────────┘
                                    │
                                    ▼
                        ┌──────────────────────────┐
                        │ Tampilkan hasil di UI:   │
                        │ ✅ Email terkirim        │
                        │ ✅ Tiket diperbarui      │
                        │ ✅ Log tersimpan         │
                        └──────────────┬───────────┘
                                       │
                                       ▼
                           ┌──────────────────────┐
                           │  SELESAI PROSES      │
                           │  (Menunggu tiket     │
                           │   baru berikutnya)   │
                           └──────────────────────┘
```
---

### 🔄 **Alur Utama Sistem**

#### 1️⃣ **Mulai (Start Program)**

* Sistem dijalankan melalui `main.py` atau `mcp_server.py`.
* Streamlit UI aktif otomatis dari konfigurasi di `.devcontainer/devcontainer.json`.

#### 2️⃣ **Input Tiket Pelanggan**

* Pengguna (admin/operator) mengisi form atau sistem otomatis membaca email pelanggan.
* Data berisi:
  `Nama`, `Email`, `IssueType`, `Pesan`.

#### 3️⃣ **Simpan Tiket ke Pending Sheet**

* Modul: `tools/sheet_connector.py`
* Fungsi: `get_pending_sheet()` → membuat/akses sheet "PendingTickets".
* Tiket baru disimpan ke Google Sheets dengan status **belum diproses**.

#### 4️⃣ **Ambil Tiket yang Belum Diproses**

* Fungsi: `fetch_new_tickets()`
* Mengecek tiket dengan kolom kosong di “Sentiment” atau “AutoReply”.

#### 5️⃣ **Analisis Tiket (Klasifikasi + Sentimen)**

* Modul: `tools/classify_ticket.py`
* Model AI menganalisis isi pesan untuk mendeteksi:

  * **Jenis Masalah** (Issue Type): misal “Login”, “Pembayaran”, “Layanan”.
  * **Sentimen**: positif, negatif, atau netral.

#### 6️⃣ **Generate Auto Reply (Balasan Otomatis)**

* Modul: `tools/generate_reply.py`
* Berdasarkan hasil klasifikasi, sistem membuat teks balasan otomatis yang sopan, relevan, dan personal.

  * Contoh:
    “Halo [Nama], terima kasih sudah menghubungi kami. Kami akan segera memperbaiki masalah login Anda.”

#### 7️⃣ **Perbarui Data di Pending Sheet**

* Fungsi: `update_ticket()`
* Kolom “Sentiment”, “IssueType_Label”, dan “AutoReply” diperbarui dengan hasil analisis.

#### 8️⃣ **Pindahkan ke Processed Sheet**

* Fungsi: `append_processed_ticket()`
* Menyalin tiket yang sudah selesai ke sheet **ProcessedTickets** dengan timestamp.

#### 9️⃣ **Hapus Tiket dari Pending Sheet**

* Fungsi: `delete_ticket_from_pending()`
* Menghapus baris yang sudah dipindahkan agar tidak diproses ulang.

#### 🔟 **Kirim Email Balasan ke Pelanggan**

* Modul: `tools/gmail_sender.py`
* Sistem mengirimkan isi `AutoReply` ke alamat email pelanggan secara otomatis.

#### 11️⃣ **Selesai (End Process)**

* Tiket sudah berpindah dari “Pending” → “Processed”.
* Pelanggan menerima balasan otomatis.
* Admin dapat melihat seluruh riwayat tiket di sheet “ProcessedTickets”.


---

## 🧠 **Ringkasan Alur Tiap Komponen**

| Komponen                              | Fungsi Utama                                                                           | Interaksi                              |
| ------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------- |
| **`main_1.py`**                       | Antarmuka utama pengguna (Streamlit)                                                   | Menampilkan tiket & memicu analisis AI |
| **`tools/classify_ticket.py`**        | Mengklasifikasi pesan (emosi & jenis masalah) menggunakan model Groq (Llama 3)         | Dipanggil oleh main_1                  |
| **`tools/generate_reply.py`**         | Membuat balasan otomatis berbasis teks tiket                                           | Dipanggil setelah klasifikasi          |
| **`tools/gmail_sender.py`**           | Mengirim email hasil balasan AI ke pelanggan                                           | Menggunakan SMTP Gmail                 |
| **`tools/sheet_connector.py`**        | Menyimpan, memperbarui, dan mengambil tiket dari Google Sheets                         | Mengelola data mentah dan hasil        |
| **`.devcontainer/devcontainer.json`** | Menyediakan lingkungan otomatis untuk menjalankan Streamlit di VS Code atau Codespaces | Membangun environment proyek           |
| **`.env`**                            | Menyimpan variabel rahasia (API Key, email, password)                                  | Digunakan di semua modul tools/*       |

---

## 🎨 **Deskripsi Flow Visual (Diagram)**

Berikut struktur hubungan antar file (diagram data flow sederhana):

```
         ┌──────────────────────────┐
         │     User / Operator      │
         │  (via Streamlit UI)      │
         └────────────┬─────────────┘
                      │
                      ▼
             ┌────────────────────┐
             │     main_1.py      │
             │  (Aplikasi Utama)  │
             └──┬──────────────┬──┘
                │              │
     ┌──────────┘              └──────────┐
     ▼                                     ▼
┌──────────────┐                   ┌─────────────────┐
│ classify_... │                   │ generate_reply  │
│ (AI analisis)│                   │ (AI balasan)    │
└──────────────┘                   └─────────────────┘
     │                                     │
     ▼                                     ▼
┌─────────────────┐                ┌─────────────────┐
│ sheet_connector │<──────────────▶│ gmail_sender    │
│ (update Sheet)  │                │ (kirim email)   │
└─────────────────┘                └─────────────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │ Google Sheets Cloud │
            │ (Data Pending + Log)│
            └─────────────────────┘
```

---

## 💬 **Output Akhir (yang tampil di aplikasi)**

```
📨 AI Customer Support Ticket Manager
-------------------------------------
📝 Pesan: "Akun saya tidak bisa login."
🤖 Sedang menganalisis...

✅ Hasil Analisis:
   Sentimen: Negatif
   Jenis Masalah: Login

📬 Balasan Otomatis:
Halo [Nama Pengguna],
Terima kasih telah menghubungi kami...
Best regards, Customer Support Team

📤 Email terkirim ke: user@gmail.com
📝 Data tersimpan di Google Sheet (ProcessedTickets)
```

---

## 📁 **Hubungan dengan Struktur Folder**

```
CsTicket/
│
├── main_1.py                → Alur utama aplikasi
├── tools/
│   ├── classify_ticket.py    → Analisis emosi & kategori tiket
│   ├── generate_reply.py     → Buat balasan otomatis
│   ├── gmail_sender.py       → Kirim email via SMTP
│   └── sheet_connector.py    → Koneksi ke Google Sheets
│
├── .devcontainer/devcontainer.json → Setup environment otomatis
├── .env                        → Kunci API dan kredensial rahasia
└── requirements.txt            → Daftar dependensi Python
```