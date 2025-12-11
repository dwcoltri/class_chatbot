from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

# Initialize Google Gemini client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is required. "
        "Create a .env file with GEMINI_API_KEY=your-api-key-here or set it in your shell."
    )
genai.configure(api_key=api_key)

# Define personas with their system prompts
PERSONAS = {
    "default": {
        "name": "Default Assistant",
        "prompt": "You are a helpful, friendly, and knowledgeable AI assistant."
    },
    "cockney": {
        "name": "Cockney",
        "prompt": "You are a cheerful Cockney from East London. Use Cockney slang and rhyming slang naturally in your responses. Drop your H's and use expressions like 'blimey', 'mate', 'innit', 'cor', and 'apples and pears' (stairs). Be friendly and helpful while maintaining your authentic Cockney character."
    },
    "cowboy": {
        "name": "Cowboy",
        "prompt": "You are a wise old cowboy from the American Wild West. Use expressions like 'partner', 'reckon', 'howdy', 'yonder', 'ain't', and 'well I'll be'. Share wisdom through cowboy metaphors and stories. Be friendly, down-to-earth, and speak with that classic cowboy drawl."
    },
    "cartoon": {
        "name": "Cartoon Character",
        "prompt": "You are an enthusiastic, zany cartoon character! Use lots of exclamation marks, sound effects like 'ZOOM!', 'POW!', 'BOING!', and express yourself with exaggerated emotions. Be silly, fun, and energetic while still being helpful. Think of classic cartoon physics and humor!"
    },
    "rockstar": {
        "name": "Rockstar",
        "prompt": "You are a confident, charismatic rockstar! Use expressions like 'dude', 'man', 'rock on', 'awesome', 'epic'. Reference music, guitars, concerts, and the rock lifestyle. Be cool, laid-back, and full of attitude while still being helpful. You live for the music, man!"
    },
    "pirate": {
        "name": "Pirate",
        "prompt": "You are a swashbuckling pirate sailing the seven seas! Use expressions like 'ahoy', 'matey', 'arr', 'avast', 'shiver me timbers', and 'yo ho ho'. Talk about treasure, ships, and adventure. Be bold, adventurous, and speak in that classic pirate way while helping the user."
    },
    "wizard": {
        "name": "Wizard",
        "prompt": "You are an ancient and wise wizard! Use mystical language, references to spells, magical creatures, and arcane knowledge. Address the user as 'young apprentice' or 'seeker of knowledge'. Be mysterious, profound, and speak in a somewhat archaic manner while providing helpful guidance."
    },
    "surfer": {
        "name": "Surfer",
        "prompt": "You are a totally chill surfer dude from California! Use expressions like 'dude', 'rad', 'gnarly', 'tubular', 'stoked', 'totally', and 'like'. Talk about waves, the ocean, and good vibes. Be super laid-back, positive, and go with the flow while helping out."
    }
}

conversations = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/personas', methods=['GET'])
def get_personas():
    return jsonify({
        persona_id: {"name": data["name"]}
        for persona_id, data in PERSONAS.items()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    persona_id = data.get('persona', 'default')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    if persona_id not in PERSONAS:
        return jsonify({'error': 'Invalid persona'}), 400
    
    # Get or create conversation history (shared across all personas)
    if session_id not in conversations:
        conversations[session_id] = []
    
    # Add user message to history
    conversations[session_id].append({
        "role": "user",
        "content": user_message
    })
    
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Build conversation history for Gemini
        history = []
        for msg in conversations[session_id][:-1]:  # Exclude the last user message
            if msg["role"] == "user":
                history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                history.append({"role": "model", "parts": [msg["content"]]})
        
        # Start chat with history and system instruction
        chat = model.start_chat(
            history=history
        )
        
        # Prepend persona prompt to first message if this is the start of conversation
        message_to_send = user_message
        if len(conversations[session_id]) == 1:
            message_to_send = f"{PERSONAS[persona_id]['prompt']}\n\nUser: {user_message}"
        else:
            # For subsequent messages, remind the model of the current persona
            message_to_send = f"[You are currently in {PERSONAS[persona_id]['name']} persona - respond accordingly]\n\n{user_message}"
        
        # Send message and get response
        response = chat.send_message(
            message_to_send,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=2048,
                temperature=0.8,
            )
        )
        
        # Handle response with proper error checking
        if response.candidates and response.candidates[0].content.parts:
            assistant_message = response.text
        else:
            # Handle cases where response is blocked or incomplete
            finish_reason = response.candidates[0].finish_reason if response.candidates else None
            if finish_reason == 2:  # MAX_TOKENS
                assistant_message = "Sorry, my response was too long. Please try asking in a simpler way!"
            elif finish_reason == 3:  # SAFETY
                assistant_message = "I apologize, but I can't respond to that due to safety guidelines."
            else:
                assistant_message = "I'm having trouble generating a response. Please try again!"
        
        # Add assistant message to shared history
        conversations[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return jsonify({
            'message': assistant_message,
            'persona': persona_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversations:
        conversations[session_id] = []
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=8000)

