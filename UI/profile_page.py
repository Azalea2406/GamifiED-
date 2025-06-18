from Backend.granite_utils import query_granite

def profile_page(user):
    st.title("👤 Player Profile")

    username = user.get("username") or user.get("email") or "Learner"
    total_xp = user.get("total_xp", 0)
    badge = "🥇 Master" if total_xp >= 300 else "🥈 Expert" if total_xp >= 200 else "🥉 Intermediate" if total_xp >= 100 else "🎓 Beginner"
    course = user.get("course", "General Learning")

    # --- Personalized Motivation Section ---
    st.markdown("### 💬 Need a Boost?")
    custom_challenge = st.text_input("Feeling stuck? Share what you're struggling with (optional)")

    if st.button("Get Motivation"):
        if custom_challenge.strip():
            prompt = (
                f"Motivate a learner working on '{course}' who has earned {total_xp} XP "
                f"and is feeling stuck with: '{custom_challenge}'. "
                f"Encourage them to continue with kindness and positivity."
            )
        else:
            prompt = (
                f"Motivate a {badge} level learner who has earned {total_xp} XP in the course '{course}'. "
                "Give personalized encouragement to keep learning and progressing."
            )

        with st.spinner("Fetching motivation from Granite..."):
            try:
                response = query_granite(prompt)
                if isinstance(response, list):
                    st.success("🧠 Granite says:")
                    st.markdown(response[0]["generated_text"])
                else:
                    st.warning("⚠️ Unexpected response format from Granite.")
            except Exception as e:
                st.error(f"❌ Granite query failed: {e}")

    # --- Profile Card UI ---
    st.markdown(f"""
    <div style="background: rgba(0,0,0,0.6); padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 0 20px #00ffff;">
        <img src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png' width='120' style='border-radius: 50%; border: 3px solid #00ffff;' />
        <h2 style='color: #00ffff; font-family: Orbitron, monospace;'>{username}</h2>
        <h3 style='color: #ffffff;'>XP: {total_xp}</h3>
        <h3 style='color: #00ccff;'>🏅 Badge: {badge}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("🎨 Avatar customization and achievements coming soon!")
