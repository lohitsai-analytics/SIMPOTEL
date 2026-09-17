from datetime import date

from services.hotel_service import load_hotel_data


def check_availability(
    check_in: date,
    check_out: date,
    adults: int
):
    """
    Deterministic mock availability checker.

    Business rules:
    - At least 1 adult is required.
    - Check-out must be after check-in.
    - A room is suitable when max_guests >= adults.
    """

    # =====================================================
    # VALIDATE GUEST COUNT
    # =====================================================

    if adults < 1:
        raise ValueError(
            "Number of adults must be at least 1."
        )

    # =====================================================
    # VALIDATE DATES
    # =====================================================

    if check_out <= check_in:
        raise ValueError(
            "Check-out must be after check-in."
        )

    # =====================================================
    # CALCULATE NIGHTS
    # =====================================================

    nights = (check_out - check_in).days

    # =====================================================
    # LOAD HOTEL DATA
    # =====================================================

    data = load_hotel_data()

    suitable_rooms = []

    # =====================================================
    # FIND SUITABLE ROOMS
    # =====================================================

    for room in data["rooms"]:

        max_guests = room["max_guests"]

        if max_guests >= adults:

            # Support either "id" or "room_id"
            room_id = room.get(
                "id",
                room.get("room_id")
            )

            # Support either "price" or "price_per_night"
            price = room.get(
                "price",
                room.get("price_per_night")
            )

            # Safety check
            if price is None:
                raise ValueError(
                    f"Price is missing for room: {room.get('name', room_id)}"
                )

            suitable_rooms.append(
                {
                    "room_id": room_id,
                    "room_name": room["name"],
                    "max_guests": max_guests,
                    "price_per_night": price,
                    "nights": nights,
                    "total_price": price * nights,
                }
            )

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "adults": adults,
        "available": len(suitable_rooms) > 0,
        "rooms": suitable_rooms,
    }