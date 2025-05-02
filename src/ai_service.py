# Service for interacting with the AI model (e.g., OpenAI)

import openai
from .config import settings
from .models import Message, User # To potentially use message history and user profile
from sqlalchemy.orm import Session
from .db_manager import get_user_messages, get_user_by_whatsapp_id # To fetch conversation history and user profile
import json

# Configure OpenAI client
if settings.OPENAI_API_KEY:
    # Consider using async client if available and beneficial
    # from openai import AsyncOpenAI
    # client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
else:
    print("WARNING: OPENAI_API_KEY not found in environment variables. AI service will not function.")
    client = None

# --- Enhanced System Prompt --- (Can be further refined)
SYSTEM_PROMPT = """
You are ShopperGPT, a friendly, expert, and highly personalized AI shopping assistant operating on WhatsApp.
Your goal is to provide an exceptional, human-like customer service experience, making online shopping easier and more enjoyable.

Key characteristics:
- Conversational & Engaging: Chat naturally, understand nuances, and maintain context.
- Personalized: Leverage user profile (style, budget), past interactions, and stated needs (occasion, mood if mentioned).
- Knowledgeable: Possess broad knowledge of fashion, electronics, gifts, trends, etc.
- Helpful & Proactive: Offer relevant suggestions, comparisons, and alerts (e.g., price drops on wishlist - future feature).
- Trustworthy: Explain recommendations briefly if asked. Respect user privacy.
- Action-Oriented: Guide users towards making a purchase decision by providing clear product info and affiliate links when available.

Interaction Flow:
1. Understand the user's request (product search, gift idea, outfit building, comparison, etc.).
2. Ask clarifying questions if needed (budget, specific features, occasion, recipient details for gifts).
3. Access user profile and conversation history for context.
4. Generate relevant product recommendations or advice.
5. (Future) Integrate affiliate links and product details (images, price) fetched from external APIs/DB.
6. Handle feedback like "show me more", "cheaper options", "add to wishlist".

Constraint: Do not invent products or prices. If you need product details, state that you will look them up (integration pending).
Constraint: Always prioritize the user's stated needs and preferences.
Constraint: Keep responses concise and suitable for WhatsApp chat format.
"""

async def get_ai_response(user_id: int, user_message: str, db: Session) -> str:
    """Gets a response from the AI model based on the user message, profile, and context."""
    if not client:
        return "Desculpe, o serviço de IA não está configurado corretamente."

    try:
        # 1. Fetch User Profile (Optional, but useful for personalization)
        # user = get_user_by_whatsapp_id(db, whatsapp_id=...) # Need whatsapp_id here, maybe pass it?
        # For now, we only have user_id
        # user_profile_info = f"User Profile: Style={user.style_preferences}, Budget={user.budget_range}" # Example

        # 2. Fetch & Prepare Conversation History
        history_messages = get_user_messages(db, user_id, limit=20) # Increase limit slightly
        history_messages.reverse() # Order from oldest to newest

        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT}
            # Add user profile info here if available and relevant
            # {"role": "system", "content": user_profile_info}
        ]

        # Simple context window management: Add messages until near token limit
        # A more robust approach would use token counting (e.g., tiktoken library)
        # For now, limit message count
        max_history = 10 # Limit to last 5 back-and-forths approx
        start_index = max(0, len(history_messages) - max_history)

        for msg in history_messages[start_index:]:
            role = "user" if msg.sender == "user" else "assistant"
            conversation.append({"role": role, "content": msg.content})

        # Add the current user message
        conversation.append({"role": "user", "content": user_message})

        # 3. Call OpenAI API
        print(f"\n--- Sending to OpenAI for user {user_id} ---")
        # print(json.dumps(conversation, indent=2))
        print(f"Current User Message: {user_message}")
        print(f"History length: {len(conversation) - 1} messages")
        print("-------------------------------------\n")

        # Using await client.chat.completions.create if using async client
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Using a more recent/capable model if budget allows
            messages=conversation,
            max_tokens=300, # Increased slightly for potentially more detailed answers
            temperature=0.6, # Slightly lower for more focused responses
            # Add other parameters like frequency_penalty, presence_penalty if needed
        )

        ai_message = response.choices[0].message.content.strip()
        usage = response.usage
        print(f"\n--- OpenAI Response --- ({usage.total_tokens} tokens used)")
        print(ai_message)
        print("----------------------\n")

        return ai_message

    except openai.AuthenticationError:
        print("ERROR: OpenAI Authentication failed. Check your API key.")
        return "Desculpe, houve um problema de autenticação com o serviço de IA."
    except openai.RateLimitError:
        print("ERROR: OpenAI Rate Limit exceeded.")
        return "Desculpe, estou recebendo muitas solicitações no momento. Tente novamente em breve."
    except openai.APIError as e:
        print(f"ERROR: OpenAI API Error: {e}")
        return "Desculpe, houve um problema com o serviço de IA. Tente novamente mais tarde."
    except Exception as e:
        print(f"ERROR: Unexpected error in get_ai_response: {e}")
        # Consider logging the full traceback here
        return "Desculpe, não consegui processar sua solicitação no momento devido a um erro inesperado."

# Placeholder for future enhancements like visual recognition, context integration (weather, etc.)

