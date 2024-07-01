import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import numpy as np

# Charger les données depuis le CSV
df = pd.read_csv('https://github.com/PRAJAM/Projet/raw/jules/Export_TER_juin2023_FIX_SafwanChendeb.csv', sep=';')

df2 = df.dropna(subset=['ASS_LGBD_KHZ'])
df2 = df2[df2["ASS_LGBD_KHZ"] > 1000]

enreg_to_supp = df2[df2['MVT_CODE'] == 'SUP']['N° ENREG']
df2 = df2[~df2['N° ENREG'].isin(enreg_to_supp)]

df2['Date CAF'] = pd.to_datetime(df['Date CAF'], format='%d/%m/%Y')
df2 = df2.sort_values('Date CAF').drop_duplicates(subset='N° ENREG', keep='last')

# Fonction vectorisée pour convertir les coordonnées DMS en degrés décimaux
def dms_to_dd(degrees, minutes, seconds, orientation):
    dd = degrees + minutes / 60 + seconds / 3600
    dd[orientation.isin(['W', 'S'])] *= -1
    return dd

# Appliquer la conversion sur les colonnes de latitude et de longitude
df2['latitude'] = dms_to_dd(df2['PT_LAT_DEG'], df2['PT_LAT_MIN'], df2['PT_LAT_SEC'], df2['PT_LAT_ORIENT'])
df2['longitude'] = dms_to_dd(df2['PT_LONG_DEG'], df2['PT_LONG_MIN'], df2['PT_LONG_SEC'], df2['PT_LONG_ORIENT'])

# Échantillonnage des données pour réduire le nombre de points
sample_fraction = 0.1  # Vous pouvez ajuster cette valeur
df_sample = df2.sample(frac=sample_fraction, random_state=1)

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

# Sauvegarder la carte dans un fichier HTML
m.save('antennas_heatmap_small.html')

# Afficher la carte dans le notebook
m
