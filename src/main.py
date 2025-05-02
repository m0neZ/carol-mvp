from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from . import models, db_manager, whatsapp_handler, config
from .admin_routes import router as admin_router # Import the admin router

# Initialize database (create tables if they don't exist)
# In a production scenario, use migrations (e.g., Alembic)
db_manager.init_db()

app = FastAPI(
    title=config.settings.PROJECT_NAME,
    version=config.settings.VERSION,
    description="AI Personal Shopper Assistant on WhatsApp"
)

# Include the admin router
app.include_router(admin_router)

@app.get("/health", tags=["Health Check"])
async def health_check():
    """Checks if the API is running."""
    return {"status": "ok", "version": config.settings.VERSION}

# --- WhatsApp Webhook Endpoints ---

@app.get("/whatsapp/webhook", tags=["WhatsApp"])
async def verify_whatsapp_webhook(request: Request):
    """Handles WhatsApp webhook verification requests."""
    # Delegate verification logic to the handler module
    try:
        challenge = await whatsapp_handler.verify_webhook(request)
        # Return challenge as plain text integer for WhatsApp verification
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=str(challenge))
    except HTTPException as e:
        raise e # Re-raise HTTP exceptions from the handler
    except Exception as e:
        print(f"Error during webhook verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during verification")

@app.post("/whatsapp/webhook", tags=["WhatsApp"])
async def receive_whatsapp_message(payload: models.WhatsAppWebhookPayload, background_tasks: BackgroundTasks, db: Session = Depends(db_manager.get_db)):
    """Receives messages and events from WhatsApp webhook."""
    # Process the message in the background to respond quickly to WhatsApp
    background_tasks.add_task(whatsapp_handler.handle_message, payload, db)
    # Acknowledge receipt immediately
    return {"status": "received"}


# --- Application Startup/Shutdown Events (Optional) ---
@app.on_event("startup")
async def startup_event():
    print("ShopperGPT API starting up...")
    # Perform any startup tasks if needed

@app.on_event("shutdown")
async def shutdown_event():
    print("ShopperGPT API shutting down...")
    # Perform any cleanup tasks if needed

# --- Run Instruction (for local development) ---
# To run locally: uvicorn src.main:app --host 0.0.0.0 --port=int(os.getenv("PORT", 8000)) --reload --app-dir /home/ubuntu/shoppergpt
# Ensure .env file is present in /home/ubuntu/shoppergpt/

