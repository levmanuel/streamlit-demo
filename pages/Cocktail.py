import pandas as pd
import streamlit as st
from sqlalchemy import text

st.set_page_config(page_title="Mon Bar à Cocktails", page_icon="🍸")

# Source : liste officielle IBA (International Bartenders Association)
_COCKTAILS_DEFAUT = {
    # ── The Unforgettables ────────────────────────────────────────────
    "Alexander":          ["cognac", "crème de cacao brune", "crème fraîche"],
    "Americano":          ["campari", "vermouth rouge", "eau gazeuse"],
    "Angel Face":         ["gin", "apricot brandy", "calvados"],
    "Aviation":           ["gin", "maraschino", "crème de violette", "jus de citron"],
    "Between the Sheets": ["cognac", "rhum blanc", "triple sec", "jus de citron"],
    "Boulevardier":       ["whisky bourbon", "campari", "vermouth rouge"],
    "Clover Club":        ["gin", "jus de citron", "sirop de grenadine", "blanc d'oeuf"],
    "Daiquiri":           ["rhum blanc", "jus de citron vert", "sirop de sucre"],
    "Dry Martini":        ["gin", "vermouth sec"],
    "Gimlet":             ["gin", "jus de citron vert"],
    "Gin Fizz":           ["gin", "jus de citron", "sirop de sucre", "eau gazeuse"],
    "Hanky Panky":        ["gin", "vermouth rouge", "fernet branca"],
    "John Collins":       ["gin", "jus de citron", "sirop de sucre", "eau gazeuse"],
    "Last Word":          ["gin", "chartreuse verte", "maraschino", "jus de citron vert"],
    "Manhattan":          ["whisky seigle", "vermouth rouge", "angostura"],
    "Mary Pickford":      ["rhum blanc", "jus d'ananas", "maraschino", "grenadine"],
    "Monkey Gland":       ["gin", "jus d'orange", "grenadine", "absinthe"],
    "Negroni":            ["gin", "campari", "vermouth rouge"],
    "Old Fashioned":      ["whisky bourbon", "sucre", "angostura"],
    "Paradise":           ["gin", "apricot brandy", "jus d'orange"],
    "Rob Roy":            ["scotch whisky", "vermouth rouge", "angostura"],
    "Rose":               ["gin", "vermouth sec", "cherry brandy"],
    "Rusty Nail":         ["scotch whisky", "drambuie"],
    "Sazerac":            ["whisky seigle", "absinthe", "sucre", "peychaud bitters"],
    "Sidecar":            ["cognac", "triple sec", "jus de citron"],
    "Stinger":            ["cognac", "crème de menthe blanche"],
    "Tuxedo":             ["gin", "vermouth sec", "maraschino", "absinthe", "angostura"],
    "Whisky Sour":        ["whisky bourbon", "jus de citron", "sirop de sucre", "blanc d'oeuf"],
    "White Lady":         ["gin", "triple sec", "jus de citron"],
    # ── Contemporary Classics ─────────────────────────────────────────
    "Bellini":            ["prosecco", "purée de pêche"],
    "Black Russian":      ["vodka", "kahlua"],
    "Bloody Mary":        ["vodka", "jus de tomate", "sauce worcestershire", "tabasco", "sel de céleri"],
    "Caipirinha":         ["cachaça", "citron vert", "sucre"],
    "Cosmopolitan":       ["vodka citron", "triple sec", "jus de citron vert", "jus de cranberry"],
    "Cuba Libre":         ["rhum blanc", "coca-cola", "jus de citron vert"],
    "Dark 'n' Stormy":    ["rhum brun", "ginger beer", "jus de citron vert"],
    "French Martini":     ["vodka", "chambord", "jus d'ananas"],
    "Grasshopper":        ["crème de menthe verte", "crème de cacao blanche", "crème fraîche"],
    "Harvey Wallbanger":  ["vodka", "jus d'orange", "galliano"],
    "Hemingway Special":  ["rhum blanc", "maraschino", "jus de citron vert", "jus de pamplemousse"],
    "Horse's Neck":       ["brandy", "ginger ale", "angostura"],
    "Kamikaze":           ["vodka", "triple sec", "jus de citron vert"],
    "Kir":                ["vin blanc", "crème de cassis"],
    "Kir Royal":          ["champagne", "crème de cassis"],
    "Long Island Iced Tea": ["vodka", "gin", "rhum blanc", "tequila", "triple sec", "jus de citron", "cola"],
    "Mai Tai":            ["rhum ambré", "rhum brun", "curaçao orange", "orgeat", "jus de citron vert"],
    "Margarita":          ["tequila", "triple sec", "jus de citron vert"],
    "Mimosa":             ["champagne", "jus d'orange"],
    "Mint Julep":         ["whisky bourbon", "menthe", "sucre"],
    "Mojito":             ["rhum blanc", "menthe", "sucre", "jus de citron vert", "eau gazeuse"],
    "Moscow Mule":        ["vodka", "ginger beer", "jus de citron vert"],
    "Pina Colada":        ["rhum blanc", "crème de coco", "jus d'ananas"],
    "Planters Punch":     ["rhum brun", "jus d'orange", "jus d'ananas", "grenadine"],
    "Sex on the Beach":   ["vodka", "schnapps pêche", "jus d'orange", "jus de cranberry"],
    "Singapore Sling":    ["gin", "cherry brandy", "bénédictine", "cointreau", "grenadine", "jus d'ananas", "jus de citron", "angostura"],
    "Spritz Veneziano":   ["prosecco", "aperol", "eau gazeuse"],
    "Tequila Sunrise":    ["tequila", "jus d'orange", "grenadine"],
    "White Russian":      ["vodka", "kahlua", "crème fraîche"],
    # ── New Era Drinks ────────────────────────────────────────────────
    "Bramble":            ["gin", "crème de mûre", "jus de citron", "sirop de sucre"],
    "Espresso Martini":   ["vodka", "kahlua", "expresso", "sirop de sucre"],
    "Naked and Famous":   ["mezcal", "chartreuse jaune", "aperol", "jus de citron vert"],
    "Pornstar Martini":   ["vodka vanille", "passoa", "jus de fruit de la passion", "prosecco"],
    "Spicy Fifty":        ["vodka", "elderflower cordial", "jus de citron vert", "vanille", "piment"],
}

_BAR_DEFAUT = ["vodka", "gin", "rhum blanc", "jus de citron", "jus d'orange", "sirop de sucre", "menthe", "angostura"]


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
        # Bar : seed seulement si le bar est vide (respecte les choix utilisateur)
        bar_count = session.execute(text("SELECT COUNT(*) FROM bar_ingredients")).scalar()
        if bar_count == 0:
            for ing in _BAR_DEFAUT:
                session.execute(text("INSERT OR IGNORE INTO bar_ingredients VALUES (:ing)"), {"ing": ing})

        # Cocktails : seed incrémental — INSERT OR IGNORE permet d'ajouter de nouvelles
        # recettes sans écraser celles ajoutées par l'utilisateur
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
