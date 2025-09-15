import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("nba.csv")
    df["gameDate"] = pd.to_datetime(df["gameDate"])
    return df

df = load_data()

# Sidebar: select team
teams = sorted(set(df["hometeamName"]).union(set(df["awayteamName"])))
selected_team = st.sidebar.selectbox("Select a team", teams)

# Filter games
team_games = df[(df["hometeamName"] == selected_team) | (df["awayteamName"] == selected_team)]

# Compute stats
total_games = len(team_games)
wins = sum(team_games["winner"] == team_games["hometeamId"][team_games["hometeamName"] == selected_team].iloc[0]) if total_games > 0 else 0
losses = total_games - wins
points_scored = []
points_allowed = []

for _, row in team_games.iterrows():
    if row["hometeamName"] == selected_team:
        points_scored.append(row["homeScore"])
        points_allowed.append(row["awayScore"])
    else:
        points_scored.append(row["awayScore"])
        points_allowed.append(row["homeScore"])

avg_scored = sum(points_scored) / len(points_scored) if points_scored else 0
avg_allowed = sum(points_allowed) / len(points_allowed) if points_allowed else 0
avg_attendance = team_games["attendance"].mean()

# Title
st.title(f"🏀 {selected_team} - Team Insights")

# KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Games Played", total_games)
col2.metric("Wins", wins)
col3.metric("Losses", losses)
col4.metric("Avg Points Scored", f"{avg_scored:.1f}")
col5.metric("Avg Points Allowed", f"{avg_allowed:.1f}")

st.metric("Avg Attendance", f"{avg_attendance:,.0f}")

# Line chart: score trends
st.subheader("📈 Score Trends Over Time")
if not team_games.empty:
    team_games = team_games.sort_values("gameDate")
    scored_series = []
    allowed_series = []
    for _, row in team_games.iterrows():
        if row["hometeamName"] == selected_team:
            scored_series.append(row["homeScore"])
            allowed_series.append(row["awayScore"])
        else:
            scored_series.append(row["awayScore"])
            allowed_series.append(row["homeScore"])
    plt.figure(figsize=(8,4))
    plt.plot(team_games["gameDate"], scored_series, label="Points Scored", marker="o")
    plt.plot(team_games["gameDate"], allowed_series, label="Points Allowed", marker="o")
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Points")
    plt.title(f"{selected_team} Scores Over Time")
    st.pyplot(plt)

# Histogram: point differentials
st.subheader("📊 Point Differential Distribution")
point_diff = [sc - al for sc, al in zip(points_scored, points_allowed)]
plt.figure(figsize=(6,4))
plt.hist(point_diff, bins=10, color="skyblue", edgecolor="black")
plt.axvline(0, color="red", linestyle="--")
plt.title(f"{selected_team} Point Differentials")
plt.xlabel("Point Differential")
plt.ylabel("Frequency")
st.pyplot(plt)

# Show games table
st.subheader("📋 Game Records")
st.dataframe(team_games[["gameDate","hometeamName","awayteamName","homeScore","awayScore","winner","attendance"]])


# --- Performance vs Opponents ---
st.subheader(f"🤝 {selected_team} Performance vs Opponents")

# Determine opponent and whether selected team won
def get_opponent_and_result(row, team):
    if row["hometeamName"] == team:
        opponent = row["awayteamName"]
        won = row["winner"] == row["hometeamId"]
        scored, allowed = row["homeScore"], row["awayScore"]
    else:
        opponent = row["hometeamName"]
        won = row["winner"] == row["awayteamId"]
        scored, allowed = row["awayScore"], row["homeScore"]
    return opponent, won, scored, allowed

# Build opponent stats
opponent_stats = {}
for _, row in team_games.iterrows():
    opponent, won, scored, allowed = get_opponent_and_result(row, selected_team)
    if opponent not in opponent_stats:
        opponent_stats[opponent] = {"wins": 0, "losses": 0, "scored": [], "allowed": [], "attendance": []}
    if won:
        opponent_stats[opponent]["wins"] += 1
    else:
        opponent_stats[opponent]["losses"] += 1
    opponent_stats[opponent]["scored"].append(scored)
    opponent_stats[opponent]["allowed"].append(allowed)
    opponent_stats[opponent]["attendance"].append(row["attendance"])

# Convert to DataFrame
opp_df = pd.DataFrame([
    {
        "opponent": opp,
        "wins": stats["wins"],
        "losses": stats["losses"],
        "avg_scored": sum(stats["scored"]) / len(stats["scored"]),
        "avg_allowed": sum(stats["allowed"]) / len(stats["allowed"]),
        "avg_attendance": sum(stats["attendance"]) / len(stats["attendance"]),
    }
    for opp, stats in opponent_stats.items()
])

if not opp_df.empty:
    # Wins vs Losses Bar Chart
    st.markdown("### ✅ Wins vs ❌ Losses by Opponent")
    plt.figure(figsize=(8,4))
    plt.bar(opp_df["opponent"], opp_df["wins"], label="Wins", color="green")
    plt.bar(opp_df["opponent"], opp_df["losses"], bottom=opp_df["wins"], label="Losses", color="red")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Games")
    plt.legend()
    st.pyplot(plt)

    # Avg Points Scored vs Allowed
    st.markdown("### 📊 Avg Points Scored vs Allowed by Opponent")
    x = range(len(opp_df))
    width = 0.35
    plt.figure(figsize=(8,4))
    plt.bar([i - width/2 for i in x], opp_df["avg_scored"], width=width, label="Scored", color="blue")
    plt.bar([i + width/2 for i in x], opp_df["avg_allowed"], width=width, label="Allowed", color="orange")
    plt.xticks(x, opp_df["opponent"], rotation=45, ha="right")
    plt.ylabel("Points")
    plt.legend()
    st.pyplot(plt)

    # Avg Attendance
    st.markdown("### 🏟️ Avg Attendance by Opponent")
    plt.figure(figsize=(8,4))
    plt.bar(opp_df["opponent"], opp_df["avg_attendance"], color="purple")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Attendance")
    st.pyplot(plt)
