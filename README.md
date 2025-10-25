# 🤖 CsTicket (Menggunakan Agents dan MCP (Model Context Protocol)

Proyek ini dibangun menggunakan **Python 3.13.9**, **Streamlit**, dan **MCP (Model Context Protocol)** untuk mengotomatisasi layanan dukungan pelanggan.
Sistem dapat **menganalisis tiket**, **mengklasifikasikan pesan pelanggan**, **menghasilkan respons otomatis**, dan **mengirimkannya langsung ke email pelanggan** menggunakan integrasi Gmail API.

---

## ⚙️ Versi dan Lingkungan

| Komponen        | Versi                                       |
| --------------- | ------------------------------------------- |
| 🐍 Python       | **3.13.9**                                  |
| 🧠 MCP CLI      | 1.9.1+                                      |
| 🌐 Streamlit    | Terbaru (diinstall dari `requirements.txt`) |
| 📬 SMTP (Gmail) | TLS/587                                     |
| 📄 Format File  | `.env`, `.yaml`, `.toml`, `.py`             |

---

## 📦 Fungsi Utama

* 📬 Menerima pesan atau pertanyaan dari pelanggan.
* 🤖 Menggunakan **AI Agents** untuk memahami dan mengklasifikasikan tiket.
* 🧠 Menentukan tingkat urgensi dan kategori tiket.
* ✉️ Menghasilkan serta mengirim balasan otomatis ke email pelanggan.
* 📊 Mencatat hasil klasifikasi dan riwayat ke **Google Sheets**.
* 💻 Menyediakan antarmuka **Streamlit** untuk input dan monitoring.

---

## 🏗️ Struktur Proyek

```
CsTicket/
│
├── .devcontainer/
│   └── devcontainer.json        # Konfigurasi VSCode Dev Container (Python 3.13.9)
│
├── tools/
│   ├── classify_ticket.py       # Klasifikasi tiket berdasarkan isi pesan
│   ├── generate_reply.py        # Membuat balasan otomatis dari hasil analisis AI
│   ├── gmail_sender.py          # Mengirim email melalui SMTP Gmail
│   └── sheet_connector.py       # Integrasi ke Google Sheets
│
├── main.py                      # Backend utama (AI Agents + Streamlit)
├── register_ticket.py            # UI Form untuk registrasi tiket
├── mcp_server.py                 # Menjalankan Model Context Protocol server
│
├── reader.yaml                   # Pengaturan layanan deploy
├── pyproject.toml                # Metadata proyek dan dependensi
├── requirements.txt              # Pustaka Python
├── .env                          # Kredensial API dan variabel rahasia
└── uv.lock, runtime.txt, dll.
```

---

## 🛠️ Instalasi & Setup Lingkungan

### 1. Clone Repositori

```bash
git clone https://github.com/Y0xDft07/CsTicket.git
cd CsTicket
```

### 2. Buat Virtual Environment (Python 3.13.9)

```bash
python3.13 -m venv venv
source venv/bin/activate  # (Linux/Mac)
venv\Scripts\activate     # (Windows)
```

### 3. Instal Dependensi

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔐 Konfigurasi Kredensial & API Key

Buat file `.env` di direktori utama dengan isi berikut:

```env
GROQ_API_KEY=your_groq_api_key
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
GOOGLE_SHEET_CRED=google_cred.json
```

---

## 🧾 Antarmuka Depan — Formulir Tiket Pelanggan

File: `register_ticket.py`
Menampilkan formulir sederhana untuk pembuatan tiket dukungan pelanggan.

```bash
streamlit run register_ticket.py
```

Akses di browser:
🔗 [http://localhost:8501](http://localhost:8501)

### Fungsi:

* Input tiket baru dari pelanggan.
* Menyimpan ke Google Sheets secara otomatis.

---

## 🤖 Backend — AI Ticket Resolver

File: `main.py`
Menangani seluruh alur otomatisasi:

1. Memantau tiket baru.
2. Menganalisis isi pesan.
3. Mengklasifikasikan berdasarkan kategori & urgensi.
4. Menghasilkan balasan dengan model AI.
5. Mengirim email melalui `gmail_sender.py`.
6. Menyimpan hasil ke Google Sheets.

Jalankan:

```bash
streamlit run main.py
```

---

## 🧠 Integrasi MCP (Model Context Protocol)

Gunakan MCP untuk menginspeksi dan mengontrol agent AI:

```bash
pip install fastmcp
mcp install mcp_server:mcp
mcp dev mcp_server.py
```

Atau menggunakan Node Inspector:

```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```

---

## 🌐 Deploy ke Cloud (Opsional)

Proyek ini siap dijalankan di:

* **Streamlit Cloud**
* **Render**
* **Google Cloud / AWS / Heroku**

Pastikan file `reader.yaml` sudah diperbarui:

```yaml
services:
  - type: web
    name: streamlit-app
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run main.py --server.port $PORT --server.headless true
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.9
```

---

## 💡 Alur Sistem (Flowchart Tekstual)

```
[Mulai]
   ↓
[Pelanggan mengirim tiket melalui Streamlit Form]
   ↓
[AI Agent memproses teks & klasifikasi masalah]
   ↓
[Generate balasan otomatis dengan LLM]
   ↓
[Gmail Sender mengirim email ke pelanggan]
   ↓
[Sheet Connector mencatat hasil ke Google Sheets]
   ↓
[Selesai - Sistem siap menerima tiket berikutnya]
```

---

## 📊 Flowchart Visual (Deskripsi)

```
┌────────────────────┐
│  Pelanggan (UI)   │
│ register_ticket.py │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────┐
│ AI Agent & Classifier  │
│ classify_ticket.py      │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ AI Response Generator  │
│ generate_reply.py       │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ Gmail Sender (SMTP)    │
│ gmail_sender.py         │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ Google Sheets Logger   │
│ sheet_connector.py      │
└────────────────────────┘
```

---

## 🚀 Log Aktivitas Terminal (Contoh)

```
🔧 Menyiapkan lingkungan Python 3.13.9...
📦 Menginstal dependensi dari requirements.txt...
✅ Semua paket berhasil diinstal!
🤖 Menjalankan AI Ticket Resolver...
📨 Mengirim email ke: support@example.com
📊 Menyimpan log ke Google Sheets...
✅ Sistem berjalan normal (Streamlit aktif di http://localhost:8501)
```

## 🤝 Kolaborasi dan Kontribusi

Kontribusi terbuka untuk siapa pun yang tertarik di bidang:

> Machine Learning • NLP • Automasi AI • Sistem Dukungan Pelanggan

Buat *pull request* atau *issue* di repositori utama untuk bergabung.

---

## 🧠 Ringkasan Alur Flowchart Utama (High-Level)

```
[Input Pelanggan]
   ↓
[Analisis NLP → Klasifikasi → Respons Otomatis]
   ↓
[Email Dikirim + Log Disimpan]
   ↓
[Dashboard & Feedback Loop]
```
