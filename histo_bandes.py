import pandas as pd
import plotly.graph_objects as go

# Charger les données depuis le CSV
df = pd.read_csv('Export_TER_juin2023_FIX_SafwanChendeb.csv', sep=';')

# Filter out rows with missing 'ASS_LGBD_KHZ' and keep rows where 'ASS_LGBD_KHZ' is greater than 1000
df2 = df.dropna(subset=['ASS_LGBD_KHZ'])
df2 = df2[df2["ASS_LGBD_KHZ"] > 1000]

# Remove records with 'MVT_CODE' == 'SUP'
enreg_to_supp = df2[df2['MVT_CODE'] == 'SUP']['N° ENREG']
df2 = df2[~df2['N° ENREG'].isin(enreg_to_supp)]

# Convert 'Date CAF' to datetime and sort the dataframe
df2['Date CAF'] = pd.to_datetime(df2['Date CAF'], format='%d/%m/%Y')
df2 = df2.sort_values('Date CAF').drop_duplicates(subset='N° ENREG', keep='last')

# Convert 'ASS_FRQ_KHZ' and 'ASS_LGBD_KHZ' to integers if they are floats
df2['ASS_FRQ_KHZ'] = df2['ASS_FRQ_KHZ'].astype(int)
df2['ASS_LGBD_KHZ'] = df2['ASS_LGBD_KHZ'].astype(int)

# Create a new column combining 'ASS_FRQ_KHZ' and 'ASS_LGBD_KHZ'
df2['Frequency_Band'] = df2['ASS_FRQ_KHZ'].astype(str) + '_' + df2['ASS_LGBD_KHZ'].astype(str)

# Extract unique frequency bands and their counts
frequency_counts = df2['Frequency_Band'].value_counts().reset_index()
frequency_counts.columns = ['Frequency_Band', 'Count']

# Separate the frequency bands back into individual columns for plotting
frequency_counts[['ASS_FRQ_KHZ', 'ASS_LGBD_KHZ']] = frequency_counts['Frequency_Band'].str.split('_', expand=True)
frequency_counts['ASS_FRQ_KHZ'] = frequency_counts['ASS_FRQ_KHZ'].astype(int)
frequency_counts['ASS_LGBD_KHZ'] = frequency_counts['ASS_LGBD_KHZ'].astype(int)

# Convert frequencies to MHz for better readability
frequency_counts['ASS_FRQ_MHZ'] = frequency_counts['ASS_FRQ_KHZ'] / 1000
frequency_counts['ASS_LGBD_MHZ'] = frequency_counts['ASS_LGBD_KHZ'] / 1000

# Create the bar plot using plotly.graph_objects
fig = go.Figure()

for _, row in frequency_counts.iterrows():
    start_freq = row['ASS_FRQ_MHZ']
    end_freq = start_freq + row['ASS_LGBD_MHZ']
    hover_text = (
        f"Start Frequency: {start_freq} MHz<br>"
        f"End Frequency: {end_freq} MHz<br>"
        f"Bandwidth: {row['ASS_LGBD_MHZ']} MHz<br>"
        f"Occurrences: {row['Count']}"
    )
    fig.add_trace(go.Bar(
        x=[start_freq],
        y=[row['Count']],
        width=[row['ASS_LGBD_MHZ']],
        name=f"{start_freq} MHz",
        hovertext=hover_text,
        hoverinfo="text"
    ))

# Customize the layout
fig.update_layout(
    title='Histogram of Frequency Bands Usage',
    xaxis_title='Frequency (MHz)',
    yaxis_title='Count',
    bargap=0.2,
    bargroupgap=0.1,
    xaxis=dict(tickformat=','),
    yaxis=dict(tickformat=',')
)

fig.show()
