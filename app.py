from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# ==========================================
# PASTE YOUR SERPAPI KEY BELOW
# ==========================================
SERP_API_KEY = "9b7d6dd9b57cdeea2e02b5f55c16d2e2205f5ba82933c55ce3af6a6b30fb41ee"

app = FastAPI(title="AI Flight Recommendation Agent")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Airport Codes
AIRPORT_CODES = {
    "Delhi": "DEL",
    "Mumbai": "BOM",
    "Pune": "PNQ",
    "Bangalore": "BLR",
    "Hyderabad": "HYD",
    "Chennai": "MAA",
    "Kolkata": "CCU",
    "Ahmedabad": "AMD",
    "Goa": "GOI",
    "Jaipur": "JAI",
    "Nagpur": "NAG",
    "Indore": "IDR",
    "Lucknow": "LKO",
    "Bhopal": "BHO"
}


@app.get("/")
def home():
    return {
        "message": "AI Flight Recommendation Agent Running Successfully"
    }


class FlightRequest(BaseModel):
    source: str
    destination: str
    budget: int
    airline: str = ""


@app.post("/recommend")
def recommend(req: FlightRequest):

    source = req.source.strip().title()
    destination = req.destination.strip().title()

    departure = AIRPORT_CODES.get(source)
    arrival = AIRPORT_CODES.get(destination)

    if departure is None:
        return {
            "message": f"Airport code not found for {source}"
        }

    if arrival is None:
        return {
            "message": f"Airport code not found for {destination}"
        }

    url = "https://serpapi.com/search.json"

    params = {
    "engine": "google_flights",
    "departure_id": departure,
    "arrival_id": arrival,
    "outbound_date": "2026-07-10",
    "return_date": "2026-07-15",

    "currency": "INR",
    "hl": "en",
    "gl": "in",

    "api_key": SERP_API_KEY
}

    response = requests.get(url, params=params)

    data = response.json()

    # Debug
    print(data)

    if "error" in data:
        return {
            "message": "SerpAPI Error",
            "error": data["error"]
        }

    if "best_flights" not in data:
        return {
            "message": "No flights returned",
            "raw_response": data
        }

    flights = []

    for item in data["best_flights"]:

        if "flights" not in item:
            continue

        first = item["flights"][0]

        price = item.get("price", 999999)

        airline = first.get("airline", "")

        if req.airline != "":
            if airline.lower() != req.airline.lower():
                continue

        if price <= req.budget:

            flights.append({

                "airline": airline,

                "price": price,

                "departure": first["departure_airport"]["time"],

                "arrival": first["arrival_airport"]["time"],

                "source": source,

                "destination": destination

            })

    if len(flights) == 0:
        return {
            "message": "No flights found within budget."
        }

    best = min(flights, key=lambda x: x["price"])

    return {
        "best_option": best,
        "reason": "Cheapest Live Flight from Google Flights"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )