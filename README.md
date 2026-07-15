# Creative Alibi v2.0 - The "Proof of Human Effort" Protocol

---

# 🇬🇧 English

**Creative Alibi** is a Microsoft Word Add-in that acts as a digital notary, recording the process of writing to mathematically prove that the text was created by a human. It provides defense against false accusations from faulty AI detectors.

Built for the **AI Builders Challenge** — theme "Reimagine Creative Industries with AI".

### Architecture (Multi-Layer Forensics)
1. **Layer 1: Behavioral Engine (Offline)** — Analyzes keystroke rhythms, editing bursts, and pauses.
2. **Layer 2: Linguistic Engine (Offline)** — Analyzes lexical diversity using Zipf's Law and Hapax Legomena.
3. **Layer 3: External API Verification (Consent-based)** — Integrates with powerful AI models like **IBM watsonx.ai (Granite)**, GPTZero, ZeroGPT, and Desklib through a secured proxy server on Cloud Run.
4. **Layer 4: Blockchain Timestamping** — Bitcoin-anchored proof via OpenTimestamps.

### Why IBM watsonx.ai?
For the IBM AI Builders Challenge, we leverage **IBM watsonx.ai** and its Granite foundation models. By analyzing linguistic patterns through Granite models, we get an enterprise-grade forensic classification to complement our local offline layers.

### Quick Setup
```bash
npm install
npm run server      # backend proxy on localhost:3001
npm run dev-server   # taskpane dev server
```
> Note: `npm run dev:all` uses a Windows-only `start` command and won't work on macOS/Linux. Run `server` and `dev-server` in two separate terminals instead, or install `concurrently` to combine them.

---

# 🇮🇩 Bahasa Indonesia

**Creative Alibi** adalah Add-in Microsoft Word yang bertindak sebagai notaris digital, merekam proses mengetik untuk membuktikan secara matematis bahwa teks tersebut dibuat oleh manusia murni. Aplikasi ini memberikan perlindungan dari tuduhan palsu *AI detector*.

### Arsitektur (Multi-Layer Forensics)
1. **Layer 1: Mesin Perilaku (Offline)** — Menganalisis ritme ketikan, lonjakan (*burst*) penyalinan, dan jeda natural.
2. **Layer 2: Mesin Linguistik (Offline)** — Menganalisis kekayaan kosakata menggunakan Hukum Zipf dan *Hapax Legomena*.
3. **Layer 3: Verifikasi API Eksternal (Berbasis Persetujuan)** — Terintegrasi dengan model AI canggih seperti **IBM watsonx.ai (Granite)**, GPTZero, ZeroGPT, dan Desklib melalui proxy server yang aman di Cloud Run.
4. **Layer 4: Blockchain Timestamping** — Bukti timestamp berbasis Bitcoin via OpenTimestamps.

### Kenapa menggunakan IBM watsonx.ai?
Khusus untuk IBM AI Builders Challenge, kami memanfaatkan **IBM watsonx.ai** dengan model unggulannya, *Granite*. Analisis dari *foundation model* IBM memberikan tingkat klasifikasi forensik standar *enterprise* yang melengkapi algoritma *offline* lokal kami.

### Cara Menjalankan (Lokal)
```bash
npm install
cp server/.env.example server/.env   # isi API key masing-masing provider
npm run server      # backend proxy di localhost:3001
npm run dev-server   # taskpane dev server
```

---

## 🔗 Live Demo — Cloud Run

Backend proxy server berjalan di Google Cloud Run:

**Base URL: `https://ai-alibi-backend-994794168239.asia-southeast2.run.app`**

