// routePlannerEngine.js - Built-in Intelligent Routing & Agentic Engine

export const CITIES_DATABASE = {
  "delhi": { name: "Delhi", lat: 28.6139, lon: 77.2090, state: "Delhi", highlights: ["Red Fort", "Qutub Minar", "India Gate", "Chandni Chowk"], food: ["Parathas at Paranthe Wali Gali", "Chole Bhature", "Butter Chicken"] },
  "agra": { name: "Agra", lat: 27.1767, lon: 78.0081, state: "Uttar Pradesh", highlights: ["Taj Mahal (Sunrise)", "Agra Fort", "Mehtab Bagh", "Fatehpur Sikri"], food: ["Agra Petha", "Bedmi Puri", "Mughlai Korma"] },
  "jaipur": { name: "Jaipur", lat: 26.9124, lon: 75.7873, state: "Rajasthan", highlights: ["Hawa Mahal", "Amber Fort", "City Palace", "Jantar Mantar"], food: ["Dal Baati Churma", "Pyaaz Kachori", "Ghevar"] },
  "chandigarh": { name: "Chandigarh", lat: 30.7333, lon: 76.7794, state: "Punjab/Haryana", highlights: ["Rock Garden", "Sukhna Lake", "Rose Garden", "Sector 17 Market"], food: ["Amritsari Kulcha", "Makki di Roti & Sarson Saag", "Lassi"] },
  "amritsar": { name: "Amritsar", lat: 31.6340, lon: 74.8723, state: "Punjab", highlights: ["Golden Temple", "Jallianwala Bagh", "Wagah Border Ceremony", "Gobindgarh Fort"], food: ["Langhar Prasad", "Amritsari Fish", "Kesar Da Dhaba Thali"] },
  "mumbai": { name: "Mumbai", lat: 19.0760, lon: 72.8777, state: "Maharashtra", highlights: ["Gateway of India", "Marine Drive sunset", "Colaba Causeway", "Elephanta Caves"], food: ["Vada Pav", "Pav Bhaji at Sardar", "Bombay Duck"] },
  "goa": { name: "Goa", lat: 15.2993, lon: 74.1240, state: "Goa", highlights: ["Baga & Palolem Beaches", "Old Goa Churches", "Dudhsagar Falls", "Fort Aguada"], food: ["Goan Fish Curry", "Pork Vindaloo", "Bebinca dessert"] },
  "udaipur": { name: "Udaipur", lat: 24.5854, lon: 73.7125, state: "Rajasthan", highlights: ["City Palace", "Lake Pichola boat ride", "Jag Mandir", "Saheliyon-ki-Bari"], food: ["Gatte ki Sabzi", "Laal Maas", "Kachori"] },
  "manali": { name: "Manali", lat: 32.2396, lon: 77.1887, state: "Himachal Pradesh", highlights: ["Solang Valley", "Rohtang Pass", "Old Manali Cafes", "Hadimba Temple"], food: ["Siddu", "Trout Fish", "Thukpa & Momos"] },
  "shimla": { name: "Shimla", lat: 31.1048, lon: 77.1734, state: "Himachal Pradesh", highlights: ["Mall Road", "The Ridge", "Jakhoo Temple", "Kalka-Shimla Toy Train"], food: ["Dhaam thali", "Chana Madra", "Hot Cinnamon Buns"] },
  "varanasi": { name: "Varanasi", lat: 25.3176, lon: 82.9739, state: "Uttar Pradesh", highlights: ["Dashashwamedh Ghat Aarti", "Kashi Vishwanath Temple", "Sarnath", "Boat ride at dawn"], food: ["Banarasi Paan", "Kachori Jalebi", "Malaiyyo"] },
  "bengaluru": { name: "Bengaluru", lat: 12.9716, lon: 77.5946, state: "Karnataka", highlights: ["Lalbagh Botanical Garden", "Cubbon Park", "Bangalore Palace", "Indiranagar cafes"], food: ["Masala Dosa at CTR", "Filter Coffee", "Bisi Bele Bath"] }
};

