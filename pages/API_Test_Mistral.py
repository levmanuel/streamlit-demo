import time

import requests
import streamlit as st

st.set_page_config(page_title="Diagnostic API Mistral", page_icon="🔧")

st.title("🔧 Diagnostic API Mistral")
st.caption(
    "Appels bruts, **sans retry**, pour diagnostiquer précisément une erreur 401/403/429 : "
    "statut HTTP, en-têtes complets et corps de la réponse."
)

MISTRAL_API_KEY = st.secrets["api"]["MISTRAL_API_KEY"]
HEADERS = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}

if len(MISTRAL_API_KEY) > 8:
    masked = f"{MISTRAL_API_KEY[:4]}…{MISTRAL_API_KEY[-4:]}"
else:
    masked = "(clé anormalement courte)"
st.write(f"Clé chargée : `{masked}` — {len(MISTRAL_API_KEY)} caractères")


def _interpret(status: int, headers: dict) -> None:
    if status == 200:
        st.success("200 OK — la requête a réussi.")
    elif status == 401:
        st.error("401 — clé API invalide, absente ou mal formée.")
    elif status == 403:
        st.error("403 — clé valide mais accès refusé à cette ressource/modèle (plan insuffisant).")
    elif status == 429:
        st.error("429 — rate limit ou quota dépassé.")
        retry_after = headers.get("Retry-After") or headers.get("retry-after")
        if retry_after:
            st.info(f"En-tête Retry-After : {retry_after}s")
        quota_headers = {k: v for k, v in headers.items() if "quota" in k.lower() or "limit" in k.lower() or "ratelimit" in k.lower()}
        if quota_headers:
            st.json(quota_headers)
        else:
            st.caption("Aucun en-tête de quota/rate-limit explicite dans la réponse — voir le corps ci-dessous.")
    else:
        st.warning(f"Statut inattendu : {status}")


def _show_response(resp: requests.Response, elapsed: float) -> None:
    st.write(f"Statut : **{resp.status_code}** — {elapsed:.2f}s")
    _interpret(resp.status_code, dict(resp.headers))
    st.subheader("En-têtes de réponse")
    st.json(dict(resp.headers))
    st.subheader("Corps de la réponse")
    try:
        st.json(resp.json())
    except ValueError:
        st.code(resp.text or "(corps vide)")


st.divider()
st.subheader("Test 1 — GET /v1/models")
st.caption("Liste les modèles accessibles avec cette clé. Ne consomme pas de tokens.")
if st.button("Lancer le test 1"):
    start = time.time()
    resp = requests.get("https://api.mistral.ai/v1/models", headers=HEADERS, timeout=15)
    _show_response(resp, time.time() - start)

st.divider()
st.subheader("Test 2 — POST /v1/chat/completions")
st.caption(
    "Un seul appel minimal (5 tokens max), sans retry. Différents modèles peuvent avoir des "
    "limites très différentes sur le tier gratuit — teste plusieurs valeurs si besoin."
)
chat_model = st.text_input("Modèle à tester", value="ministral-3b-latest", key="chat_model")
if st.button("Lancer le test 2"):
    start = time.time()
    resp = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers=HEADERS,
        json={
            "model": chat_model,
            "messages": [{"role": "user", "content": "Réponds juste 'ok'."}],
            "max_tokens": 5,
        },
        timeout=15,
    )
    _show_response(resp, time.time() - start)

st.divider()
st.subheader("Test 3 — POST /v1/embeddings")
st.caption("Un seul appel minimal, sans retry, sur mistral-embed (utilisé par la page Chat RAG).")
embed_model = st.text_input("Modèle à tester", value="mistral-embed", key="embed_model")
if st.button("Lancer le test 3"):
    start = time.time()
    resp = requests.post(
        "https://api.mistral.ai/v1/embeddings",
        headers=HEADERS,
        json={"model": embed_model, "input": ["test"]},
        timeout=15,
    )
    _show_response(resp, time.time() - start)
