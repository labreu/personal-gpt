import os
import json
import uuid
from datetime import datetime
from litellm import completion

class ChatManager:
    def __init__(self):
        self.chats_dir = "chats"
        os.makedirs(self.chats_dir, exist_ok=True)
        # Define supported models
        self.supported_models = {
            "gpt-4o-mini-2024-07-18": "GPT-4 Mini",
            "gpt-3.5-turbo": "GPT-3.5 Turbo"
        }

    def get_available_models(self):
        """Return list of available models"""
        return [{"id": k, "name": v} for k, v in self.supported_models.items()]

    def send_message(self, message, model, chat_id=None):
        if not chat_id:
            chat_id = str(uuid.uuid4())
        
        chat_data = self._load_chat(chat_id)
        messages = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in chat_data["messages"]
        ]
        messages.append({"role": "user", "content": message})

        try:
            response = completion(
                model=model,  # Use the model ID directly
                messages=messages,
                api_key=os.getenv("API_KEY")
            )
            
            assistant_message = response.choices[0].message.content

            # Save messages to chat history
            chat_data["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "model": model
            })
            chat_data["messages"].append({
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.now().isoformat(),
                "model": model
            })
            
            self._save_chat(chat_id, chat_data)
            
            return {
                "chatId": chat_id,
                "response": assistant_message,
                "model": model
            }
        except Exception as e:
            print(f"Error calling LiteLLM: {str(e)}")
            return {
                "chatId": chat_id,
                "response": f"Sorry, there was an error processing your request: {str(e)}",
                "error": True
            }

    def get_all_chats(self):
        chats = []
        for filename in os.listdir(self.chats_dir):
            if filename.endswith(".txt"):
                chat_id = filename[:-4]
                chat_data = self._load_chat(chat_id)
                chats.append({
                    "id": chat_id,
                    "messages": chat_data["messages"]
                })
        return chats

    def delete_chat(self, chat_id):
        filepath = os.path.join(self.chats_dir, f"{chat_id}.txt")
        if os.path.exists(filepath):
            os.remove(filepath)

    def _load_chat(self, chat_id):
        filepath = os.path.join(self.chats_dir, f"{chat_id}.txt")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {"messages": []}

    def _save_chat(self, chat_id, chat_data):
        filepath = os.path.join(self.chats_dir, f"{chat_id}.txt")
        with open(filepath, 'w') as f:
            json.dump(chat_data, f, indent=2) 