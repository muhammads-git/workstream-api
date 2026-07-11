

class ConnectionManager:
   def __init__(self):
      self.active_connections = {}

   async def connect(self, user_id, websocket):
      await websocket.accept()
      self.active_connections[user_id] = websocket  # add user to connections

   def disconnect(self, user_id, websocket):
      self.active_connections.pop(user_id,None)   # remove from connections

   async def send_text_message(self, user_id,message):
      websocket = self.active_connections.get(user_id) # look up in phonebook
      if websocket:
         await websocket.send_text(message)  # send if found
         print(f"Message sent successfully to {user_id}")
      
      # if not found user is offline , save to db notifications
   
manager = ConnectionManager() # the connecton