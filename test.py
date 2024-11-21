import google.generativeai as genai

api_key = "AIzaSyDPf-_j6vVw1i83CggXuVJQDxByJE5jssA"

# Configure the API key
genai.configure(api_key=api_key)

def extract_entities_from_text(input_text):
    generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=(
            "Find entities from the Hindi text among the following entities: "
            "Just mark the entities present only, don't give an explanation for why you set that entity. "
            "Give which word is which entity."
        ),
    )

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(input_text)
    return response.text