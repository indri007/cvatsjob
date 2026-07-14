"""
auth_setup.py — Login dengan Google Account untuk Streamlit (Cloud Run friendly)
"""

import os
import streamlit as st
from streamlit.runtime.secrets import secrets_singleton

_GOOGLE_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"


def _inject_auth_secrets():
    redirect_uri = os.environ.get("AUTH_REDIRECT_URI", "")
    cookie_secret = os.environ.get("AUTH_COOKIE_SECRET", "")
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    missing = [
        name
        for name, val in [
            ("AUTH_REDIRECT_URI", redirect_uri),
            ("AUTH_COOKIE_SECRET", cookie_secret),
            ("GOOGLE_CLIENT_ID", client_id),
            ("GOOGLE_CLIENT_SECRET", client_secret),
        ]
        if not val
    ]
    if missing:
        return False, missing

    secrets_singleton._secrets = {
        "auth": {
            "redirect_uri": redirect_uri,
            "cookie_secret": cookie_secret,
            "client_id": client_id,
            "client_secret": client_secret,
            "server_metadata_url": _GOOGLE_METADATA_URL,
        }
    }
    return True, []


def require_google_login():
    ok, missing = _inject_auth_secrets()

    if not ok:
        st.error(
            "⚠️ Konfigurasi Google Login belum lengkap. "
            f"Environment variable berikut belum diisi: {', '.join(missing)}"
        )
        st.stop()

    if not st.user.is_logged_in:
        st.markdown(
            """
            <div class="jm-landing">
                <div class="jm-landing-grid">
                    <div>
                        <div class="jm-landing-brand">
                            <div class="jm-landing-brand-icon">💼</div>
                            <span class="jm-landing-brand-text">JobMatch AI</span>
                        </div>
                        <h1>Lowongan impianmu,<br>tinggal selangkah<br>dari CV-mu.</h1>
                        <p class="jm-landing-sub">
                            Upload CV kamu dan biarkan AI membantu mencari lowongan
                            yang cocok, meninjau CV, dan berlatih interview -
                            semua dalam satu aplikasi.
                        </p>
                        <div class="jm-landing-stats">
                            <div>
                                <p class="jm-landing-stat-num">500+</p>
                                <p class="jm-landing-stat-label">Lowongan kerja Indonesia</p>
                            </div>
                            <div>
                                <p class="jm-landing-stat-num">5</p>
                                <p class="jm-landing-stat-label">Fitur berbasis AI</p>
                            </div>
                        </div>
                    </div>
                    <div class="jm-landing-features">
                        <div class="jm-feature-card">
                            <div class="jm-feature-icon">📄</div>
                            <div>
                                <p class="jm-feature-title">Review CV & Skor ATS</p>
                                <p class="jm-feature-desc">Feedback langsung, generate & download CV ATS-friendly dalam Bahasa Indonesia atau Inggris, menyesuaikan bahasa CV asli kamu.</p>
                            </div>
                        </div>
                        <div class="jm-feature-card">
                            <div class="jm-feature-icon">🎯</div>
                            <div>
                                <p class="jm-feature-title">Rekomendasi Lowongan</p>
                                <p class="jm-feature-desc">Pencocokan semantik dari ratusan lowongan kerja Indonesia.</p>
                            </div>
                        </div>
                        <div class="jm-feature-card">
                            <div class="jm-feature-icon">🎤</div>
                            <div>
                                <p class="jm-feature-title">Mock Interview AI</p>
                                <p class="jm-feature-desc">Simulasi wawancara kerja, mode text maupun voice.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Masuk dengan Google", use_container_width=True, type="primary", icon=":material/login:"):
                st.login()
        st.markdown(
            """
            <div class="jm-landing-stripe">
                <div class="jm-landing-stripe-item">Login aman dengan <b>Google OAuth</b></div>
                <div class="jm-landing-stripe-item">Ditenagai <b>Gemini AI</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()


def show_user_badge_and_logout(location="sidebar"):
    target = st.sidebar if location == "sidebar" else st
    with target:
        name = getattr(st.user, "name", None) or getattr(st.user, "email", "User")
        picture = getattr(st.user, "picture", None)
        if picture:
            target.markdown(
                f"""
                <div class="gauth-avatar-wrap">
                    <img class="gauth-avatar-img" src="{picture}" />
                    <span class="gauth-avatar-name">👋 {name}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            target.markdown(f"**👋 {name}**")
        if target.button("Logout", key="btn_logout_google"):
            st.logout()
