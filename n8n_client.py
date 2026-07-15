"""
N8N Client — wrapper HTTP untuk memanggil workflow AI Job Assistant yang
di-deploy di N8N (Agent Utama + Agent RAG/Qdrant + Agent SQL/MySQL),
diekspos sebagai REST API lewat webhook.

Konsisten dengan pola client lain di project ini (lihat jsearch_client.py).
"""

import requests
import config

TIMEOUT_SECONDS = 30


def ask_n8n_agent(query: str) -> dict:
    """
    Kirim pertanyaan ke AI Job Assistant workflow di N8N.

    Args:
        query: Pertanyaan user dalam bahasa natural (contoh: "Ada lowongan
               data analyst di Jakarta dengan gaji di atas 8 juta?")

    Returns dict dengan:
    - "answer": teks jawaban dari AI Agent (str atau None kalau gagal)
    - "available": bool, apakah N8N_WEBHOOK_URL sudah dikonfigurasi
    - "error": pesan error kalau ada masalah (None kalau sukses)
    """
    if not config.is_n8n_configured():
        return {"answer": None, "available": False, "error": None}

    try:
        response = requests.post(
            config.N8N_WEBHOOK_URL,
            json={"query": query},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("output") or data.get("answer") or data.get("response")
        if answer is None:
            return {
                "answer": None,
                "available": True,
                "error": f"Format respons N8N tidak dikenali: {data}",
            }
        return {"answer": answer, "available": True, "error": None}

    except requests.exceptions.Timeout:
        return {
            "answer": None,
            "available": True,
            "error": "N8N tidak merespons dalam waktu yang wajar. Coba lagi sebentar.",
        }
    except requests.exceptions.ConnectionError:
        return {
            "answer": None,
            "available": True,
            "error": "Tidak bisa terhubung ke N8N. Pastikan workflow sedang aktif.",
        }
    except requests.exceptions.HTTPError as e:
        return {
            "answer": None,
            "available": True,
            "error": f"N8N mengembalikan error: {e}",
        }
    except Exception as e:
        return {"answer": None, "available": True, "error": f"Error tidak terduga: {e}"}
