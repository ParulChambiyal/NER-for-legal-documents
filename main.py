import google.generativeai as genai

# Replace 'your-gemini-api-key' with your actual Gemini API key
api_key = "AIzaSyDPf-_j6vVw1i83CggXuVJQDxByJE5jssA"

# Configure the API key
genai.configure(api_key=api_key)

# Create the model
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  safety_settings=safety_settings,
  generation_config=generation_config,
  system_instruction="Find entities from the Hindi text among the following entities: . Just mark the entities presnt only,dont give explanation why you set that entity.give which word is which entity ",
)

# Start a chat session
chat_session = model.start_chat(
    history=[]
)

print("Bot: Hello, how can I help you?")
print()

while True:
    user_input = input("You: ")
    print()

    response = chat_session.send_message(user_input)
    model_response = response.text

    print(f'Bot: {model_response}')
    print()

    chat_session.history.append({"role": "user", "parts": [user_input]})
    chat_session.history.append({"role": "model", "parts": [model_response]})