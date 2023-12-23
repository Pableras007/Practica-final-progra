import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import re
import numpy as np
import requests

@st.cache_data
def load_data(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    mijson = r.json()
    listado = mijson['partidos']
    df = pd.DataFrame.from_records(listado)

    # Convertir la columna 'date' a tipo datetime
    df['date'] = pd.to_datetime(df['date'])

    return df

def infer_winner(row):
    if row['home_score'] > row['away_score']:
        return row['home_team']
    elif row['away_score'] > row['home_score']:
        return row['away_team']
    else:
        return None

def percentage_of_wins(df, team_name, location):
    if location == 'Home':
        total_matches = df[df['home_team'] == team_name]
        total_wins = df[(df['home_team'] == team_name) & (df['home_score'] > df['away_score'])]
    elif location == 'Away':
        total_matches = df[df['away_team'] == team_name]
        total_wins = df[(df['away_team'] == team_name) & (df['away_score'] > df['home_score'])]
    else:
        total_matches = df[(df['home_team'] == team_name) | (df['away_team'] == team_name)]
        total_wins = df[(df['home_team'] == team_name) & (df['home_score'] > df['away_score']) |
                        (df['away_team'] == team_name) & (df['away_score'] > df['home_score'])]

    win_percentage = (len(total_wins) / len(total_matches)) * 100 if len(total_matches) > 0 else 0
    return win_percentage

def teams_with_highest_cumulative_wins(df):
    cumulative_wins = df.groupby(['competition', 'home_team']).apply(
        lambda x: x['home_score'] > x['away_score']).groupby(['competition', 'home_team']).sum().reset_index()
    cumulative_wins['win'] = cumulative_wins[0].astype(int)
    cumulative_wins.drop(columns=0, inplace=True)
    teams_cumulative_wins = cumulative_wins.sort_values(by=['competition', 'win'], ascending=[False, False])
    return teams_cumulative_wins

def head_to_head_stats(df, team1, team2, selected_years=None):
    head_to_head = df[((df['home_team'] == team1) & (df['away_team'] == team2)) |
                      ((df['home_team'] == team2) & (df['away_team'] == team1))]

    if selected_years:
        start_year = pd.Timestamp.now().year - selected_years
        head_to_head['date'] = pd.to_datetime(head_to_head['date'])  # Convertir 'date' a tipo datetime
        head_to_head = head_to_head[head_to_head['date'].dt.year >= start_year]

    if 'winner' not in head_to_head.columns:
        head_to_head['winner'] = head_to_head.apply(
            lambda row: row['home_team'] if row['home_score'] > row['away_score'] else row['away_team'], axis=1)

    head_to_head_stats = head_to_head[
        ['date', 'competition', 'winner', 'home_team', 'away_team', 'home_score', 'away_score', 'stadium']]
    return head_to_head_stats

def world_cup_performance(df, team_name, selected_years):
    team_matches = df[
        ((df['home_team'] == team_name) | (df['away_team'] == team_name)) &
        (df['date'].dt.year.isin(selected_years))]

    if team_matches.empty:
        st.info(f"No hay datos disponibles para {team_name} en los años seleccionados.")
    else:
        if 'winner' not in team_matches.columns:
            team_matches['winner'] = team_matches.apply(
                lambda row: row['home_team'] if row['home_score'] > row['away_score'] else (
                    row['away_team'] if row['away_score'] > row['home_score'] else None), axis=1)

        st.subheader(f"Desempeño de {team_name} en los años {', '.join(map(str, selected_years))}")
        st.write(f"Total de partidos jugados: {len(team_matches)}")
        st.write(f"Total de partidos ganados: {len(team_matches[team_matches['winner'] == team_name])}")

        st.subheader("Partidos y Resultados:")
        st.table(team_matches[['date', 'home_team', 'away_team', 'home_score', 'away_score', 'winner']])

def world_cup_final_wins(df, team_name):
    # Filtrar partidos de la Copa del Mundo
    world_cup_matches = df[df['competition'].str.lower().str.contains('world cup', na=False)]

    # Asegurarse de que 'stage' esté presente o intentar inferirlo
    if 'stage' not in world_cup_matches.columns:
        world_cup_matches['stage'] = world_cup_matches.apply(
            lambda row: 'Final' if 'final' in str(row['competition']).lower() else None, axis=1
        )

    # Asegurarse de que 'winner' esté presente o intentar inferirlo
    if 'winner' not in world_cup_matches.columns:
        world_cup_matches['winner'] = np.where(
            world_cup_matches['home_score'] > world_cup_matches['away_score'],
            world_cup_matches['home_team'],
            np.where(
                world_cup_matches['away_score'] > world_cup_matches['home_score'],
                world_cup_matches['away_team'],
                None
            )
        )

    # Eliminar filas donde 'stage' es nulo
    world_cup_matches = world_cup_matches.dropna(subset=['stage'])

    # Identificar las finales de la Copa del Mundo para el equipo seleccionado
    finals_won = world_cup_matches[
        (((world_cup_matches['home_team'] == team_name) | (world_cup_matches['away_team'] == team_name)) &
         (world_cup_matches['winner'] == team_name) &
         (world_cup_matches['stage'] == 'Final') &
         (world_cup_matches['competition'].str.lower().str.contains('rugby world cup final')))
    ]

    return finals_won[['date', 'competition', 'home_team', 'away_team', 'home_score', 'away_score', 'stadium']]

df_merged = load_data('http://fastapi:8000/retrieve_data')

registros = str(df_merged.shape[0])
equipos = str(len(df_merged['home_team'].unique()))
torneos = str(len(df_merged['competition'].dropna().unique()))

st.header("Información general sobre partidos de rugby")

col1, col2, col3 = st.columns(3)

with col1:
    col1.subheader('Partidos totales')
    st.markdown(f'<p style="text-align:center;font-size:24px;">{registros}</p>', unsafe_allow_html=True)

with col2:
    col2.subheader('Numero de equipos')
    st.markdown(f'<p style="text-align:center;font-size:24px;">{equipos}</p>', unsafe_allow_html=True)

with col3:
    col3.subheader('Torneos')
    st.markdown(f'<p style="text-align:center;font-size:24px;">{torneos}</p>', unsafe_allow_html=True)

# Porcentaje de victorias para un equipo específico
equipo_seleccionado = st.selectbox('Selecciona un equipo para ver su porcentaje de victorias:',
                                   df_merged['home_team'].unique())
location_seleccionada = st.radio("Selecciona la ubicación:", ['Home', 'Away', 'Total'])
win_percentage = percentage_of_wins(df_merged, equipo_seleccionado, location_seleccionada)

st.subheader(f'Porcentaje de victorias para {equipo_seleccionado} ({location_seleccionada})')
st.markdown(f'{win_percentage:.2f}%')

# Comparación de equipos
st.subheader("Comparación de Equipos")

# Seleccionar equipos
equipo1 = st.selectbox('Selecciona el primer equipo:', df_merged['home_team'].unique())
equipo2 = st.selectbox('Selecciona el segundo equipo:', df_merged['away_team'].unique())

if equipo1 == equipo2:
    st.warning("Por favor, selecciona dos equipos diferentes.")
else:
    st.subheader(f"Resultados entre {equipo1} y {equipo2}")

    selected_years = st.slider('Selecciona la cantidad de años (opcional):', 1, 150, 10,
                               key='years_slider')  # clave única para el slider
    head_to_head_stats_df = head_to_head_stats(df_merged, equipo1, equipo2, selected_years)
    head_to_head_stats_df = head_to_head_stats_df.sort_values(by='date', ascending=False)

    st.table(head_to_head_stats_df)

# Desempeño en el Mundial de un equipo específico en un año seleccionado
st.subheader("Desempeño en el Mundial por Año")
equipo_seleccionado_mundial = st.selectbox('Selecciona un equipo:', df_merged['home_team'].unique())

# Filtrar eventos internacionales a solo Rugby World Cups
world_cup_options = df_merged[df_merged['competition'].str.lower().str.contains('world cup', na=False)]

# Obtener una lista única de años utilizando expresiones regulares
world_cup_years = world_cup_options['competition'].str.extract(r'(\d{4})').dropna().astype(int).squeeze().unique()
selected_years = st.multiselect('Selecciona los años:', world_cup_years)

# Filtrar partidos de la Copa del Mundo para el equipo seleccionado en los años seleccionados
world_cup_matches = df_merged[
    (df_merged['competition'].str.contains('world cup', case=False, na=False)) &
    ((df_merged['home_team'] == equipo_seleccionado_mundial) | (df_merged['away_team'] == equipo_seleccionado_mundial)) &
    (df_merged['date'].dt.year.isin(selected_years))]

# Asegurarse de que winner esté presensente
if 'winner' not in world_cup_matches.columns:
    world_cup_matches['winner'] = world_cup_matches.apply(
        lambda row: row['home_team'] if row['home_score'] > row['away_score'] else (
            row['away_team'] if row['away_score'] > row['home_score'] else None), axis=1)

# Eliminar filas donde winner es nulo
world_cup_matches = world_cup_matches.dropna(subset=['winner'])

# Desempeño del equipo en los años seleccionados del Mundial
world_cup_performance(df_merged, equipo_seleccionado_mundial, selected_years)

# Creo el dashboard
st.title("Finales de la Copa del Mundo Ganadas por un Equipo")

# Seleccionar equipo
equipo_seleccionado_finals = st.selectbox('Selecciona un equipo para ver las finales ganadas:',
                                          df_merged['home_team'].unique())

# Obtener las finales ganadas por el equipo seleccionado
finals_won_df = world_cup_final_wins(df_merged, equipo_seleccionado_finals)

# Mostrar los resultados en una tabla
if not finals_won_df.empty:
    st.subheader(f"Finales de la Copa del Mundo Ganadas por {equipo_seleccionado_finals}")
    st.table(finals_won_df)

    # Calcular el número de finales ganadas por el equipo seleccionado directamente
    team_wins = finals_won_df[((finals_won_df['home_team'] == equipo_seleccionado_finals) |
                               (finals_won_df['away_team'] == equipo_seleccionado_finals))].shape[0]

    # Mostrar el número de finales ganadas por el equipo seleccionado
    st.subheader(f"Número de Finales Ganadas por {equipo_seleccionado_finals}")
    st.write(team_wins)
else:
    st.info(f"{equipo_seleccionado_finals} no ha ganado ninguna final de la Copa del Mundo.")

# Calcular la cantidad total de mundiales ganados por cada equipo
world_cup_winners = df_merged[df_merged['competition'].str.lower().str.contains('world cup final', na=False)]
world_cup_winners['winner'] = np.where(
    world_cup_winners['home_score'] > world_cup_winners['away_score'],
    world_cup_winners['home_team'],
    np.where(
        world_cup_winners['away_score'] > world_cup_winners['home_score'],
        world_cup_winners['away_team'],
        None
    )
)
world_cup_winners = world_cup_winners.dropna(subset=['winner'])

# Contar la cantidad de veces que cada equipo ha ganado la Copa del Mundo
world_cup_win_counts = world_cup_winners['winner'].value_counts().reset_index()
world_cup_win_counts.columns = ['Team', 'Wins']

# Creo el gráfico de barras
st.title("Mundiales Totales Ganados")
fig = px.bar(world_cup_win_counts, x='Team', y='Wins', title="Mundiales Totales Ganados")
st.plotly_chart(fig)

# Calcular el recuento de partidos jugados por año
matches_per_year = df_merged['date'].dt.year.value_counts().sort_index()

# Creo el gráfico
fig_matches_per_year = px.bar(x=matches_per_year.index, y=matches_per_year.values,
                              labels={'x': 'Año', 'y': 'Número de partidos jugados'},
                              title='Partidos jugados por año',
                              template='plotly',
                              )

# Muestro el gráfico
st.plotly_chart(fig_matches_per_year)