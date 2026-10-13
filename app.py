import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from crew import run_trip_planner
from tools.tools import compute_optimal_route

st.set_page_config(page_title="Multi-Stop Route Planner", page_icon="🗺️", layout="wide")

st.title("🗺️ AI Multi-Stop Route Planner")
st.caption("Plan your travel route with real-time driving distances, geocoding, and AI-generated itineraries.")

with st.form("route_form"):
    col_orig, col_dest = st.columns(2)
    with col_orig:
        origin = st.text_input("📍 Starting Location (Source / Origin)", "Delhi, India", help="Where your trip starts from")
    with col_dest:
        destinations_str = st.text_input(
            "🚩 Destinations / Stops (Comma-separated)",
            "Agra, Jaipur",
            help="Enter one or more cities/stops to visit along the route"
        )

    c1, c2, c3 = st.columns(3)
    start_date = c1.date_input("Start date")
    end_date = c2.date_input("End date")
    travelers = c3.number_input("Travelers", min_value=1, value=2)

    interests = st.multiselect(
        "Interests & Preferences",
        ["Food", "Beaches", "History", "Adventure", "Nightlife", "Sightseeing", "Nature"],
        default=["Food", "History"]
    )
    submitted = st.form_submit_button("🗺️ Compute Route & Plan Itinerary", use_container_width=True)

if submitted:
    stops_list = [s.strip() for s in destinations_str.split(",") if s.strip()]

    if not origin.strip():
        st.error("Please enter a valid starting location!")
    elif not stops_list:
        st.error("Please enter at least one destination stop!")
    else:
        with st.spinner("Calculating route legs & driving distances via Geoapify..."):
            route_data = compute_optimal_route(origin, stops_list)

        st.subheader("🛣️ Route Distance Breakdown")
        st.info(f"**Route Sequence:** {route_data['route_str']}")

        if route_data["legs"]:
            cols = st.columns(len(route_data["legs"]))
            for idx, leg in enumerate(route_data["legs"]):
                with cols[idx]:
                    st.metric(
                        label=f"Leg {idx+1}: {leg['from']} ➔ {leg['to']}",
                        value=f"{leg['distance_km']} km",
                        delta=f"⏱️ {leg['duration']}" if leg['duration'] != "N/A" else None
                    )

            st.caption(f"**Total Driving Distance:** {route_data['total_km']} km")

        st.divider()

        with st.spinner("🤖 AI Agents are generating your detailed multi-stop itinerary..."):
            result = run_trip_planner(
                origin=origin,
                destinations=stops_list,
                start_date=start_date,
                end_date=end_date,
                interests=", ".join(interests),
                travelers=travelers,
                route_summary=f"Sequence: {route_data['route_str']} | Total Distance: {route_data['total_km']} km"
            )

        st.subheader("🗓️ Day-by-Day Route Itinerary")
        st.markdown(str(result))
        st.download_button("📥 Download Itinerary (Markdown)", str(result), file_name="route_itinerary.md")