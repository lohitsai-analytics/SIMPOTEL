import json
import re
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "hotel.json"


def load_hotel_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def hotel_context_text():
    return json.dumps(load_hotel_data(), indent=2)


def get_hotel_context():
    return hotel_context_text()


def answer_from_knowledge_base(question: str):
    data = load_hotel_data()
    q = question.lower().strip()

    # Availability is always handled by the deterministic backend tool.
    availability_phrases = [
        "room availability", "room available", "rooms available",
        "check availability", "check rooms", "vacancy", "vacant room",
        "book a room", "need a room", "looking for a room",
        "rooms for", "room for", "available room",
    ]
    if any(phrase in q for phrase in availability_phrases):
        return {
            "message": (
                "I can check room availability. Please provide your check-in date, "
                "check-out date, and number of adults."
            ),
            "source": "availability_flow",
            "needs_availability": True,
            "handled": True,
        }

    if "check-in" in q or "check in" in q:
        return {
            "message": f"Check-in is at {data['hotel']['check_in']}.",
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }

    if "check-out" in q or "check out" in q:
        return {
            "message": f"Check-out is at {data['hotel']['check_out']}.",
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }

    if any(phrase in q for phrase in ["location", "located", "address", "where is the hotel"]):
        hotel = data["hotel"]
        location = hotel.get("location")
        address = hotel.get("address")
        if address:
            message = f"The {hotel['name']} is located at {address}."
        elif location:
            message = f"The {hotel['name']} is located in {location}."
        else:
            message = "I don't have the hotel's location information in my knowledge base."
            return {"message": message, "source": "fallback", "needs_availability": False, "handled": True}
        return {"message": message, "source": "hotel_knowledge_base", "needs_availability": False, "handled": True}

    # Do not treat questions about cleanliness/maintenance/condition as proof
    # that the facility is well maintained. The KB does not contain that data.
    maintenance_keywords = [
        "maintained", "maintenance", "clean", "cleaned", "condition",
        "hygiene", "hygienic", "well maintained",
    ]
    if any(keyword in q for keyword in maintenance_keywords):
        return {
            "message": "I don't have information about the maintenance or condition of that facility.",
            "source": "fallback",
            "needs_availability": False,
            "handled": True,
        }

    amenity_map = {
        "swimming pool": "swimming_pool",
        "pool": "swimming_pool",
        "gym": "gym",
        "wi-fi": "wifi",
        "wifi": "wifi",
        "parking": "parking",
    }
    for keyword, key in amenity_map.items():
        if keyword in q:
            value = data["amenities"].get(key, False)
            if key == "swimming_pool":
                label = "a swimming pool"
            elif key == "wifi":
                label = "Wi-Fi"
            else:
                label = key.replace("_", " ")
            message = f"Yes, the hotel has {label}." if value else f"No, the hotel does not have {label}."
            return {"message": message, "source": "hotel_knowledge_base", "needs_availability": False, "handled": True}

    if "breakfast" in q:
        return {
            "message": f"Breakfast is {data['policies']['breakfast']}.",
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }

    if "cancellation" in q or "cancel" in q:
        return {
            "message": data["policies"]["cancellation"],
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }

    if "room" in q and any(word in q for word in ["guest", "guests", "people", "person", "adult", "adults"]):
        match = re.search(r"\b(\d+)\b", q)
        if match:
            guests = int(match.group(1))
            suitable = [room["name"] for room in data["rooms"] if room["max_guests"] >= guests]
            if suitable:
                message = f"For {guests} guest(s), suitable rooms include: {', '.join(suitable)}."
            else:
                message = f"I don't have a suitable room for {guests} guest(s) in the current hotel data."
            return {"message": message, "source": "hotel_knowledge_base", "needs_availability": False, "handled": True}

    return {
        "message": "I don't have enough information in the hotel knowledge base to answer that reliably.",
        "source": "fallback",
        "needs_availability": False,
        "handled": False,
    }
