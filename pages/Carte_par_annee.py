import pandas as pd
import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

@st.cache_data
def load_data():
    df = pd.read_csv('https://github.com/PRAJAM/Projet/raw/jules/Export_TER_juin2023_FIX_SafwanChendeb.csv', sep=';')

    sample_fraction = 0.1  # Vous pouvez ajuster cette valeur
    df = df.sample(frac=sample_fraction, random_state=1)

    df = df.dropna(subset=['ASS_LGBD_KHZ'])
    df['Date CAF'] = pd.to_datetime(df['Date CAF'], format='%d/%m/%Y')
    df['Annee'] = df['Date CAF'].dt.year

    df_sorted = df.sort_values(by=['Annee', 'Date CAF'])
    return df_sorted


@st.cache_data
def get_df_by_year(df_sorted):
    df_by_year = {}
    for year in df_sorted['Annee'].unique():
        current_year_rows = df_sorted[(df_sorted['Annee'] == year) & (df_sorted['MVT_CODE'].isin(['ADD', 'MOD']))]
        previous_years_rows = df_sorted[(df_sorted['Annee'] < year) & (~df_sorted['MVT_CODE'].str.contains('SUP', na=False))]
        combined_rows = pd.concat([previous_years_rows, current_year_rows])
        df_by_year[year] = combined_rows
    return df_by_year


df_sorted = load_data()
df_by_year = get_df_by_year(df_sorted)


# Afficher la carte dans Streamlit
st.title('Carte des antennes avec HeatMap et clusters par année')

selected_year = st.selectbox("Sélectionner une année", df_sorted['Annee'].unique())
df_year = df_by_year[selected_year]



# Fonction vectorisée pour convertir les coordonnées DMS en degrés décimaux
def dms_to_dd(degrees, minutes, seconds, orientation):
    dd = degrees + minutes / 60 + seconds / 3600
    dd[orientation.isin(['W', 'S'])] *= -1
    return dd

# Appliquer la conversion sur les colonnes de latitude et de longitude
df_year['latitude'] = dms_to_dd(df_year['PT_LAT_DEG'], df_year['PT_LAT_MIN'], df_year['PT_LAT_SEC'], df_year['PT_LAT_ORIENT'])
df_year['longitude'] = dms_to_dd(df_year['PT_LONG_DEG'], df_year['PT_LONG_MIN'], df_year['PT_LONG_SEC'], df_year['PT_LONG_ORIENT'])

# Échantillonnage des données pour réduire le nombre de points
sample_fraction = 0.1  # Vous pouvez ajuster cette valeur
df_sample = df_year.sample(frac=sample_fraction, random_state=1)

# Créer une carte Folium centrée sur la France avec des tuiles légères
m = folium.Map(location=[46.603354, 1.888334], zoom_start=6, tiles='CartoDB positron')

# Ajouter des clusters de points pour une meilleure visualisation
marker_cluster = MarkerCluster().add_to(m)

# Ajouter les points au cluster
for idx, row in df_sample.iterrows():
    folium.Marker(location=[row['latitude'], row['longitude']]).add_to(marker_cluster)

# Préparer les données pour le HeatMap avec intensité
heat_data = [[row['latitude'], row['longitude'], 1] for index, row in df_sample.iterrows()]

# Ajouter le HeatMap à la carte avec des paramètres ajustés pour une meilleure performance et visibilité
HeatMap(heat_data, radius=15, blur=10, max_zoom=12, min_opacity=0.4).add_to(m)


# Afficher la carte dans Streamlit
st_folium(m, width=800, height=600)
