# AI Chatbot with Multiple Personas

A general-purpose AI chatbot with 8 unique personalities! Chat with a Cockney from East London, a Wild West cowboy, a mystical wizard, and more - all powered by Google's **free** Gemini API.

## Quick Start

### 1. Get a Free Gemini API Key

Visit: **https://aistudio.google.com/app/apikey**

- Sign in with your Google account
- Click "Create API Key"
- Copy the key

### 2. Set up your API key

Create a `.env` file in the project directory:
```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

Or set it as an environment variable:
```bash
export GEMINI_API_KEY='your-api-key-here'
```

### 3. Install uv (if needed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on macOS with Homebrew:
```bash
brew install uv
```

### 4. Run the chatbot
```bash
uv run app.py
```

### 5. Open your browser
Go to: **http://localhost:8000**

That's it! `uv` automatically handles dependencies, virtual environments, and Python versions.

## Usage

1. **Select a persona** from the sidebar
2. **Type your message** in the text area at the bottom
3. **Press Enter** or click "Send" to chat
4. **The AI responds** in the selected persona's style
5. **Switch personas** anytime - they all remember your conversation!
6. **Click "Clear Chat"** to start a fresh conversation

---

## Configuration

### Adding New Personas

Edit the `PERSONAS` dictionary in `app.py`:

```python
"your_persona_id": {
    "name": "Your Persona Name",
    "prompt": "System prompt describing the persona's personality and speech patterns..."
}
```

### Changing the AI Model

Modify the model name in the `chat()` function in `app.py`:

```python
model = genai.GenerativeModel('gemini-2.5-flash')  # Or 'gemini-2.5-pro' for more capability
```

---

## Technologies Used

- **Backend**: Flask (Python)
- **AI**: Google Gemini API (Free!)
- **Package Manager**: uv (fast, modern Python package manager)
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Modern CSS with gradients and animations

---

## Troubleshooting

### Missing API key error?
Make sure you've set your Gemini API key in a `.env` file:
```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```