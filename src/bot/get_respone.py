def genarate_response(user_prompt):

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        client = genai.Client(api_key=api_key)
    except ValueError as e:
        print(f"Configuration error: {e}")
        exit()
    
    try:
        response = client.models.generate_content(model="gemini-3-flash-preview", 
        contents= user_prompt)
    except ValueError as e:
        print (e)
        exit()
    
   # analysis_result = analysis_result + "\n" +response.text
    return("Gemini: " + response.text)


def transform_history(messages):
    for m in messages:
        if m["role"] == "assistant":
            return(m["content"])