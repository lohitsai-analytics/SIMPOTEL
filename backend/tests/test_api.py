from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ---------------------------------------------------------
# 1. Normal hotel question
# ---------------------------------------------------------

def test_check_in_question():
    response = client.post(
        "/chat",
        json={
            "message": "What time is check-in?",
            "conversation": []
        }
    )

    assert response.status_code == 200
    assert "2:00 PM" in response.json()["message"]


# ---------------------------------------------------------
# 2. Amenity question
# ---------------------------------------------------------

def test_swimming_pool_question():
    response = client.post(
        "/chat",
        json={
            "message": "Does the hotel have a swimming pool?",
            "conversation": []
        }
    )

    assert response.status_code == 200
    assert "swimming pool" in response.json()["message"].lower()


# ---------------------------------------------------------
# 3. Breakfast
# ---------------------------------------------------------

def test_breakfast_question():
    response = client.post(
        "/chat",
        json={
            "message": "Is breakfast included?",
            "conversation": []
        }
    )

    assert response.status_code == 200
    assert "breakfast" in response.json()["message"].lower()


# ---------------------------------------------------------
# 4. Room suitability
# ---------------------------------------------------------

def test_room_for_three_guests():
    response = client.post(
        "/chat",
        json={
            "message": "Which room is suitable for 3 guests?",
            "conversation": []
        }
    )

    assert response.status_code == 200

    message = response.json()["message"]

    assert "Deluxe Room" in message
    assert "Family Room" in message


# ---------------------------------------------------------
# 5. Availability request with missing dates
# ---------------------------------------------------------

def test_availability_missing_information():
    response = client.post(
        "/chat",
        json={
            "message": "I need a room for 3 adults",
            "conversation": []
        }
    )

    assert response.status_code == 200
    assert response.json()["needs_availability"] is True


# ---------------------------------------------------------
# 6. Valid availability
# ---------------------------------------------------------

def test_valid_availability():
    response = client.post(
        "/availability",
        json={
            "check_in": "2026-09-20",
            "check_out": "2026-09-22",
            "adults": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["available"] is True
    assert len(data["rooms"]) == 2
    assert data["rooms"][0]["nights"] == 2
    assert data["rooms"][0]["total_price"] == 10000


# ---------------------------------------------------------
# 7. Invalid dates
# ---------------------------------------------------------

def test_invalid_availability_dates():
    response = client.post(
        "/availability",
        json={
            "check_in": "2026-09-22",
            "check_out": "2026-09-20",
            "adults": 3,
        },
    )

    assert response.status_code == 400
    assert "Check-out must be after check-in" in response.json()["detail"]


# ---------------------------------------------------------
# 8. Invalid guest count
# ---------------------------------------------------------

def test_invalid_guest_count():
    response = client.post(
        "/availability",
        json={
            "check_in": "2026-09-20",
            "check_out": "2026-09-22",
            "adults": 0,
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------
# 9. Unsupported question
# ---------------------------------------------------------

@patch("main.generate_response")
def test_unsupported_question(mock_generate):
    mock_generate.return_value = (
        "I don't have enough information in the hotel knowledge base "
        "to answer that reliably."
    )

    response = client.post(
        "/chat",
        json={
            "message": "What is the nearest airport?",
            "conversation": [],
        },
    )

    assert response.status_code == 200
    assert "don't have enough information" in response.json()["message"]


# ---------------------------------------------------------
# 10. Gemini failure fallback
# ---------------------------------------------------------

@patch("main.generate_response")
def test_gemini_failure_fallback(mock_generate):
    mock_generate.side_effect = Exception("Gemini unavailable")

    response = client.post(
        "/chat",
        json={
            "message": "Tell me something about the hotel",
            "conversation": [],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "fallback"
    assert "unable to process" in data["message"].lower()