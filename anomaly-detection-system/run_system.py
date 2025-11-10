"""
Main entry point for the Anomaly Detection System.
Starts the FastAPI backend server.
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from backend.utils.config import get_settings

    settings = get_settings()

    print("=" * 60)
    print("Starting Anomaly Detection System")
    print("=" * 60)
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")
    print(f"Debug Mode: {settings.debug}")
    print("=" * 60)
    print("\nAccess the API at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print("\nPress CTRL+C to stop the server\n")

    uvicorn.run(
        "backend.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
