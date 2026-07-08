# from fastapi import websockets
# import websocket


class ConnectionManager:
   def __init__(self):
      self.active_connections = {}

   async def connect(self, user_id, websocket):
      await websocket.accept()
      self.active_connections[user_id] = websocket  # add user to connections

   def disconnect(self, user_id, websocket):
      self.active_connections.pop(user_id,None)   # remove from connections

   async def send_text_message(self, user_id,message):

      print(f"Looking up user_id: {user_id}, type: {type(user_id)}")
      print(f"Active connections keys: {list(self.active_connections.keys())}")
      print(f"Key types: {[type(k) for k in self.active_connections.keys()]}")
      print(f'Sending message to: {user_id}')
      print(f'Active connection: {user_id}')
      websocket = self.active_connections.get(user_id) # look up in phonebook
      if websocket:
         await websocket.send_text(message)  # send if found
         print(f"Message sent successfully to {user_id}")
      
      # if not found user is offline , save to db notifications
   
manager = ConnectionManager() # the connecton