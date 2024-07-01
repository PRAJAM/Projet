import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans

# Chargement des données depuis un fichier CSV
df = pd.read_csv('https://github.com/PRAJAM/Projet/raw/jules/Export_TER_juin2023_FIX_SafwanChendeb.csv', delimiter=';')

# Nettoyage des données
df_clean = df.dropna(subset=['ASS_LGBD_KHZ'])
df_clean = df_clean[df_clean['ASS_LGBD_KHZ'] > 1000]

# Filtrage des mouvements avec MVT_CODE = 'SUP'
enreg_to_supp = df_clean[df_clean['MVT_CODE'] == 'SUP']['N° ENREG']
df_clean = df_clean[~df_clean['N° ENREG'].isin(enreg_to_supp)]

# Conversion de 'Date CAF' en datetime
df_clean['Date CAF'] = pd.to_datetime(df_clean['Date CAF'], format='%d/%m/%Y')

# Sélection des colonnes numériques et non numériques
numerical_cols = ['ASS_FRQ_KHZ', 'ASS_LGBD_KHZ', 'TER_ANT_AZM_MAX', 'TER_ANT_ANG', 
                  'PT_LONG_DEG', 'PT_LONG_MIN', 'PT_LONG_SEC', 'PT_LAT_DEG', 'PT_LAT_MIN', 'PT_LAT_SEC']
categorical_cols = ['Code CAF', 'MVT_CODE']  # Exemple de colonnes catégorielles à encoder

# Encodage des colonnes catégorielles
label_encoder = LabelEncoder()

for col in categorical_cols:
    df_clean[col] = label_encoder.fit_transform(df_clean[col])

# Normalisation des données numériques
scaler = StandardScaler()
df_clean[numerical_cols] = scaler.fit_transform(df_clean[numerical_cols])

# Affichage des informations sur les données chargées
print(df_clean.info())
print(df_clean.head())

# Utilisation de la méthode du coude pour déterminer le nombre optimal de clusters
x_scaled = df_clean[numerical_cols + categorical_cols].fillna(0)  # Remplacer les NaN par 0 ou autre méthode

wcss = []
for i in range(1, 11):
    kmeans = MiniBatchKMeans(n_clusters=i, random_state=42)
    kmeans.fit(x_scaled)
    wcss.append(kmeans.inertia_)

# Tracé du coude (Elbow Method)
plt.figure(figsize=(10, 6))
plt.plot(range(1, 11), wcss, marker='o', linestyle='--')
plt.xlabel('Nombre de Clusters')
plt.ylabel('WCSS (Inertia)')
plt.title('Méthode du Coude pour K-Means')
plt.show()

# Choix du nombre optimal de clusters (ici, 6 clusters)
k_optimal = 8

# Application de K-Means avec le nombre optimal de clusters
kmeans = MiniBatchKMeans(n_clusters=k_optimal, random_state=42)
df_clean['Cluster'] = kmeans.fit_predict(x_scaled)

# Réduction de dimension avec PCA pour visualisation
pca = PCA(n_components=2)
principal_components = pca.fit_transform(x_scaled)
pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])

# Ajout des composantes principales au dataframe original
df_pca = pd.concat([df_clean.reset_index(drop=True), pca_df], axis=1)

# Visualisation des composantes principales avec Plotly
fig_pca = px.scatter(df_pca, x='PC1', y='PC2', color='Cluster',
                     title='Analyse en Composantes Principales (PCA) avec Clustering K-Means')
fig_pca.show()

# Visualisation des clusters par affectataire avec Plotly
fig_cluster_caf = px.scatter(df_pca, x='PC1', y='PC2', color='Code CAF', symbol='Cluster',
                             title='Clustering K-Means par Affectataire')
fig_cluster_caf.show()

# Tracé des boxplots pour chaque attribut numérique en fonction des clusters
plt.figure(figsize=(18, 12))
for i, col in enumerate(numerical_cols, 1):
    plt.subplot(3, 4, i)
    sns.boxplot(x='Cluster', y=col, data=df_clean)
    plt.title(f'{col} par Cluster')
    plt.xlabel('Cluster')
    plt.ylabel(col)

plt.tight_layout()
plt.show()
