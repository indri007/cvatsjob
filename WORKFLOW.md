# 🔄 Workflow — JobMatch AI

Dokumen ini menjelaskan alur kerja sistem end-to-end: baik alur otomatis (auto-fetch lowongan harian) maupun alur interaktif (perjalanan pengguna lewat 5 step wizard).

> **Catatan soal n8n:** requirement resmi final project (`rule/[JCAI - 2025] Final Project - N8N Version.docx`) mengacu ke versi berbasis n8n. Implementasi **production** saat ini **tidak** memakai n8n sebagai orchestrator — otomasi harian digantikan dengan **Google Cloud Scheduler + Cloud Run Job**, dan agent AI diimplementasikan sebagai modul Python (`agents/`) alih-alih node n8n. Namun, tiga workflow n8n asli tetap disertakan di folder [`n8n_workflows/`](./n8n_workflows/) sebagai referensi/prototipe sesuai requirement resmi — diagramnya ada di bagian § 0 di bawah.

---

## 0. Workflow n8n (Referensi Requirement Resmi)

File export asli ada di [`n8n_workflows/`](./n8n_workflows/). Diagram di bawah di-generate otomatis dari file JSON tersebut (lihat `n8n_to_mermaid.py`). Garis putus-putus (`-.label.->`) menandakan koneksi sub-komponen AI (language model, tool, vector store, embedding) — bukan alur eksekusi utama.

### 0.1 `1_cv_job_matcher.json` — CV & Job Matcher (sederhana)

```mermaid
flowchart LR
    Webhook["Webhook<br/><i>webhook</i>"]
    OpenAI_Chat["OpenAI Chat<br/><i>openAi</i>"]
    Respond_to_Webhook["Respond to Webhook<br/><i>respondToWebhook</i>"]
    Webhook --> OpenAI_Chat
    OpenAI_Chat --> Respond_to_Webhook
```

Alur paling sederhana: webhook menerima request → diproses langsung oleh OpenAI Chat → hasil dikembalikan lewat Respond to Webhook.

### 0.2 `AI_Job_Assistant_3_ (1).json` / `AI Job Assistant(3).json` — AI Agent dengan RAG + SQL Tool

*(kedua file punya struktur workflow yang identik)*

```mermaid
flowchart LR
    Webhook["Webhook<br/><i>webhook</i>"]
    AI_Agent["AI Agent<br/><i>agent</i>"]
    Groq_Chat_Model["Groq Chat Model<br/><i>lmChatGroq</i>"]
    Vector_Store_Tool["Vector Store Tool<br/><i>toolVectorStore</i>"]
    Qdrant_Vector_Store["Qdrant Vector Store<br/><i>vectorStoreQdrant</i>"]
    Cohere_Embeddings["Cohere Embeddings<br/><i>embeddingsCohere</i>"]
    Execute_a_SQL_query_in_MySQL["Execute a SQL query in MySQL<br/><i>mySqlTool</i>"]
    OpenAI_Chat_Model["OpenAI Chat Model<br/><i>lmChatOpenAi</i>"]
    Webhook --> AI_Agent
    Vector_Store_Tool -.tool.-> AI_Agent
    Qdrant_Vector_Store -.vectorStore.-> Vector_Store_Tool
    Cohere_Embeddings -.embedding.-> Qdrant_Vector_Store
    Execute_a_SQL_query_in_MySQL -.tool.-> AI_Agent
    OpenAI_Chat_Model -.languageModel.-> AI_Agent
    OpenAI_Chat_Model -.languageModel.-> Vector_Store_Tool
```

Alur: webhook memicu **AI Agent**, yang punya akses ke tiga tool —
- **Vector Store Tool** (semantic search lewat Qdrant, dengan Cohere sebagai embedding model)
- **SQL Tool** (query langsung ke MySQL)
- **OpenAI Chat Model** sebagai language model utama untuk reasoning agent

> Catatan: node **Groq Chat Model** ada di file tapi tidak terhubung ke node manapun — kemungkinan alternatif LLM yang belum diaktifkan/di-switch di workflow ini.

Pemetaan ke implementasi Python saat ini: kombinasi Vector Store Tool + SQL Tool + Agent ini setara dengan `rag_agent.py` + `sql_agent.py` yang dipanggil dari `step_b_jobs.py` (lihat § 2 di bawah).

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
