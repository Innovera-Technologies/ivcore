# app/dependencies/ws_auth.py
import os
from fastapi import WebSocket, WebSocketException, status

WEBSOCKET_AUTH_TOKEN = os.getenv("WEBSOCKET_AUTH_TOKEN", "changeme")

async def websocket_auth(websocket: WebSocket):
    token = websocket.headers.get("Authorization")

    if not token or token != f"Bearer {WEBSOCKET_AUTH_TOKEN}":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
