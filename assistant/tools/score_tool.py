from langchain_core.tools import tool


@tool
def update_score(
    current_score: int,
    points_change: int,
    reason: str,
) -> dict:
    """
    Werk de score van een speler bij.

    Gebruik deze tool wanneer punten moeten worden toegevoegd
    of afgetrokken van een bestaande score.

    Een positieve points_change voegt punten toe.
    Een negatieve points_change trekt punten af.
    """

    new_score = current_score + points_change

    return {
        "previous_score": current_score,
        "points_change": points_change,
        "new_score": new_score,
        "reason": reason,
    }