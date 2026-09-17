import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ChatRequest, AvailabilityRequest

from services.hotel_service import (
    answer_from_knowledge_base,
    get_hotel_context,
)

from services.availability_service import check_availability
from services.ai_service import generate_response


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="Hotel AI Guest Assistant",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Hotel AI Guest Assistant API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    logger.info(
        "Chat request received: %s",
        request.message
    )

    try:

        # -------------------------------------------------
        # STEP 1:
        # Try deterministic hotel knowledge first.
        # -------------------------------------------------

        result = answer_from_knowledge_base(
            request.message
        )

        # -------------------------------------------------
        # STEP 2:
        # If the knowledge base handled the request,
        # return immediately.
        #
        # This includes:
        # - Check-in
        # - Check-out
        # - Swimming pool
        # - Gym
        # - Wi-Fi
        # - Parking
        # - Breakfast
        # - Cancellation
        # - Room suitability
        # - Availability flow
        # -------------------------------------------------

        if result.get("handled", False):
            return result

        # -------------------------------------------------
        # STEP 3:
        # If the deterministic knowledge base cannot answer,
        # use Gemini.
        #
        # Gemini is only used for natural-language reasoning
        # and conversational questions.
        # -------------------------------------------------

        answer = generate_response(
            request.message,
            get_hotel_context(),
            request.conversation,
        )

        return {
            "message": answer,
            "source": "gemini",
            "needs_availability": False,
            "handled": True,
        }

    except Exception:
        logger.exception(
            "Chat processing failed."
        )

        # -------------------------------------------------
        # FINAL FALLBACK
        # -------------------------------------------------

        return {
            "message": (
                "I'm unable to process that request right now. "
                "Please try again in a moment."
            ),
            "source": "fallback",
            "needs_availability": False,
            "handled": False,
        }


# =========================================================
# AVAILABILITY
# =========================================================

@app.post("/availability")
def availability(request: AvailabilityRequest):

    logger.info(
        "Availability request: %s -> %s for %s adults",
        request.check_in,
        request.check_out,
        request.adults,
    )

    try:

        # -------------------------------------------------
        # Deterministic availability logic
        # -------------------------------------------------

        result = check_availability(
            check_in=request.check_in,
            check_out=request.check_out,
            adults=request.adults,
        )

        return result

    except ValueError as exc:

        # -------------------------------------------------
        # Validation error
        # -------------------------------------------------

        logger.warning(
            "Invalid availability request: %s",
            exc,
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:

        # -------------------------------------------------
        # Unexpected server error
        # -------------------------------------------------

        logger.exception(
            "Availability check failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to check availability right now.",
        )