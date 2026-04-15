import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="St-Joseph Planning", layout="wide")

st.title("🏥 EMS St-Joseph - Gestion Cuisine")

# --- INITIALISATION DE LA MÉMOIRE (Session State) ---
# Cela permet de garder les modifications en mémoire
if 'planning' not in st.session_state:
    equipe_noms = ["Alain", "Sarah", "Mohamed", "Amélia", "Ejaz", "Laurent", "Corinne"]
    days = [f"{i:02d}/06" for i in range(1, 31)]
    # Création du planning par défaut
    df_init = pd.DataFrame("OFF", index=equipe_noms, columns=days)
    # On pré-remplit quelques jours pour gagner du temps
    for d in days:
        day_num = int(d[:2])
        if day_num % 7 not in [0, 6]: # Jours de semaine
            df_init.loc["Alain", d] = "J"
            df_init.loc["Sarah", d] = "J"
            df_init.loc["Laurent", d] = "AS"
            df_init.loc["Mohamed", d] = "AM"
    st.session_state.planning = df_init

# --- PARAMÈTRES ÉQUIPE ---
# Laurent est maintenant autorisé à faire des AM (contrainte santé supprimée)
equipe_config = {
    "Alain": {"taux": 1.0, "vac_h": 8.2},
    "Sarah": {"taux": 1.0, "vac_h": 8.2},
    "Mohamed": {"taux": 1.0, "vac_h": 8.2},
    "Amélia": {"taux": 0.9, "vac_h": 7.38},
    "Ejaz": {"taux": 0.7, "vac_h": 5.74},
    "Laurent": {"taux": 0.6, "vac_h": 4.92},
    "Corinne": {"taux": 0.5, "vac_h": 4.1}
}

codes_h = {"AM": 8.2, "AM+": 8.25, "J": 8.0, "AS": 8.2, "LONG": 9.0, "ADM": 8.25, "OFF": 0, "VAC": 0}

# --- AFFICHAGE ET ÉDITION ---
st.subheader("📅 Planning du mois de Juin")
st.info("💡 Double-cliquez sur une case pour changer l'horaire. Les calculs se mettent à jour en bas.")

# Le data_editor modifie directement la mémoire de l'app
edited_df = st.data_editor(st.session_state.planning, use_container_width=True)
st.session_state.planning = edited_df

# --- CALCULS ---
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Totaux et Écarts (Heures)")
    stats = []
    for nom, config in equipe_config.items():
        total = 0
        for val in edited_df.loc[nom]:
            if val == "VAC":
                total += config["vac_h"]
            else:
                total += codes_h.get(val, 0)
        
        cible = config["taux"] * 168 # Base mensuelle exemple
        stats.append({"Collaborateur": nom, "Heures": round(total, 2), "Cible": cible, "Écart": round(total - cible, 2)})
    
    st.table(pd.DataFrame(stats))

with col2:
    st.subheader("🚨 Alertes Service")
    # Vérif AM (au moins un par jour)
    for day in edited_df.columns:
        if "AM" not in edited_df[day].values:
            st.warning(f"⚠️ Manque AM le {day}")

st.sidebar.success("Application St-Joseph prête.")
