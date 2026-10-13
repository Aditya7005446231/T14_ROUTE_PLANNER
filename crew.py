from crewai import Crew, Process
from agents import research_agent, planner
from tasks import build_tasks

def run_trip_planner(origin, destinations, start_date, end_date, interests, travelers, route_summary=""):
    tasks = build_tasks(origin, destinations, start_date, end_date, interests, travelers, route_summary)
    crew = Crew(agents=[research_agent, planner], tasks=tasks, process=Process.sequential, verbose=True)

    return crew.kickoff()