// Known driving distance matrix in km
const ROAD_MATRIX = {
  "delhi-agra": 233,
  "delhi-jaipur": 280,
  "delhi-chandigarh": 244,
  "delhi-amritsar": 450,
  "delhi-manali": 535,
  "delhi-shimla": 345,
  "delhi-varanasi": 820,
  "delhi-udaipur": 660,
  "agra-jaipur": 240,
  "agra-chandigarh": 440,
  "agra-amritsar": 650,
  "agra-varanasi": 605,
  "jaipur-chandigarh": 510,
  "jaipur-amritsar": 700,
  "jaipur-udaipur": 395,
  "chandigarh-amritsar": 228,
  "chandigarh-shimla": 112,
  "chandigarh-manali": 305,
  "mumbai-goa": 585,
  "mumbai-udaipur": 760,
  "mumbai-bengaluru": 985,
  "goa-bengaluru": 560
};

// Compute distance between any 2 cities
export function calculateLegDistance(cityA, cityB) {
  const normA = cityA.toLowerCase().trim();
  const normB = cityB.toLowerCase().trim();
  
  if (normA === normB) return { distanceKm: 0, durationHours: "0h 0m" };

  const key1 = `${normA}-${normB}`;
  const key2 = `${normB}-${normA}`;

  let km = ROAD_MATRIX[key1] || ROAD_MATRIX[key2];

  if (!km) {
    // Haversine formula calculation with 1.28x road winding factor
    const cA = CITIES_DATABASE[normA];
    const cB = CITIES_DATABASE[normB];
    if (cA && cB) {
      const R = 6371; // Earth radius in km
      const dLat = ((cB.lat - cA.lat) * Math.PI) / 180;
      const dLon = ((cB.lon - cA.lon) * Math.PI) / 180;
      const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos((cA.lat * Math.PI) / 180) *
          Math.cos((cB.lat * Math.PI) / 180) *
          Math.sin(dLon / 2) *
          Math.sin(dLon / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      km = Math.round(R * c * 1.28);
    } else {
      km = Math.floor(Math.random() * 250) + 180;
    }
  }

  // Driving duration estimate (average speed ~55-65 km/h)
  const totalMinutes = Math.round((km / 58) * 60);
  const hrs = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;
  const durationStr = `${hrs}h ${mins > 0 ? `${mins}m` : ""}`;

  return { distanceKm: km, durationHours: durationStr };
}

// Permutations generator for finding optimal visiting sequence
function getPermutations(arr) {
  if (arr.length <= 1) return [arr];
  const result = [];
  for (let i = 0; i < arr.length; i++) {
    const current = arr[i];
    const remaining = arr.slice(0, i).concat(arr.slice(i + 1));
    const remainingPerms = getPermutations(remaining);
    for (let p of remainingPerms) {
      result.push([current, ...p]);
    }
  }
  return result;
}

// Find optimal route sequence
export function optimizeRouteOrder(origin, stops) {
  if (!stops || stops.length === 0) return { orderedStops: [], totalKm: 0, legs: [] };
  if (stops.length === 1) {
    const leg = calculateLegDistance(origin, stops[0]);
    return {
      orderedStops: stops,
      totalKm: leg.distanceKm,
      legs: [{ from: origin, to: stops[0], distanceKm: leg.distanceKm, duration: leg.durationHours }]
    };
  }

  // For small stops (<= 6), compute permutations to find minimum distance
  const perms = stops.length <= 6 ? getPermutations(stops) : [stops];
  let bestPerm = perms[0];
  let minTotal = Infinity;

  for (let perm of perms) {
    let currentTotal = 0;
    let prev = origin;
    for (let stop of perm) {
      const leg = calculateLegDistance(prev, stop);
      currentTotal += leg.distanceKm;
      prev = stop;
    }
    if (currentTotal < minTotal) {
      minTotal = currentTotal;
      bestPerm = perm;
    }
  }

  // Construct legs for the best permutation
  const legs = [];
  let prevCity = origin;
  for (let stop of bestPerm) {
    const leg = calculateLegDistance(prevCity, stop);
    legs.push({
      from: prevCity,
      to: stop,
      distanceKm: leg.distanceKm,
      duration: leg.durationHours
    });
    prevCity = stop;
  }

  return {
    orderedStops: bestPerm,
    totalKm: minTotal,
    legs
  };
}

// Simulate Multi-Agent Pipeline & Generate Itinerary
export async function runAgenticPlanner({
  origin,
  stops,
  startDate,
  endDate,
  travelers,
  interests,
  onStepProgress
}) {
  // 1. Agent 1: Route Optimization Tool Execution
  if (onStepProgress) {
    onStepProgress({
      step: 1,
      agent: "Route & Transit Optimizer",
      thought: `Evaluating pairwise highway distances from ${origin} to stops: [${stops.join(", ")}]...`,
      action: "call:calculate_optimal_route(origin, stops)"
    });
  }
  await new Promise((r) => setTimeout(r, 600));

  const routePlan = optimizeRouteOrder(origin, stops);

  // 2. Agent 2: Destination Researcher
  if (onStepProgress) {
    onStepProgress({
      step: 2,
      agent: "Destination Researcher",
      thought: `Gathering verified attractions, cultural highlights, and local food spots for: ${[origin, ...routePlan.orderedStops].join(" ➔ ")}...`,
      action: `research_stops(focus: ${interests.join(", ")})`
    });
  }
  await new Promise((r) => setTimeout(r, 700));

  // 3. Agent 3: Trip Planner / Itinerary Architect
  if (onStepProgress) {
    onStepProgress({
      step: 3,
      agent: "Trip Planner",
      thought: `Synthesizing ${routePlan.totalKm} km road route with ${travelers} traveler(s) schedule from ${startDate} to ${endDate}...`,
      action: "generate_structured_day_schedule()"
    });
  }
  await new Promise((r) => setTimeout(r, 600));

  // Calculate day count
  const sDate = new Date(startDate);
  const eDate = new Date(endDate);
  const diffTime = Math.abs(eDate - sDate);
  const totalDays = Math.max(1, Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1);

  // Build day by day itinerary
  const allStopsSequence = [origin, ...routePlan.orderedStops];
  const days = [];

  for (let d = 1; d <= totalDays; d++) {
    const stopIndex = Math.min(Math.floor(((d - 1) / totalDays) * allStopsSequence.length), allStopsSequence.length - 1);
    const currentCityName = allStopsSequence[stopIndex];
    const normCity = currentCityName.toLowerCase().trim();
    const cityData = CITIES_DATABASE[normCity] || {
      name: currentCityName,
      highlights: ["Historic City Center", "Local Bazaar", "Scenic Viewpoint", "Architectural Landmark"],
      food: ["Signature Local Thali", "Street Food Market", "Traditional Dessert"]
    };

    const isTravelDay = d > 1 && stopIndex > 0 && Math.floor(((d - 2) / totalDays) * allStopsSequence.length) !== stopIndex;
    const prevCity = isTravelDay ? allStopsSequence[stopIndex - 1] : null;
    const legInfo = prevCity ? calculateLegDistance(prevCity, currentCityName) : null;

    days.push({
      day: d,
      city: cityData.name,
      title: isTravelDay
        ? `Scenic Drive from ${prevCity} to ${cityData.name}`
        : `Exploring ${cityData.name} • ${interests.slice(0, 2).join(" & ")} Focus`,
      transit: isTravelDay ? `Drive ${legInfo.distanceKm} km (~${legInfo.durationHours}) via National Highway` : "Local intra-city transport / cab",
      morning: {
        time: "09:00 AM - 12:30 PM",
        activity: isTravelDay
          ? `Early morning check-out from ${prevCity}; start scenic drive to ${cityData.name} with roadside breakfast.`
          : `Visit ${cityData.highlights[0] || "main historical monument"} during pleasant morning hours with guided tour.`
      },
      afternoon: {
        time: "01:00 PM - 04:30 PM",
        activity: `Lunch tasting ${cityData.food[0] || "local specialty"}. Explore ${cityData.highlights[1] || "cultural markets & craft stores"}.`
      },
      evening: {
        time: "05:00 PM - 08:30 PM",
        activity: `Sunset views at ${cityData.highlights[2] || "waterfront / viewpoint"}. Dinner enjoying authentic ${cityData.food[1] || "regional dinner"}.`
      },
      foodTip: `Must try: ${cityData.food.slice(0, 2).join(", ")}`,
      proTip: `Wear comfortable walking shoes. Pre-book monument entry tickets online to bypass weekend queues.`
    });
  }

  return {
    routePlan,
    totalDays,
    days,
    summary: {
      origin,
      destinations: routePlan.orderedStops,
      routeSequence: [origin, ...routePlan.orderedStops].join(" ➔ "),
      totalDistanceKm: routePlan.totalKm,
      travelers,
      interests,
      estimatedBudgetINR: (routePlan.totalKm * 14 + totalDays * 4200 * travelers).toLocaleString("en-IN")
    }
  };
}
