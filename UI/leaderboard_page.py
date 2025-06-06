import streamlit as st
import pandas as pd
from firebase_admin import firestore

db = firestore.client()

def fetch_leaderboard_data():
    users_ref = db.collection("users")
    docs = users_ref.stream()

    leaderboard = []
    for doc in docs:
        data = doc.to_dict()
        leaderboard.append({
            "name": data.get("name") or "Unknown",
            "email": data.get("email"),
            "xp": data.get("xp", 0),
            "avatar": data.get("avatar_url", None)
        })
    return leaderboard

def get_badge(rank):
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return f"#{rank}"

def leaderboard_page(user):
    st.markdown("## 🏆 GamifiED Leaderboard")
    st.caption("Compete, climb ranks, and earn XP for learning activities!")

    leaderboard = fetch_leaderboard_data()
    leaderboard_df = pd.DataFrame(leaderboard).sort_values("xp", ascending=False).reset_index(drop=True)
    leaderboard_df["rank"] = leaderboard_df.index + 1
    leaderboard_df["badge"] = leaderboard_df["rank"].apply(get_badge)

    # Reorder columns
    leaderboard_df = leaderboard_df[["badge", "name", "email", "xp", "avatar"]]

    # Current user rank card
    current_user_row = leaderboard_df[leaderboard_df["email"] == user.get("email")]
    if not current_user_row.empty:
        r = current_user_row.iloc[0]
        st.success(
            f"🎉 You are currently ranked **#{r['rank']}** with **{r['xp']} XP** {get_badge(r['rank'])}"
        )
    else:
        st.warning("You're not ranked yet. Complete quests to earn XP!")

    # Display styled leaderboard table
    def make_html_row(row):
        avatar_html = f"<img src='{row['avatar']}' width='32' style='border-radius:50%' />" if row['avatar'] else "👤"
        row_html = f"""
            <tr>
                <td>{row['badge']}</td>
                <td>{avatar_html}</td>
                <td>{row['name']}</td>
                <td>{row['xp']} XP</td>
            </tr>
        """
        return row_html

    table_html = """
        <style>
        table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Rajdhani', sans-serif;
        }
        th, td {
            border: 1px solid #00ffff;
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #16213e;
            color: #00ffff;
        }
        tr:nth-child(even) {
            background-color: #1a1a2e;
        }
        </style>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Avatar</th>
                    <th>Name</th>
                    <th>XP</th>
                </tr>
            </thead>
            <tbody>
    """
    for _, row in leaderboard_df.iterrows():
        table_html += make_html_row(row)
    table_html += "</tbody></table>"

    st.markdown(table_html, unsafe_allow_html=True)
