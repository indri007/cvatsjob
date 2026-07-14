# 🎯 JobMatch AI — CV Review & Job Recommendation App

AI-powered web application untuk membantu pencarian kerja di Indonesia. Upload CV kamu dan dapatkan rekomendasi lowongan, review CV, konsultasi karir, dan mock interview — semua berbasis AI.

Project ini dikembangkan untuk Final Project **JCAI (Job Connector AI Engineering) — Purwadhika Digital Technology School**.

## 🌐 Live Demo

**[https://job-search-app-994794168239.asia-southeast2.run.app](https://job-search-app-994794168239.asia-southeast2.run.app)**

## ✨ Fitur

- 🔐 **Login Google** — Autentikasi via Google OAuth sebelum mengakses aplikasi
- 📄 **Upload CV** — Mendukung format PDF & Word, maksimal 100MB
- 💼 **Rekomendasi Lowongan** — AI mencocokkan CV dengan database lowongan kerja Indonesia via Qdrant Vector Search (semantic search)
- 🔍 **Cari Lowongan Real-time** — Scraping langsung dari JobStreet (Selenium) untuk pencarian manual
- ✍️ **Review CV** — Analisis ATS score, feedback, dan generate CV versi ATS-friendly
- 💬 **Konsultasi Karir** — Chat dengan AI career consultant berbasis Gemini
- 🎤 **Mock Interview** — Simulasi wawancara kerja dengan AI interviewer (text & voice)
- 🔄 **Auto-fetch Lowongan Harian** — Cloud Scheduler menjalankan pengambilan 5 lowongan baru setiap hari dari JSearch API (RapidAPI), merotasi 10 kategori pekerjaan teratas
- 📊 **Observability** — Structured logging (Cloud Logging), health checks, error tracking (Sentry)

## 🛠️ Tech Stack

| Layer | Teknologi |
|---|---|
| Frontend | Streamlit |
| Autentikasi | Google OAuth 2.0 |
| AI/LLM | Google Gemini 2.5 Flash (utama), OpenAI (fallback embedding) |
| Vector Store | Qdrant Cloud (semantic search) |
| Database | Aiven MySQL (SQLAlchemy) |
| Job Data (real-time) | Selenium + BeautifulSoup (JobStreet scraper) |
| Job Data (otomatis harian) | JSearch API via RapidAPI |
| Scheduler | Google Cloud Scheduler |
| Deployment | Google Cloud Run (service + job), asia-southeast2 |
| Observability | Sentry, structured JSON logging, Cloud Run health checks |

## 🏗️ Arsitektur

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Cloud Scheduler │ ───▶ │  Cloud Run Job    │ ───▶ │  JSearch    │
│  (jam 9 pagi WIB)│      │  daily-job-fetch  │      │  API        │
└─────────────────┘      └─────────┬─────────┘      └─────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │   Aiven MySQL (SQL)      │
                      │   Qdrant Cloud (Vector)  │
                      └────────────┬─────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │  Cloud Run Service        │
                      │  job-search-app (Streamlit)│
                      │  ← Google OAuth Login      │
                      └─────────────────────────┘
```

## 🚀 Deployment

Aplikasi terdiri dari dua komponen Cloud Run:

**1. Service utama (Streamlit UI)**
```
Service: job-search-app
Region:  asia-southeast2 (Jakarta)
URL:     https://job-search-app-994794168239.asia-southeast2.run.app
```

**2. Cloud Run Job (auto-fetch harian)**
```
Job:       daily-job-fetch
Region:    asia-southeast2
Trigger:   Cloud Scheduler, cron "0 9 * * *" (Asia/Jakarta)
```

Deploy ulang service utama:
```bash
gcloud run deploy job-search-app \
  --source . \
  --region=asia-southeast2 \
  --project=heaven-493814
```

Deploy ulang Cloud Run Job:
```bash
gcloud run jobs deploy daily-job-fetch \
  --source . \
  --region=asia-southeast2 \
  --project=heaven-493814 \
  --command="python3" \
  --args="daily_fetch.py"
```

## ⚙️ Setup Lokal

1. Clone repository ini
2. Copy `.env.example` menjadi `.env` dan isi dengan credentials kamu
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```

Untuk setup database Aiven MySQL, lihat [`AIVEN_SETUP.md`](./AIVEN_SETUP.md).

## 📋 Environment Variables

Di production, semua variabel di bawah disimpan di **Google Secret Manager** (bukan file `.env`). Untuk development lokal, lihat `.env.example`.

| Variabel | Keterangan |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API Key (LLM utama + embedding) |
| `OPENAI_API_KEY` | OpenAI API Key (fallback embedding jika Gemini quota habis) |
| `DATABASE_URL` | Aiven MySQL connection string |
| `QDRANT_URL` / `QDRANT_API_KEY` | Qdrant Cloud credentials |
| `VECTOR_STORE` | `qdrant` atau `chromadb` |
| `EMBEDDING_MODEL` | Model embedding yang dipakai |
| `AUTH_REDIRECT_URI` / `AUTH_COOKIE_SECRET` | Konfigurasi Google OAuth login |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Kredensial OAuth dari Google Cloud Console |
| `RAPIDAPI_KEY` / `RAPIDAPI_KEY_BACKUP` | Key JSearch API untuk auto-fetch lowongan harian |
| `SENTRY_DSN` | Error tracking (opsional) |
| `ENVIRONMENT` | `production` / `development` |

## 📁 Struktur Project

```
├── app.py                  # Entry point Streamlit — auth, routing, dispatch
├── pages/                  # Modul UI per step wizard (A–E)
├── config.py                # Konfigurasi terpusat (env vars, clients)
├── database.py               # SQLAlchemy models & query (Aiven MySQL)
├── vector_store.py            # Qdrant/ChromaDB manager + embedding (Gemini/OpenAI)
├── scraper.py                # Scraper JobStreet real-time (Selenium)
├── jsearch_client.py          # Client JSearch API (auto-fetch harian)
├── daily_fetch.py             # Entry point Cloud Run Job harian
├── cv_processor.py            # Ekstraksi teks CV (PDF/Word)
├── auth_setup.py              # Google OAuth login
├── logger.py / metrics.py     # Structured logging & metrics
├── health_check.py / health_server.py  # Health check endpoint
└── rule/                      # Dokumen requirement resmi dari tutor
```

## ⚠️ Known Issues

- Google OAuth login: sedang dalam perbaikan (`client_secret` perlu di-refresh secara berkala di Google Cloud Console).

## 📚 Referensi Requirement

Requirement resmi final project dari tutor tersedia di folder [`rule/`](./rule/).
