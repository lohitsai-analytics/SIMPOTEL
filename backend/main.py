import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ChatRequest, AvailabilityRequest
from services.hotel_service import answer_from_knowledge_base, get_hotel_context
from services.availability_service import check_availability
from services.ai_service import generate_response

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hotel AI Guest Assistant",
    version="1.0.0",
)

# Local development plus the deployed Vercel frontend.
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Hotel AI Guest Assistant API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat")
def chat(request: ChatRequest):
    logger.info("Chat request received: %s", request.message)

    try:
        result = answer_from_knowledge_base(request.message)

        if result.get("handled", False):
            return result

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
        logger.exception("Chat processing failed.")
        return {
            "message": (
                "I'm unable to process that request right now. "
                "Please try again in a moment."
            ),
            "source": "fallback",
            "needs_availability": False,
            "handled": False,
        }


@app.post("/availability")
def availability(request: AvailabilityRequest):
    logger.info(
        "Availability request: %s -> %s for %s adults",
        request.check_in,
        request.check_out,
        request.adults,
    )

    try:
        return check_availability(
            check_in=request.check_in,
            check_out=request.check_out,
            adults=request.adults,
        )

    except ValueError as exc:
        logger.warning("Invalid availability request: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception:
        logger.exception("Availability check failed.")
        raise HTTPException(
            status_code=500,
            detail="Unable to check availability right now.",
        )
