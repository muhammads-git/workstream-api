import websocket

def on_message(ws, message):
    print(f"NOTIFICATION: {message}")

def on_open(ws):
    print("Connected! Waiting for notifications...")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status, close_msg):
    print("Connection closed")

ws = websocket.WebSocketApp(
    "ws://localhost:8001/ws/5",  # your user_id
    on_message=on_message,
    on_open=on_open,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
