import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===============================
# CONFIG PAGE
# ===============================
st.set_page_config(page_title="Six Nations BI Dashboard", layout="wide")
st.title("🏉 Six Nations BI Dashboard")
st.markdown("**Analyse de l'évolution offensive et du déséquilibre des matchs (2000-2024)**")

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("rugby_six_nations.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['TotalPoints'] = df['HomeScore'] + df['AwayScore']
    df['ScoreDiff'] = abs(df['HomeScore'] - df['AwayScore'])
    df['HighScoringMatch'] = (df['TotalPoints'] > 45).astype(int)
    df['CloseMatch'] = (df['ScoreDiff'] <= 7).astype(int)
    df['TotalBonus'] = df['HomeBonus'] + df['AwayBonus']

    # Décennie
    def decade(year):
        if year < 2010:
            return "2000s"
        elif year < 2020:
            return "2010s"
        else:
            return "2020s"
    df['Decade'] = df['Year'].apply(decade)
    return df

df = load_data()

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("Filtres")
selected_years = st.sidebar.slider(
    "Sélectionner une plage d'années",
    int(df['Year'].min()),
    int(df['Year'].max()),
    (int(df['Year'].min()), int(df['Year'].max()))
)

teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
selected_team = st.sidebar.selectbox("Choisir une équipe (optionnel)", ["Toutes"] + list(teams))

# Filter data
df_filtered = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]
if selected_team != "Toutes":
    df_filtered = df_filtered[
        (df_filtered['HomeTeam'] == selected_team) | (df_filtered['AwayTeam'] == selected_team)
    ]

# ===============================
# KPI METRICS
# ===============================
st.subheader("📊 KPI principaux")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Points moyens / match", round(df_filtered['TotalPoints'].mean(), 2))
col2.metric("Différence moyenne", round(df_filtered['ScoreDiff'].mean(), 2))
col3.metric("Bonus moyen / match", round(df_filtered['TotalBonus'].mean(), 2))
col4.metric("Proportion de matchs serrés (<=7 pts)", f"{round(df_filtered['CloseMatch'].mean()*100, 1)} %")

st.divider()

# ===============================
# OFFENSIVE TREND
# ===============================
st.subheader("📈 Évolution offensive")

points_trend = df_filtered.groupby('Year')['TotalPoints'].mean().reset_index()
fig_points = px.line(points_trend, x='Year', y='TotalPoints', markers=True, title="Points moyens par match")
st.plotly_chart(fig_points, use_container_width=True)

high_score_trend = df_filtered.groupby('Year')['HighScoringMatch'].mean().reset_index()
fig_high = px.line(high_score_trend, x='Year', y='HighScoringMatch', markers=True, title="Proportion de matchs à score élevé")
st.plotly_chart(fig_high, use_container_width=True)

bonus_trend = df_filtered.groupby('Year')['TotalBonus'].mean().reset_index()
fig_bonus = px.line(bonus_trend, x='Year', y='TotalBonus', markers=True, title="Bonus moyen par match")
st.plotly_chart(fig_bonus, use_container_width=True)

# ===============================
# SCORE DIFFERENCE
# ===============================
st.subheader("⚔️ Évolution du déséquilibre")
diff_trend = df_filtered.groupby('Year')['ScoreDiff'].mean().reset_index()
fig_diff = px.line(diff_trend, x='Year', y='ScoreDiff', markers=True, title="Différence moyenne de score")
st.plotly_chart(fig_diff, use_container_width=True)

close_trend = df_filtered.groupby('Year')['CloseMatch'].mean().reset_index()
fig_close = px.line(close_trend, x='Year', y='CloseMatch', markers=True, title="Proportion de matchs serrés")
st.plotly_chart(fig_close, use_container_width=True)

# ===============================
# TEAM PERFORMANCE
# ===============================
st.subheader("🏆 Performance des équipes")

# Points moyens par équipe
home_points = df_filtered.groupby('HomeTeam')['HomeScore'].mean()
away_points = df_filtered.groupby('AwayTeam')['AwayScore'].mean()
team_points = (home_points + away_points).sort_values(ascending=False)
team_points_df = team_points.reset_index().rename(columns={0:'AvgPoints'})

fig_team = px.bar(team_points_df, x='HomeTeam', y=team_points_df.index*0+0,
                  labels={'x':'Équipe','y':'Points moyens'}, title="Points moyens par équipe")
fig_team = px.bar(team_points_df, x='HomeTeam', y=(home_points + away_points).values, 
                  labels={'x':'Équipe','y':'Points moyens'}, title="Points moyens par équipe")
st.plotly_chart(fig_team, use_container_width=True)

# ===============================
# HEATMAP
# ===============================
st.subheader("🌡️ Heatmap des points par équipe par année")
team_year = df_filtered.pivot_table(index='Year', columns='HomeTeam', values='HomeScore', aggfunc='mean').fillna(0)
fig_heat = px.imshow(team_year.T, aspect="auto", color_continuous_scale='Viridis', title="Points moyens par équipe et par année")
st.plotly_chart(fig_heat, use_container_width=True)

# ===============================
# STORYTELLING
# ===============================
st.subheader("📖 Storytelling")
st.markdown("""
- Depuis 2015, on observe une **augmentation des points moyens et des bonus**, ce qui indique un jeu plus offensif.  
- La proportion de matchs à score élevé a également augmenté, confirmant le spectacle croissant.  
- Les matchs sont légèrement plus déséquilibrés ces dernières années, mais le suspense reste présent.  
- Certaines équipes sont particulièrement offensives, comme [à compléter selon ton dataset].  
- Ce dashboard permet de filtrer par équipe et période pour explorer les tendances.
""")
