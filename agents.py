import os
from dotenv import load_dotenv

load_dotenv()

import litellm

# Set LiteLLM environment variables BEFORE crewai import
os.environ["LITELLM_LOCAL_RESOURCES"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"
litellm.drop_params = True

from crewai import Agent, LLM

model_name = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
if not model_name.startswith("groq/"):
    model_name = f"groq/{model_name}"

llm = LLM(
    model=model_name,
    api_key=os.getenv("GROQ_API_KEY"),
    drop_params=True,
)

research_agent = Agent(
    role="Destination Researcher",
    goal="Find current, practical info about {destination} for {start_date} to {end_date}",
    backstory="A local travel expert skilled at pulling current attractions, events, and travel info from the web.",
    llm=llm,
    verbose=True,
    cache=False,
)

planner = Agent(
    role="Trip Planner",
    goal="Turn research into a realistic day-by-day itinerary matching interests: {interests}",
    backstory="A meticulous planner who turns raw research into an organized schedule.",
    llm=llm,
    verbose=True,
    cache=False,
)