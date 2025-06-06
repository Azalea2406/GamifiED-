def calculate_xp(score, max_score=100):
    """Calculate XP based on score out of max_score. Max XP per level is 25."""
    xp = int((score / max_score) * 25)
    return min(xp, 25)

