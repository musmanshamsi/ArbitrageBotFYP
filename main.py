import uvicorn
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("\n" + "="*40)
    print("🚀 ARBPRO CORE SYSTEM STARTING")
    print("="*40)
    
    # Run the FastAPI app defined in api.py
    # reload=True is great for dev, but set to False in production
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)