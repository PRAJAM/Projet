import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Largeur de bande par service")

# Charger les données depuis le CSV
df = pd.read_csv('https://github.com/PRAJAM/Projet/raw/jules/Export_TER_juin2023_FIX_SafwanChendeb.csv', sep=';')

sample_fraction = 0.1  # Vous pouvez ajuster cette valeur
df = df.sample(frac=sample_fraction, random_state=1)


# Filtrer les lignes avec des valeurs manquantes pour ASS_LGBD_KHZ
df2 = df.dropna(subset=['ASS_LGBD_KHZ'])
df2 = df2[df2["ASS_LGBD_KHZ"] > 1000]

# Supprimer les enregistrements avec MVT_CODE == 'SUP'
enreg_to_supp = df2[df2['MVT_CODE'] == 'SUP']['N° ENREG']
df2 = df2[~df2['N° ENREG'].isin(enreg_to_supp)]

# Convertir 'Date CAF' en datetime
df2['Date CAF'] = pd.to_datetime(df2['Date CAF'], format='%d/%m/%Y')

# Convertir 'ASS_FRQ_KHZ' et 'ASS_LGBD_KHZ' en entiers si ce sont des floats
df2['ASS_FRQ_KHZ'] = df2['ASS_FRQ_KHZ'].astype(int)
df2['ASS_LGBD_KHZ'] = df2['ASS_LGBD_KHZ'].astype(int)

# Ajouter une colonne pour la bande de fréquence en MHz
df2['ASS_FRQ_MHZ'] = df2['ASS_FRQ_KHZ'] / 1000
df2['ASS_LGBD_MHZ'] = df2['ASS_LGBD_KHZ'] / 1000

# Ajouter une colonne pour la fréquence de fin en MHz
df2['END_FRQ_MHZ'] = df2['ASS_FRQ_MHZ'] + df2['ASS_LGBD_MHZ']

# Regrouper les données par année, service (Code CAF) et affectataire (BASE)
df2['Year'] = df2['Date CAF'].dt.year
grouped = df2.groupby(['Year', 'Code CAF', 'BASE']).agg(
    {'ASS_FRQ_MHZ': 'count', 'ASS_LGBD_MHZ': 'sum'}
).reset_index()

# Renommer les colonnes pour plus de clarté
grouped.columns = ['Year', 'Service', 'Affectataire', 'Num_Bands', 'Total_Bandwidth_MHz']



fig_bar = px.bar(grouped, x='Year', y='Total_Bandwidth_MHz', color='Service', barmode='stack',
             hover_data=['Affectataire', 'Num_Bands'],
             title='Largeur de Bande Totale par Année et par Service/Affectataire')

fig_bar.update_layout(xaxis=dict(tickformat='d'), yaxis=dict(tickformat=','))
st.plotly_chart(fig_bar)

fig_pie = px.pie(grouped, values='Total_Bandwidth_MHz', names='Service', title='Répartition de la Largeur de Bande par Service')
st.plotly_chart(fig_pie)
