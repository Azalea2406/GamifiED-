import streamlit as st
import pandas as pd
from firebase_admin import firestore

db = firestore.client()

@st.cache_data(ttl=60)
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
    leaderboard_df = leaderboard_df[["badge", "name", "email", "xp", "avatar", "rank"]]

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
    def make_html_row(row, is_current_user=False):
        avatar_html = f"<img src='{row['avatar']}' width='32' style='border-radius:50%' />" if row['avatar'] else "👤"
        style = "font-weight: bold; background-color: #0f3460;" if is_current_user else ""
        return f"""
            <tr style="{style}">
                <td>{row['badge']}</td>
                <td>{avatar_html}</td>
                <td>{row['name']}</td>
                <td>{row['xp']} XP</td>
            </tr>
        """

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
        tr:hover {
            background-color: #283149;
            transition: background 0.3s;
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
        is_me = row["email"] == user.get("email", "")
        table_html += make_html_row(row, is_me)
    table_html += "</tbody></table>"

    st.markdown(table_html, unsafe_allow_html=True)

    # 🔮 AI Assistant Section
    st.markdown("---")
    st.subheader("🤖 Ask the AI Assistant")

    user_question = st.text_input("Got a question about your course or a topic?")
    assigned_course = user.get("course", "General Learning")  # Fallback course context

    if user_question:
        with st.spinner("Thinking..."):
            try:
                from main import query_granite  # Safely import only when needed
                prompt = f"As a course assistant for the topic '{assigned_course}', answer this question: {user_question}"
                granite_response = query_granite(prompt)

                if isinstance(granite_response, dict) and "error" in granite_response:
                    st.error("Granite Error: " + granite_response["error"])
                elif isinstance(granite_response, list):
                    st.success("🧠 Granite says:")
                    st.markdown(granite_response[0]["generated_text"])
                else:
                    st.warning("Unexpected response format from Granite.")
            except Exception as e:
                st.error(f"Error communicating with Granite: {e}")
