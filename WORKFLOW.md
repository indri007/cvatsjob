# 🔄 Workflow — JobMatch AI

Dokumen ini menjelaskan alur kerja sistem end-to-end: baik alur otomatis (auto-fetch lowongan harian) maupun alur interaktif (perjalanan pengguna lewat 5 step wizard).

> **Catatan soal n8n:** requirement resmi final project (`rule/[JCAI - 2025] Final Project - N8N Version.docx`) mengacu ke versi berbasis n8n. Implementasi saat ini **tidak** memakai n8n sebagai orchestrator — otomasi harian digantikan dengan **Google Cloud Scheduler + Cloud Run Job**, dan agent AI diimplementasikan sebagai modul Python (`agents/`) alih-alih node n8n. Diagram di bawah menggambarkan node-node fungsional dengan gaya yang sama seperti workflow n8n (trigger → proses → output), supaya tetap mudah dipetakan ke versi n8n bila suatu saat migrasi dilakukan.

---

## 1. Workflow Otomatis — Auto-fetch Lowongan Harian

```mermaid
flowchart LR
    A[⏰ Cloud Scheduler<br/>cron 09:00 WIB] --> B[▶️ Cloud Run Job<br/>daily-job-fetch]
    B --> C[🔌 JSearch API<br/>via RapidAPI]
    C --> D{Rotasi 10 kategori<br/>pekerjaan teratas}
    D --> E[📥 Ambil 5 lowongan baru<br/>per kategori]
    E --> F[(Aiven MySQL<br/>simpan data lowongan)]
    E --> G[Generate embedding<br/>Gemini/OpenAI]
    G --> H[(Qdrant Cloud<br/>simpan vector)]
    F --> I[✅ Log hasil<br/>Cloud Logging]
    H --> I
```

**Node breakdown:**

| Node | Fungsi | File terkait |
|---|---|---|
| Trigger: Cloud Scheduler | Memicu job setiap hari jam 09:00 WIB | — (konfigurasi GCP) |
| Cloud Run Job | Entry point eksekusi fetch harian | `daily_fetch.py` |
| JSearch API Client | Ambil data lowongan dari RapidAPI | `jsearch_client.py` |
| Simpan ke MySQL | Persist data lowongan terstruktur | `database.py` |
| Generate Embedding | Ubah teks lowongan jadi vector untuk semantic search | `vector_store.py` |
| Simpan ke Qdrant | Persist vector untuk pencarian semantik | `vector_store.py` |
| Logging | Catat hasil run (jumlah lowongan baru, error, dsb) | `logger.py` |

---

## 2. Workflow Interaktif — Perjalanan Pengguna (Step A–E)

```mermaid
flowchart TD
    Login[🔐 Login Google OAuth] --> A[Step A: Upload CV<br/>PDF/Word, maks 100MB]
    A --> Extract[cv_processor.py<br/>ekstraksi teks CV]
    Extract --> B[Step B: Rekomendasi Lowongan]
    B --> Semantic[rag_agent.py<br/>semantic search di Qdrant]
    B --> Manual[scraper.py<br/>cari manual di JobStreet]
    Semantic --> C[Step C: Review CV]
    Manual --> C
    C --> Analyze[cv_analyzer_agent.py<br/>hitung ATS score + feedback]
    Analyze --> D[Step D: Konsultasi Karir]
    D --> Career[career_agent.py<br/>chat dengan AI consultant]
    Career --> E[Step E: Mock Interview]
    E --> Interview[interview_agent.py<br/>simulasi wawancara teks/suara]
```

**Node breakdown:**

| Step | Fungsi | Agent/Modul |
|---|---|---|
| A — Input CV | Upload & validasi file CV | `step_a_input_cv.py`, `cv_processor.py` |
| B — Rekomendasi Lowongan | Cocokkan CV dengan lowongan (semantic + manual) | `step_b_jobs.py`, `rag_agent.py`, `scraper.py` |
| C — Review CV | Analisis ATS score, feedback, generate versi baru | `step_c_review.py`, `cv_analyzer_agent.py` |
| D — Konsultasi Karir | Chat interaktif seputar strategi karir | `step_d_consultation.py`, `career_agent.py` |
| E — Mock Interview | Simulasi wawancara kerja | `step_e_interview.py`, `interview_agent.py` |

---

## 3. Arsitektur Sistem Keseluruhan

```mermaid
flowchart TB
    subgraph Otomatis
        Sched[Cloud Scheduler] --> Job[Cloud Run Job:<br/>daily-job-fetch]
        Job --> JSearch[JSearch API]
    end

    subgraph Data Layer
        MySQL[(Aiven MySQL)]
        Qdrant[(Qdrant Cloud)]
    end

    subgraph Interaktif
        User((Pengguna)) --> OAuth[Google OAuth]
        OAuth --> App[Cloud Run Service:<br/>job-search-app / Streamlit]
        App --> Agents[agents/*.py<br/>Gemini + OpenAI fallback]
    end

    Job --> MySQL
    Job --> Qdrant
    Agents --> MySQL
    Agents --> Qdrant

    App --> Sentry[Sentry<br/>error tracking]
    App --> CloudLogging[Cloud Logging]
```

---

## 4. Catatan Observability

- **Health check**: `health_check.py` / `health_server.py` menyediakan endpoint yang dicek Cloud Run untuk memastikan service hidup.
- **Logging**: `logger.py` dan `metrics.py` mengirim structured JSON log ke Cloud Logging.
- **Error tracking**: Sentry aktif jika `SENTRY_DSN` diset.
