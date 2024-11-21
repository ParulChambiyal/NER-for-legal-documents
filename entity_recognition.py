import google.generativeai as genai

def extract_entities_from_text(input_text, api_key):
    """
    Extracts entities from the given text using the Gemini API.

    Parameters:
        input_text (str): The input text for entity extraction.
        api_key (str): Your Gemini API key.

    Returns:
        str: Extracted entities in text format.
    """
    # Configure the Gemini API
    genai.configure(api_key=api_key)  

    # Set generation parameters
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    # Initialize the Gemini model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=(
            "Find entities from the Hindi text among the following entities: "
            "Just mark the entities present only, don't give an explanation for why you set that entity. "
            "Give which word is which entity."
        ),
    )

    # Send the input text for entity extraction
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(input_text)

    return response.text  # Return the response text
