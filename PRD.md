# 📋 Product Requirements Document (PRD) — JobMatch AI

## 1. Ringkasan Produk

**Nama Produk:** JobMatch AI — CV Review & Job Recommendation App
**Konteks:** Final Project JCAI (Job Connector AI Engineering) — Purwadhika Digital Technology School
**Live Demo:** https://job-search-app-994794168239.asia-southeast2.run.app

JobMatch AI adalah aplikasi web berbasis AI yang membantu pencari kerja di Indonesia melalui satu alur terpadu: mencocokkan CV dengan lowongan yang relevan, memberi review CV berbasis ATS, konsultasi karir, dan simulasi wawancara kerja.

---

## 2. Latar Belakang & Masalah

Pencari kerja umumnya menghadapi beberapa hambatan:
- Kesulitan menemukan lowongan yang benar-benar relevan dengan profil/CV mereka di antara ribuan listing.
- CV yang tidak dioptimalkan untuk sistem ATS (Applicant Tracking System) sehingga tidak lolos seleksi otomatis.
- Minimnya akses ke konsultasi karir yang terjangkau dan cepat.
- Kurangnya kesempatan berlatih wawancara sebelum wawancara sesungguhnya.

## 3. Tujuan Produk

- Mempercepat proses pencarian kerja dengan rekomendasi lowongan berbasis semantic matching, bukan hanya keyword matching.
- Meningkatkan peluang lolos seleksi awal (ATS) lewat review dan optimasi CV otomatis.
- Menyediakan konsultasi karir dan simulasi wawancara berbasis AI yang bisa diakses kapan saja.

## 4. Target Pengguna

- Pencari kerja aktif di Indonesia (fresh graduate hingga profesional berpengalaman).
- Pengguna yang ingin mengevaluasi/optimasi CV sebelum melamar.
- Pengguna yang butuh latihan wawancara mandiri sebelum wawancara sesungguhnya.

## 5. Ruang Lingkup (Scope)

### 5.1 Dalam Scope (fitur yang sudah diimplementasikan)

| Fitur | Deskripsi |
|---|---|
| Login Google OAuth | Autentikasi pengguna sebelum masuk aplikasi |
| Upload CV | Mendukung PDF & Word, maksimal 100MB |
| Rekomendasi lowongan (semantic search) | Pencocokan CV ↔ lowongan via Qdrant Vector Search |
| Pencarian lowongan real-time | Scraping JobStreet on-demand (Selenium) |
| Review CV & ATS scoring | Analisis, feedback, dan generate ulang CV ATS-friendly |
| Konsultasi karir | Chat dengan AI career consultant (Gemini) |
| Mock interview | Simulasi wawancara teks & suara |
| Auto-fetch lowongan harian | Cloud Scheduler + Cloud Run Job, 5 lowongan/kategori, 10 kategori teratas |
| Observability | Structured logging, health check, Sentry error tracking |

### 5.2 Di Luar Scope (saat ini)

- Orkestrasi via n8n (requirement asli final project mengacu ke versi n8n; implementasi saat ini memakai Cloud Scheduler + Cloud Run Job + agent Python sebagai gantinya — lihat `WORKFLOW.md`).
- Aplikasi mobile native.
- Multi-bahasa (saat ini UI & AI berbahasa Indonesia).
- Integrasi job board selain JobStreet & JSearch API.

## 6. Alur Pengguna Utama (User Flow)

Lihat detail lengkap di [`WORKFLOW.md`](./WORKFLOW.md). Ringkasan:

1. Login via Google OAuth
2. Upload CV (Step A)
3. Terima rekomendasi lowongan / cari manual (Step B)
4. Review CV & ATS score (Step C)
5. Konsultasi karir dengan AI (Step D)
6. Mock interview dengan AI (Step E)

## 7. Requirement Non-Fungsional

| Aspek | Requirement |
|---|---|
| Performa | Rekomendasi lowongan & respons chat AI harus terasa near real-time (mengandalkan Gemini 2.5 Flash untuk latensi rendah) |
| Keamanan | Semua credential (API key, DB password) disimpan di Google Secret Manager di production, tidak pernah di-commit ke repo |
| Observability | Setiap request penting harus tercatat di structured log; error harus tertangkap di Sentry |
| Ketersediaan | Health check endpoint aktif untuk memastikan Cloud Run service tetap sehat |
| Skalabilitas | Deployment berbasis Cloud Run agar bisa auto-scale sesuai trafik |

## 8. Metrik Keberhasilan (Success Metrics)

- Tingkat kecocokan rekomendasi lowongan (relevansi hasil semantic search terhadap CV pengguna).
- Peningkatan ATS score rata-rata setelah pengguna menggunakan fitur Review CV.
- Jumlah sesi mock interview yang diselesaikan pengguna.
- Uptime service (dari health check & Cloud Logging).
- Keberhasilan job auto-fetch harian (jumlah lowongan baru yang berhasil masuk tanpa error).

## 9. Risiko & Known Issues

| Risiko | Status/Mitigasi |
|---|---|
| Google OAuth `client_secret` perlu di-refresh berkala | Sedang dalam perbaikan (lihat README § Known Issues) |
| Ketergantungan pada kuota API eksternal (Gemini, RapidAPI) | Ada fallback embedding ke OpenAI jika kuota Gemini habis |
| Scraping JobStreet rentan berubah jika struktur halaman berubah | Perlu monitoring berkala pada `scraper.py` |
| Kebocoran credential lewat commit tidak sengaja | `.gitignore` diperketat; kebijakan revoke/reset key segera jika ter-expose |

## 10. Referensi

- Requirement resmi tutor: [`rule/Features.txt`](./rule/Features.txt), [`rule/[JCAI - 2025] Final Project - N8N Version.docx`](./rule/), [`rule/Rubrik Penilaian Final Project JCAI.docx`](./rule/)
- Alur teknis end-to-end: [`WORKFLOW.md`](./WORKFLOW.md)
- Panduan fitur & instalasi: [`README.md`](./README.md)
