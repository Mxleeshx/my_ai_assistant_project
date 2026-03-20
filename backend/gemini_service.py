import os
import tempfile
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing! Check your .env file.")

client = genai.Client(api_key=API_KEY)


def get_gemini_response(history_contents, prompt, file_bytes=None, mime_type=None):
    contents = []

    # Safely parse the existing history to ensure strict SDK typing
    for msg in history_contents:
        msg_parts = []
        for p in msg.get("parts", []):
            if isinstance(p, str):
                msg_parts.append(types.Part.from_text(text=p))
            elif isinstance(p, dict) and "text" in p:
                msg_parts.append(types.Part.from_text(text=p["text"]))
            else:
                msg_parts.append(p)  # Fallback for already correct objects

        contents.append(types.Content(role=msg.get("role"), parts=msg_parts))

    parts = []

    # Handle file attachments
    if file_bytes and mime_type:
        if "image" in mime_type:
            parts.append(
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type
                )
            )
        elif "pdf" in mime_type:
            # Temp file for PDF upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file_bytes)
                temp_path = temp_file.name

            # Upload to Google's servers (Returns a File object)
            uploaded_file = client.files.upload(file=temp_path)

            # THE FIX: Explicitly convert the File object into a Part object
            parts.append(
                types.Part.from_uri(
                    file_uri=uploaded_file.uri,
                    mime_type=uploaded_file.mime_type
                )
            )

            os.unlink(temp_path)  # Clean up the temp file

    # Add the text prompt
    parts.append(
        types.Part.from_text(text=prompt)
    )

    # Append the current combined user message to the history
    contents.append(
        types.Content(role="user", parts=parts)
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I encountered an error trying to process that. Please try again."