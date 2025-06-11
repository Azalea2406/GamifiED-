import streamlit as st
from Backend.granite_utils import query_granite

def profile_page(user):
    st.title("👤 Player Profile")

    username = user.get("username") or user.get("email") or "Learner"
    total_xp = user.get("total_xp", 0)

    # --- Motivation Section ---
    if st.button("Get Motivation"):
        motivation_prompt = f"Motivate a learner who has {total_xp} XP to keep learning."
        with st.spinner("Fetching motivation..."):
            response = query_granite(motivation_prompt)

        if isinstance(response, list):
            st.success("🧠 Motivation from Granite:")
            st.markdown(response[0]["generated_text"])
        else:
            st.warning("⚠️ Could not fetch AI response.")

    # --- Profile Card UI ---
    st.markdown(f"""
    <div style="
        background: rgba(0,0,0,0.6);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 0 20px #00ffff;">
        
        <img src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png' width='120' style='border-radius: 50%; border: 3px solid #00ffff;' />
        <h2 style='color: #00ffff; font-family: Orbitron, monospace;'>{username}</h2>
        <h3 style='color: #ffffff;'>XP: {total_xp}</h3>
        <h3 style='color: #00ccff;'>🏅 Badge: {"🥇 Master" if total_xp >= 300 else "🎓 Beginner"}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("Customize your avatar and profile here soon!")
