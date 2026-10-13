from crewai import Task
from agents import research_agent, planner

def build_tasks(origin, destinations, start_date, end_date, interests, travelers, route_summary=""):
    dest_str = ", ".join(destinations) if isinstance(destinations, list) else destinations
    research_task = Task(
        description=f"Research a travel route starting from '{origin}' visiting stops: {dest_str} "
                     f"from {start_date} to {end_date}, focusing on interests: {interests}. "
                     f"Cover top attractions, food spots, weather, and travel tips for each stop.",
        expected_output="A concise research summary covering all stops on the route.",
        agent=research_agent,
    )
    plan_task = Task(
        description=f"Build a realistic day-by-day multi-stop itinerary for {travelers} traveler(s) starting from '{origin}' "
                     f"and visiting: {dest_str} from {start_date} to {end_date}.\n"
                     f"Calculated Route & Distances: {route_summary}\n"
                     f"Include travel times between legs, daily activities matching interests ({interests}), and rough budgets.",
        expected_output="A clean markdown itinerary with route order, travel leg times, day-by-day schedule, and estimated costs.",
        agent=planner,
        context=[research_task],
    )
    return [research_task, plan_task]