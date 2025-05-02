# Handles incoming WhatsApp messages and sends replies

import requests
import json
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from .config import settings
from .models import WhatsAppWebhookPayload, User, Message
from .db_manager import get_db, get_user_by_whatsapp_id, create_user, create_message
from .ai_service import get_ai_response
# Import recommendation engine (ensure it exists)
try:
    from .recommendation_engine import get_recommendations, RecommendedProduct
except ImportError:
    print("WARNING: Recommendation engine not found or has issues. Recommendations disabled.")
    # Define a dummy function/class if import fails to avoid runtime errors later
    class RecommendedProduct:
        def __init__(self, **kwargs): pass
    def get_recommendations(*args, **kwargs) -> list:
        return []

async def verify_webhook(request: Request):
    """Verifies the webhook subscription with WhatsApp."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return int(challenge)
        else:
            print("VERIFICATION_FAILED")
            raise HTTPException(status_code=403, detail="Verification token mismatch")
    else:
        raise HTTPException(status_code=400, detail="Missing mode or token")

async def handle_message(payload: WhatsAppWebhookPayload, db: Session = Depends(get_db)):
    """Processes incoming WhatsApp messages from the webhook."""
    print("Received webhook payload:", payload.model_dump_json(indent=2))

    if payload.entry and payload.entry[0].changes:
        change = payload.entry[0].changes[0]
        if change.value and change.value.messages:
            message_data = change.value.messages[0]

            if message_data.get("type") == "text":
                phone_number_id = change.value.metadata.get("phone_number_id")
                from_number = message_data.get("from")
                whatsapp_message_id = message_data.get("id")
                msg_body = message_data.get("text", {}).get("body")
                timestamp = message_data.get("timestamp")
                profile_name = change.value.contacts[0].get("profile", {}).get("name") if change.value.contacts else from_number
                whatsapp_user_id = change.value.contacts[0].get("wa_id") if change.value.contacts else from_number

                if not msg_body or not whatsapp_user_id:
                    print("Ignoring message: Missing body or user ID")
                    return {"status": "ignored", "reason": "Missing body or user ID"}

                print(f"Processing message from {profile_name} ({whatsapp_user_id}): {msg_body}")

                user = get_user_by_whatsapp_id(db, whatsapp_id=whatsapp_user_id)
                if not user:
                    print(f"Creating new user for {whatsapp_user_id}")
                    user = create_user(db, phone_number=from_number, whatsapp_id=whatsapp_user_id)

                create_message(db, user_id=user.id, whatsapp_message_id=whatsapp_message_id, content=msg_body, sender="user")

                ai_reply = await get_ai_response(user_id=user.id, user_message=msg_body, db=db)

                create_message(db, user_id=user.id, whatsapp_message_id=f"ai_{whatsapp_message_id}", content=ai_reply, sender="assistant")

                # Check if recommendations might be relevant based on AI response keywords
                recommendations = []
                recommendation_keywords = ["recomendo", "sugestões", "opções", "produtos", "encontrei", "alternativas"]
                if any(keyword in ai_reply.lower() for keyword in recommendation_keywords):
                    print("AI response suggests recommendations might be needed. Calling recommendation engine.")
                    recommendation_query = msg_body # Use user message as query for now
                    try:
                        # Pass the actual user object
                        recommendations = get_recommendations(user=user, query=recommendation_query, db=db, num_recommendations=2)
                    except Exception as e:
                        print(f"Error calling recommendation engine: {e}")

                # Send the main AI reply first
                send_whatsapp_message(to=from_number, message_body=ai_reply)

                # Send recommendations if any (as separate messages)
                if recommendations:
                    print(f"Sending {len(recommendations)} recommendations...")
                    for product in recommendations:
                        # Basic text format - Enhance with WhatsApp formatting or templates later
                        product_message = (
                            f"*{product.name}*\n"
                            f"Preço: {product.price}\n"
                            # f"{product.description}\n" # Keep it concise for chat
                            f"Link: {product.affiliate_link}"
                            # Add image URL if possible/desired: f"\nImagem: {product.image_url}"
                        )
                        send_whatsapp_message(to=from_number, message_body=product_message)
                else:
                    print("No recommendations generated or triggered.")

                return {"status": "processed"}
            else:
                print(f'Ignoring non-text message type: {message_data.get("type")}')
                return {"status": "ignored", "reason": "Non-text message"}
        elif change.value and change.value.statuses:
            print(f"Received status update: {change.value.statuses[0]}")
            return {"status": "status_update_received"}

    print("Ignoring webhook event: Not a message or status update")
    return {"status": "ignored", "reason": "Not a message or status update"}

def send_whatsapp_message(to: str, message_body: str):
    """Sends a text message via the WhatsApp Cloud API."""
    if not settings.WHATSAPP_API_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        print("ERROR: WhatsApp API Token or Phone Number ID not configured. Cannot send message.")
        return None

    url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message_body},
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Message sent to {to}. Status: {response.status_code}. Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to send WhatsApp message to {to}: {e}")
        if e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while sending WhatsApp message: {e}")
        return None

# Add functions to send other message types (images, buttons, lists) as needed

