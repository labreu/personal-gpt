from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from .chat_manager import ChatManager

load_dotenv()

app = Flask(__name__)
chat_manager = ChatManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message')
    model = data.get('model')
    chat_id = data.get('chatId')
    
    response = chat_manager.send_message(message, model, chat_id)
    return jsonify(response)

@app.route('/api/get_chats', methods=['GET'])
def get_chats():
    chats = chat_manager.get_all_chats()
    return jsonify(chats)

@app.route('/api/delete_chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    chat_manager.delete_chat(chat_id)
    return jsonify({"status": "success"})

@app.route('/api/models', methods=['GET'])
def get_models():
    models = chat_manager.get_available_models()
    return jsonify(models)

if __name__ == '__main__':
    app.run(debug=True) 