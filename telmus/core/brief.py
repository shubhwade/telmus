from __future__ import annotations

from telmus.core.result import ScanResult


def generate_brief(result: ScanResult) -> str:
    """Generate a deterministic analyst brief from scan results."""
    health_phrases: list[str] = []
    if result.health.piotroski_f is not None:
        if result.health.piotroski_f >= 7:
            health_phrases.append(
                f"strong fundamentals (Piotroski F-score of {result.health.piotroski_f})"
            )
        elif result.health.piotroski_f >= 5:
            health_phrases.append(
                f"adequate fundamentals (Piotroski F-score of {result.health.piotroski_f})"
            )
        else:
            health_phrases.append(
                f"weak fundamentals (Piotroski F-score of {result.health.piotroski_f})"
            )
    if result.health.altman_z is not None:
        if result.health.altman_z > 2.6:
            health_phrases.append(
                f"financially safe (Altman Z-score of {result.health.altman_z:.2f})"
            )
        elif result.health.altman_z >= 1.1:
            health_phrases.append(
                f"grey zone credit profile (Altman Z-score of {result.health.altman_z:.2f})"
            )
        else:
            health_phrases.append(
                f"distress risk (Altman Z-score of {result.health.altman_z:.2f})"
            )
    health_sentence = (
        ". ".join(health_phrases) + "."
        if health_phrases
        else "Health metrics are inconclusive."
    )

    growth_phrases: list[str] = []
    if result.growth.revenue_cagr_3y is not None:
        growth_phrases.append(
            f"Revenue growth is {result.growth.revenue_cagr_3y * 100:.1f}% over three years"
        )
    if result.growth.margin_trend is not None:
        growth_phrases.append(f"operating margins are {result.growth.margin_trend}")
    growth_sentence = (
        " and ".join(growth_phrases) + "."
        if growth_phrases
        else "Growth metrics are inconclusive."
    )

    if result.red_flags:
        flags_text = ", ".join(
            f"{flag.type.replace('_', ' ')} ({flag.severity})"
            for flag in result.red_flags
        )
        final_sentence = (
            f"Red flags detected: {flags_text}. Requires further due diligence."
        )
    else:
        final_sentence = "No significant red flags detected. Suitable for DCF or comparable company analysis."

    return f"{health_sentence} {growth_sentence} {final_sentence}"
