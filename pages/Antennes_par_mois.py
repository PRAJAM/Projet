import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Analyse des Antennes")

df = pd.read_csv('https://github.com/PRAJAM/Projet/raw/jules/Export_TER_juin2023_FIX_SafwanChendeb.csv', sep=';')

sample_fraction = 0.1  # Vous pouvez ajuster cette valeur
df = df.sample(frac=sample_fraction, random_state=1)

# Enlever les valeurs nulles ou trop petites de Largeur de bande
df2 = df.dropna(subset=['ASS_LGBD_KHZ'])
df2 = df2[df2["ASS_LGBD_KHZ"] >1000]

# Enlever les antennes qui ont été supprimées
enreg_to_supp = df2[df2['MVT_CODE'] == 'SUP']['N° ENREG']
df2 = df2[~df2['N° ENREG'].isin(enreg_to_supp)]

# Garder seulement les ajouts d'antenne
df2 = df2[df2['MVT_CODE'] == 'ADD']

# Enlever les MOD
df2 = df2[df2['MVT_CODE'] != 'MOD' ]

# Garder seulement les dernières modifications de chaque antenne
df2['Date CAF'] = pd.to_datetime(df['Date CAF'], format='%d/%m/%Y')
df2 = df2.sort_values('Date CAF').drop_duplicates(subset = "N° ENREG", keep = 'last')



# Graph du nombre d'ajouts d'antennes par mois
df2 = df2[df2['MVT_CODE'] != 'MOD' ]

# Convert 'Date CAF' to datetime
df2['Date CAF'] = pd.to_datetime(df2['Date CAF'], format='%d/%m/%Y')

# Extract month and year and count the occurrences
df2['YearMonth'] = df2['Date CAF'].dt.to_period('M')
monthly_counts = df2['YearMonth'].value_counts().sort_index().reset_index()
monthly_counts.columns = ['YearMonth', 'Number of Antennas']

# Converting 'YearMonth' to string to avoid serialization issue
monthly_counts['YearMonth'] = monthly_counts['YearMonth'].astype(str)

# Plotting the evolution using Plotly
fig = px.line(
    monthly_counts, 
    x='YearMonth', 
    y='Number of Antennas', 
    title='Évolution du nombre d\'ajout d\'antennes par mois',
    markers=True,
    labels={'YearMonth': 'Mois', 'Number of Antennas': 'Nombre d\'antennes ajoutées'}
)

fig.update_layout(
    xaxis_title='Mois',
    yaxis_title='Nombre d\'antennes ajoutées',
    xaxis_tickangle=-45
)

# Affichage du graphe
st.plotly_chart(fig)


# Graph du nombre d'antennes en service par mois
# Convertir 'Date CAF' en datetime
df2['Date CAF'] = pd.to_datetime(df2['Date CAF'], format='%d/%m/%Y')

# Recalculer les cumuls de manière détaillée
# Reprendre les données filtrées et triées
df2 = df.dropna(subset=['ASS_LGBD_KHZ'])
df2 = df2[df2["ASS_LGBD_KHZ"] > 1000]
df2['Date CAF'] = pd.to_datetime(df2['Date CAF'], format='%d/%m/%Y')
df2 = df2.sort_values(by='Date CAF')
df2['YearMonth'] = df2['Date CAF'].dt.to_period('M')

# Compter les 'ADD' et 'SUP' par mois sans cumuls
adds_per_month = df2[df2['MVT_CODE'] == 'ADD'].groupby('YearMonth').size()
sups_per_month = df2[df2['MVT_CODE'] == 'SUP'].groupby('YearMonth').size()

# Fusionner les deux séries en DataFrame
service_df_corrected = pd.DataFrame({'Adds': adds_per_month, 'Sups': sups_per_month}).fillna(0)

# Calculer les cumuls de manière correcte
service_df_corrected['Cumulative Adds'] = service_df_corrected['Adds'].cumsum()
service_df_corrected['Cumulative Sups'] = service_df_corrected['Sups'].cumsum()

# Calculer le nombre d'antennes en service
service_df_corrected['Antennas in Service'] = service_df_corrected['Cumulative Adds'] - service_df_corrected['Cumulative Sups']

# Réinitialiser l'index et convertir 'YearMonth' en string pour le tracé
service_df_corrected = service_df_corrected.reset_index()
service_df_corrected['YearMonth'] = service_df_corrected['YearMonth'].astype(str)



# Tracer le nombre d'antennes en service avec Plotly
fig_corrected = px.line(
    service_df_corrected, 
    x='YearMonth', 
    y='Antennas in Service', 
    title='Nombre d\'antennes en service par mois',
    markers=True,
    labels={'YearMonth': 'Mois', 'Antennas in Service': 'Nombre d\'antennes en service'}
)

fig_corrected.update_layout(
    xaxis_title='Mois',
    yaxis_title='Nombre d\'antennes en service',
    xaxis_tickangle=-45
)


st.plotly_chart(fig_corrected)
