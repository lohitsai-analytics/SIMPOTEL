import os
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_response(user_message, hotel_context, conversation=None):
    """
    Generate a grounded response using Gemini.

    Conversation history is included so that follow-up questions
    can refer to previous messages.
    """

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not configured.")
        return (
            "I'm unable to connect to the AI assistant right now. "
            "Please try again shortly."
        )

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        system_instruction = f"""
You are the AI guest assistant for Grand Horizon Hotel.

Answer guest questions using ONLY the hotel information below.

HOTEL INFORMATION:
{hotel_context}

RULES:
1. Never invent hotel information.
2. Never invent prices, facilities, policies, addresses, or services.
3. Never invent room availability.
4. If information is not present, say that you don't have that information.
5. Use previous conversation messages to understand follow-up questions.
6. If the guest uses words such as "it", "they", "that", or "this",
   use the conversation history to determine what they are referring to.
7. Keep answers concise, friendly, and useful.
8. Room availability is handled by the backend availability system.
"""

        final_input = user_message

        if conversation:
            history = []

            for message in conversation[-10:]:
                # ChatMessage is a Pydantic model
                role = getattr(message, "role", "user")
                content = getattr(message, "content", "")

                if content:
                    history.append(f"{role.upper()}: {content}")

            if history:
                conversation_text = "\n".join(history)

                final_input = f"""
Previous conversation:
{conversation_text}

Current guest question:
{user_message}
"""

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=final_input,
            system_instruction=system_instruction,
        )

        response = interaction.output_text

        if not response:
            logger.warning("Gemini returned an empty response.")
            return (
                "I couldn't generate a reliable answer right now. "
                "Please try again."
            )

        return response

    except Exception:
        logger.exception("Gemini request failed.")

        return (
            "I'm having trouble connecting to the AI assistant right now. "
            "Please try again in a moment."
        )