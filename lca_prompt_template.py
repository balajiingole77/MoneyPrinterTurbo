"""
Drop this into MoneyPrinterTurbo's prompt chain to generate
LCA information videos. Call get_script_prompt(row) with a
dict from your LCA dataset to get a ready-to-use MPT prompt.
"""

INFORMATION_VIDEO_PROMPT = """
You are writing a script for a 30-second faceless YouTube Short / TikTok video.

Topic: {topic}
Employer: {employer}
Job Title: {job_title}
Location: {location}
Prevailing Wage: ${wage:,.0f}/year

Rules:
- Hook in the first 3 words (do NOT start with "Did you know")
- Speak directly to H1B workers and employers
- State the wage, location, and job title clearly
- End with ONE call-to-action pointing to the website
- Total length: 60-80 words (30 seconds at average speaking pace)
- Tone: factual, trustworthy, slightly urgent
- No filler phrases ("amazing", "incredible", "game-changer")

Output ONLY the spoken script. No stage directions, no labels.
"""


def get_script_prompt(row: dict) -> str:
    """
    row: dict with keys employer, job_title, location, wage, topic (optional)
    """
    topic = row.get("topic") or f"LCA filing for {row['job_title']} at {row['employer']}"
    return INFORMATION_VIDEO_PROMPT.format(
        topic=topic,
        employer=row["employer"],
        job_title=row["job_title"],
        location=row["location"],
        wage=float(row["wage"]),
    )


# Example usage:
if __name__ == "__main__":
    sample = {
        "employer": "Google LLC",
        "job_title": "Software Engineer III",
        "location": "Mountain View, CA",
        "wage": 185000,
    }
    print(get_script_prompt(sample))
