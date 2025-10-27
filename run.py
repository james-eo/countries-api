#!/usr/bin/env python3
"""
Railway startup script for Country API
"""
import os
import uvicorn

def main():
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🚀 Starting Country API on {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug
    )

if __name__ == "__main__":
    main()