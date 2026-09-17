import json
import re
from pathlib import Path


# =========================================================
# HOTEL DATA FILE
# =========================================================

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "hotel.json"
)


# =========================================================
# LOAD HOTEL DATA
# =========================================================

def load_hotel_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


# =========================================================
# HOTEL CONTEXT FOR GEMINI
# =========================================================

def hotel_context_text():
    data = load_hotel_data()

    return json.dumps(
        data,
        indent=2
    )


def get_hotel_context():
    return hotel_context_text()


# =========================================================
# DETERMINISTIC KNOWLEDGE-BASE ANSWERING
# =========================================================

def answer_from_knowledge_base(question: str):

    data = load_hotel_data()

    q = question.lower().strip()


    # =====================================================
    # ROOM AVAILABILITY
    # =====================================================

    availability_phrases = [
        "room availability",
        "room available",
        "rooms available",
        "check availability",
        "check rooms",
        "vacancy",
        "vacant room",
        "book a room",
        "need a room",
        "looking for a room",
        "rooms for",
        "room for",
        "available room",
    ]

    if any(
        phrase in q
        for phrase in availability_phrases
    ):

        return {
            "message": (
                "I can check room availability. "
                "Please provide your check-in date, "
                "check-out date, and number of adults."
            ),
            "source": "availability_flow",
            "needs_availability": True,
            "handled": True,
        }


    # =====================================================
    # CHECK-IN
    # =====================================================

    if (
        "check-in" in q
        or "check in" in q
    ):

        return {
            "message": (
                f"Check-in is at "
                f"{data['hotel']['check_in']}."
            ),
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }


    # =====================================================
    # CHECK-OUT
    # =====================================================

    if (
        "check-out" in q
        or "check out" in q
    ):

        return {
            "message": (
                f"Check-out is at "
                f"{data['hotel']['check_out']}."
            ),
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }


    # =====================================================
    # LOCATION
    # =====================================================

    if any(
        phrase in q
        for phrase in [
            "location",
            "located",
            "address",
            "where is the hotel",
        ]
    ):

        hotel = data["hotel"]

        location = hotel.get("location")
        address = hotel.get("address")

        if address:

            message = (
                f"The {hotel['name']} "
                f"is located at {address}."
            )

        elif location:

            message = (
                f"The {hotel['name']} "
                f"is located in {location}."
            )

        else:

            return {
                "message": (
                    "I don't have the hotel's "
                    "location information in my "
                    "knowledge base."
                ),
                "source": "fallback",
                "needs_availability": False,
                "handled": True,
            }

        return {
            "message": message,
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }


    # =====================================================
    # AMENITIES
    # =====================================================

    amenity_map = {
        "swimming pool": "swimming_pool",
        "swimming": "swimming_pool",
        "pool": "swimming_pool",
        "gym": "gym",
        "wi-fi": "wifi",
        "wifi": "wifi",
        "parking": "parking",
    }

    for keyword, key in amenity_map.items():

        if keyword in q:

            value = data["amenities"].get(
                key,
                False
            )

            label = key.replace(
                "_",
                " "
            )

            if value:

                message = (
                    f"Yes, the hotel has {label}."
                )

            else:

                message = (
                    f"No, the hotel does not "
                    f"have {label}."
                )

            return {
                "message": message,
                "source": "hotel_knowledge_base",
                "needs_availability": False,
                "handled": True,
            }


    # =====================================================
    # BREAKFAST
    # =====================================================

    if "breakfast" in q:

        return {
            "message": (
                f"Breakfast is "
                f"{data['policies']['breakfast']}."
            ),
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }


    # =====================================================
    # CANCELLATION
    # =====================================================

    if (
        "cancellation" in q
        or "cancel" in q
    ):

        return {
            "message": data["policies"]["cancellation"],
            "source": "hotel_knowledge_base",
            "needs_availability": False,
            "handled": True,
        }


    # =====================================================
    # ROOM SUITABILITY
    # =====================================================

    if (
        "room" in q
        and any(
            word in q
            for word in [
                "guest",
                "guests",
                "people",
                "person",
                "adult",
                "adults",
            ]
        )
    ):

        match = re.search(
            r"\b(\d+)\b",
            q
        )

        if match:

            guests = int(
                match.group(1)
            )

            suitable = [
                room["name"]
                for room in data["rooms"]
                if room["max_guests"] >= guests
            ]

            if suitable:

                return {
                    "message": (
                        f"For {guests} guest(s), "
                        f"suitable rooms include: "
                        f"{', '.join(suitable)}."
                    ),
                    "source": "hotel_knowledge_base",
                    "needs_availability": False,
                    "handled": True,
                }

            return {
                "message": (
                    f"I don't have a suitable room "
                    f"for {guests} guest(s) in the "
                    f"current hotel data."
                ),
                "source": "hotel_knowledge_base",
                "needs_availability": False,
                "handled": True,
            }


    # =====================================================
    # FALLBACK
    # =====================================================

    return {
        "message": (
            "I don't have enough information in "
            "the hotel knowledge base to answer "
            "that reliably."
        ),
        "source": "fallback",
        "needs_availability": False,
        "handled": False,
    }