| Resource | URL |
|---|---|
| Health check | [`/health`](https://ai-alibi-backend-994794168239.asia-southeast2.run.app/health) |
| Manifest add-in | [`/manifest.xml`](https://ai-alibi-backend-994794168239.asia-southeast2.run.app/manifest.xml) |
| Taskpane UI | [`/taskpane.html`](https://ai-alibi-backend-994794168239.asia-southeast2.run.app/taskpane.html) |

Detector model lokal (Desklib) berjalan sebagai service terpisah:

| Service | URL |
|---|---|
| **desklib-detector** | https://desklib-detector-994794168239.asia-southeast2.run.app |

---

## 📖 Tutorial Penggunaan

### 1. 🚀 Akses API Cloud Run

| Endpoint | Method | Auth | Deskripsi |
|----------|--------|------|-----------|
| `/health` | GET | — | Cek status server, provider aktif, dan kesehatan dependency (Desklib, GCS) |
| `/api/detect` | POST | X-API-Key | Deteksi apakah teks buatan AI |
| `/api/support` | POST | — | Chat dengan support AI |
| `/api/license/request` | POST | — | Ajukan permintaan akses lisensi |
| `/api/admin/*` | GET/POST | Admin Password | Kelola lisensi (dashboard admin) |

### 2. 🔬 Deteksi Teks AI
**Request:**
```bash
curl -X POST https://ai-alibi-backend-994794168239.asia-southeast2.run.app/api/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <api-key-kamu>" \
  -d '{"provider":"desklib","text":"Teks yang ingin diperiksa (minimum 50 karakter)..."}'
```

**Status provider saat ini:**
| Provider | Status | Keterangan |
|----------|--------|------------|
| `desklib` | ✅ Aktif | Model lokal DeBERTa-v3 (self-hosted di Cloud Run) |
| `zerogpt` | ⚠️ Key terpasang, akses API masih ditolak (403) | Menunggu konfirmasi dari support ZeroGPT |
| `watsonx` | ⚠️ Key tidak valid | Perlu akun IBM Cloud baru |
| `gptzero` | ⬜ Belum dikonfigurasi | Butuh API key dari gptzero.me |
| `hix` | ⬜ Belum dikonfigurasi | Butuh kredensial HIX premium |

### 3. 💬 Support Chat
```bash
curl -X POST https://ai-alibi-backend-994794168239.asia-southeast2.run.app/api/support \
  -H "Content-Type: application/json" \
  -d '{"message":"Halo, bagaimana cara kerja Creative Alibi?"}'
```

### 4. 📝 Integrasi Microsoft Word
1. Clone repo: `git clone https://github.com/indri007/ai-alibi.git`
2. Buka Word → **Insert** → **Get Add-ins** → **Upload My Add-in**
3. Masukkan URL manifest: `https://ai-alibi-backend-994794168239.asia-southeast2.run.app/manifest.xml`
4. Tab **Creative Alibi** akan muncul di ribbon, sudah terhubung otomatis ke Cloud Run

### 5. 🔑 Sistem Lisensi
Creative Alibi menggunakan alur persetujuan akses berbasis email:
1. Pengguna mengajukan permintaan akses lewat form
2. Admin menerima email approval dengan tombol **Setujui**/**Tolak**
3. Setelah disetujui, kode lisensi otomatis dikirim ke email pemohon
4. Kode lisensi dimasukkan di halaman aktivasi add-in

Admin juga bisa generate lisensi manual lewat CLI:
```bash
node server/scripts/generate-license.js 365 "nama pembeli"
```

### 6. 🛠️ Fitur Utama
- ✅ **Keystroke Forensics** — Rekam kebiasaan mengetik
- ✅ **Linguistic Analysis** — Analisis gaya bahasa (Zipf's Law)
- ✅ **Multi-Provider Detection** — Desklib, ZeroGPT, watsonx, GPTZero, HIX
- ✅ **Real-time Tracking** — Pantau proses menulis langsung
- ✅ **Digital Certificate** — Bukti otentik tulisan manusia
- ✅ **Blockchain Timestamping** — OpenTimestamps (Bitcoin-anchored)
- ✅ **Support Chat AI** — Tanya jawab langsung
- ✅ **Sistem Lisensi** — Approval akses berbasis email

### 7. 🏗️ Struktur Project
```
server/
├── index.js               # Entry point utama
├── config/env.js          # Validasi environment variable saat startup
├── utils/logger.js        # Logging terstruktur
├── routes/                 # Route per-domain
│   ├── auth.js             # Google OAuth
│   ├── detect.js           # Endpoint deteksi AI
│   ├── support.js          # Support chat
│   └── admin.js             # Manajemen lisensi (rate-limited)
├── middleware/
│   └── errorHandler.js      # Error handler terpusat
├── lib/
│   ├── licenses.js          # Logic lisensi (GCS-backed)
│   ├── mailer.js            # Kirim email approval via Gmail
│   └── healthChecks.js       # Deep health check (Desklib, GCS)
├── providers/                # Handler tiap AI detector
│   ├── desklib.js
│   ├── gptzero.js
│   ├── zerogpt.js
│   ├── watsonx.js
│   └── hix.js
├── scripts/
│   └── generate-license.js   # CLI generate lisensi manual
└── public/                    # Static assets (taskpane, admin dashboard)
```

### 8. 🐳 Deploy Sendiri (Cloud Run)
```bash
gcloud run deploy ai-alibi-backend \
  --source . \
  --region asia-southeast2 \
  --allow-unauthenticated
```

Environment variable & secret dikelola lewat Google Secret Manager — lihat `server/.env.example` untuk daftar lengkap variable yang dibutuhkan (`ZEROGPT_API_KEY`, `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `GMAIL_APP_PASSWORD`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `API_KEY`, dll).

---

## 👥 Tim

Dibangun oleh tim 5 orang lintas disiplin (AI, Industrial, Electrical Engineering) untuk AI Builders Challenge.
