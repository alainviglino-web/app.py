import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURATION DE L'APPLICATION ---
st.set_page_config(page_title="EMS Cuisine V8 - Intelligence de Planification", layout="wide")

st.title("🏥 EMS Cuisine - Planning Intelligent V8")
st.sidebar.header("⚙️ Paramètres & Contrôle")

# --- DONNÉES ÉQUIPE & TAUX ---
equipe = {
    "Alain": {"taux": 1.0, "role": "Cuisinier", "am": False},
    "Sarah": {"taux": 1.0, "role": "Cuisinier", "am": False},
    "Mohamed": {"taux": 1.0, "role": "Aide", "am": True},
    "Amélia": {"taux": 0.9, "role": "Aide", "am": True},
    "Ejaz": {"taux": 0.7, "role": "Aide", "am": True},
    "Laurent": {"taux": 0.6, "role": "Aide", "am": False}, # Pas de 06h30
    "Corinne": {"taux": 0.5, "role": "Aide", "am": True},
}

codes_horaires = {
    "AM": 8.2,      # 06:30 - 15:00
    "AM+": 8.25,    # 10:15 - 18:30 (Renfort vaisselle)
    "J": 8.0,       # 08:30 - 17:00 (Cuisine)
    "AS": 8.2,      # 11:00 - 19:30 (Soir)
    "LONG": 9.0,    # 09:00 - 19:00
    "ADM": 8.25,    # Administratif Alain
    "OFF": 0,       # Repos
    "VAC": 0        # Vacances (calculées au prorata séparément)
}

# --- LOGIQUE DE CALCUL DES VACANCES ---
def get_vac_hours(nom):
    return round(equipe[nom]["taux"] * 8.2, 2)

# --- GÉNÉRATION DU PLANNING ---
days = [f"{i:02d}/06" for i in range(1, 31)]
df = pd.DataFrame(index=equipe.keys(), columns=days)

# Remplissage par défaut (Simulation intelligente)
for nom in equipe.keys():
    for day in days:
        d = int(day[:2])
        # Vacances Corinne (10 au 24 juin)
        if nom == "Corinne" and 10 <= d <= 24:
            df.loc[nom, day] = "VAC"
        # Vacances Alain (22 au 26 juin)
        elif nom == "Alain" and 22 <= d <= 26:
            df.loc[nom, day] = "VAC"
        # Jeudi Alain ADM
        elif nom == "Alain" and d % 7 == 4: # Jeudi
            df.loc[nom, day] = "ADM"
        elif d % 7 in [0, 6]: # Week-ends
            df.loc[nom, day] = "OFF" if d % 14 == 0 else "J"
        else:
            df.loc[nom, day] = "J" if equipe[nom]["role"] == "Cuisinier" else "AM"

# --- INTERFACE UTILISATEUR ---
st.subheader("📅 Vue Mensuelle Horizontale")
edited_df = st.data_editor(df, use_container_width=True)

# --- CALCULS RH & ALERTES ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Compteur d'heures mensuel")
    stats = []
    for nom in equipe.keys():
        total = 0
        for val in edited_df.loc[nom]:
            if val == "VAC":
                total += get_vac_hours(nom)
            else:
                total += codes_horaires.get(val, 0)
        
        cible = equipe[nom]["taux"] * 175 # Base 175h pour 100%
        stats.append({"Employé": nom, "Total": total, "Cible": cible, "Ecart": total - cible})
    
    st.table(pd.DataFrame(stats))

with col2:
    st.subheader("🚨 Contrôle Qualité EMS")
    # Vérification 1 AM par jour
    missing_am = []
    for day in days:
        if "AM" not in edited_df[day].values:
            missing_am.append(day)
    
    if missing_am:
        st.error(f"⚠️ Manque horaire AM (06:30) les : {', '.join(missing_am[:5])}...")
    else:
        st.success("✅ Ouverture 06:30 sécurisée tous les jours.")

    # Alerte Laurent 06:30
    if "AM" in edited_df.loc["Laurent"].values:
        st.warning("❗ Attention : Laurent est planifié à 06:30 (Contrainte santé !)")

st.sidebar.info("Cliquer sur une case pour modifier l'horaire. Le calcul des heures et les alertes se mettent à jour instantanément.")
