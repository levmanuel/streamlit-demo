import pandas as pd
import streamlit as st
from sqlalchemy import text

st.set_page_config(page_title="Mon Bar à Cocktails", page_icon="🍸")

_COCKTAILS_DEFAUT = {
    'Vodka Orange': ["vodka", "orange(jus)"],
    'Vodka Martini': ["vodka", "martini"],
    'Mojito': ['menthe', 'rhum', 'sucre'],
    'Acapulco': ['tequila', 'rhum', 'ananas', 'pamplemouse'],
    'American Beauty': ['cognac', 'vermouth', 'orange', 'grenadine', 'creme menthe blanche', 'porto'],
    'Americano': ['vermouth rouge', 'campari', 'eau gazeuze'],
    'Bacardi': ['rhum doux', 'jus de citron', 'grenadine (sirop)'],
    'Bahamas': ['rhum doux', 'Southern Confort', 'jus de citron', 'banane (creme)'],
    'Bellini': ['pêche', 'champagne'],
    'Bloody Mary': ['vodka', 'jus de tomate', 'sauce worcestershire', 'tabasco', 'sel de céleri', 'branche de céleri'],
    'Blue Lagon': ['vodka', 'curaçao bleu', 'citron (jus)'],
    'Between the sheets': ['cognac', 'rhum', 'cointreau', 'orange(jus)'],
}

_BAR_DEFAUT = ["vodka", "orange(jus)", "coca", "menthe", "martini", "rhum"]


def _init_db(conn) -> None:
    with conn.session as session:
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS bar_ingredients (
                ingredient TEXT PRIMARY KEY
            )
        """))
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS cocktails (
                name TEXT PRIMARY KEY
            )
        """))
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS cocktail_ingredients (
                cocktail_name TEXT,
                ingredient    TEXT,
                PRIMARY KEY (cocktail_name, ingredient)
            )
        """))
        count = session.execute(text("SELECT COUNT(*) FROM cocktails")).scalar()
        if count == 0:
            for ing in _BAR_DEFAUT:
                session.execute(text("INSERT OR IGNORE INTO bar_ingredients VALUES (:ing)"), {"ing": ing})
            for name, ingredients in _COCKTAILS_DEFAUT.items():
                session.execute(text("INSERT OR IGNORE INTO cocktails VALUES (:name)"), {"name": name})
                for ing in ingredients:
                    session.execute(
                        text("INSERT OR IGNORE INTO cocktail_ingredients VALUES (:name, :ing)"),
                        {"name": name, "ing": ing},
                    )
        session.commit()


@st.cache_resource
def get_conn():
    conn = st.connection("cocktail_db", type="sql", url="sqlite:///cocktail.db")
    _init_db(conn)
    return conn


conn = get_conn()

# ── Sidebar — gestion du bar ──────────────────────────────────────

st.sidebar.title("Gestion du Bar")

with st.sidebar.form("form_ajout_ingredient"):
    nouvel_ingredient = st.text_input("Nouvel ingrédient :")
    if st.form_submit_button("Ajouter au bar") and nouvel_ingredient.strip():
        with conn.session as session:
            session.execute(
                text("INSERT OR IGNORE INTO bar_ingredients VALUES (:ing)"),
                {"ing": nouvel_ingredient.strip().lower()},
            )
            session.commit()
        st.success(f"✅ {nouvel_ingredient} ajouté !")
        st.rerun()

st.sidebar.subheader("Ingrédients disponibles")
bar_df = conn.query("SELECT ingredient FROM bar_ingredients ORDER BY ingredient", ttl=0)
bar_ingredients = bar_df["ingredient"].tolist()

with st.sidebar.form("form_suppression"):
    a_supprimer = st.multiselect("Sélectionner pour supprimer", bar_ingredients)
    if st.form_submit_button("Supprimer la sélection") and a_supprimer:
        with conn.session as session:
            for ing in a_supprimer:
                session.execute(
                    text("DELETE FROM bar_ingredients WHERE ingredient = :ing"), {"ing": ing}
                )
            session.commit()
        st.success("✅ Ingrédients supprimés !")
        st.rerun()

# ── Page principale ───────────────────────────────────────────────

st.title("🍸 Mon Bar à Cocktails")
st.caption("Stockage persistant via **SQLite** — `st.connection(type='sql')`, `conn.query()`, `conn.session`")

st.subheader("Cocktails réalisables avec vos ingrédients")

seuil = st.slider("Seuil minimum de matching (%)", 0, 100, 50)

matching_sql = """
SELECT
    c.name AS Cocktail,
    COUNT(ci.ingredient)                                                                          AS total,
    COUNT(CASE WHEN ci.ingredient IN (SELECT ingredient FROM bar_ingredients) THEN 1 END)        AS matched,
    ROUND(
        100.0 * COUNT(CASE WHEN ci.ingredient IN (SELECT ingredient FROM bar_ingredients) THEN 1 END)
        / COUNT(ci.ingredient),
        1
    ) AS pct
FROM cocktails c
JOIN cocktail_ingredients ci ON c.name = ci.cocktail_name
GROUP BY c.name
HAVING pct >= :seuil
ORDER BY pct DESC, c.name
"""
resultats = conn.query(matching_sql, params={"seuil": seuil}, ttl=0)

if resultats.empty:
    st.info("Aucun cocktail ne correspond au seuil sélectionné.")
else:
    # Ajouter la colonne ingrédients manquants
    def manquants(name):
        df = conn.query(
            """
            SELECT ingredient FROM cocktail_ingredients
            WHERE cocktail_name = :name
              AND ingredient NOT IN (SELECT ingredient FROM bar_ingredients)
            """,
            params={"name": name},
            ttl=0,
        )
        return ", ".join(df["ingredient"].tolist()) if not df.empty else "—"

    resultats["Matching (%)"] = resultats["pct"].astype(str) + " %"
    resultats["Ingrédients manquants"] = resultats["Cocktail"].apply(manquants)
    st.dataframe(
        resultats[["Cocktail", "Matching (%)", "matched", "total", "Ingrédients manquants"]].rename(
            columns={"matched": "Présents", "total": "Total"}
        ),
        use_container_width=True,
        hide_index=True,
    )

# ── Ajout d'un nouveau cocktail ───────────────────────────────────

with st.expander("Ajouter un nouveau cocktail"):
    with st.form("form_nouveau_cocktail"):
        col1, col2 = st.columns(2)
        with col1:
            nouveau_nom = st.text_input("Nom du cocktail :")
        with col2:
            ingredients_str = st.text_input("Ingrédients (séparés par des virgules) :")
        if st.form_submit_button("Ajouter le cocktail") and nouveau_nom.strip() and ingredients_str.strip():
            ings = [i.strip().lower() for i in ingredients_str.split(",") if i.strip()]
            with conn.session as session:
                session.execute(
                    text("INSERT OR IGNORE INTO cocktails VALUES (:name)"), {"name": nouveau_nom.strip()}
                )
                for ing in ings:
                    session.execute(
                        text("INSERT OR IGNORE INTO cocktail_ingredients VALUES (:name, :ing)"),
                        {"name": nouveau_nom.strip(), "ing": ing},
                    )
                session.commit()
            st.success(f"✅ {nouveau_nom} ajouté !")
            st.rerun()
