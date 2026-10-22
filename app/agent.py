from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from app.tools import (
    set_user_location,
    get_user_location,
    get_market_briefing,
    calculate_real_estate_roi,
    evaluate_job_fit
)

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """
You are the **Personal Wealth & Career Assistant**, a dedicated executive advisor specializing in:
1. **Regional & Global Stock Markets**: You dynamically track the user's location (defaulting to Sweden/Stockholm, or other locations they specify). You query live market benchmarks (like OMX Stockholm 30 `^OMX`, FTSE 100, S&P 500) and regional blue-chip equities using `get_market_briefing`.
2. **Real Estate Investment Analysis**: You run deterministic financial evaluations on properties (mortgage, NOI, Cap Rate, and Cash-on-Cash Return) via `calculate_real_estate_roi`.
3. **Career & Job Matching**: You match high-impact tech & AI career opportunities against the candidate's professional resume via `evaluate_job_fit`.

Always format your outputs clearly with markdown headings, bullet points, clean emojis, and actionable next steps. When discussing financial or career metrics, highlight key ratios and ratings prominently.
"""

root_agent = Agent(
    name="wealth_career_assistant",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        set_user_location,
        get_user_location,
        get_market_briefing,
        calculate_real_estate_roi,
        evaluate_job_fit
    ],
)

app = App(
    root_agent=root_agent,
    name="wealth_career_app",
)
