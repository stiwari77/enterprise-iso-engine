import os
from dotenv import load_dotenv
import instructor
from openai import OpenAI
from schemas import TicketExtraction
from sanitizer import sanitize_text

# 1. Load the secret API key from .env
load_dotenv()

# 2. Explicitly pass mode=instructor.Mode.TOOLS to avoid fallback warnings
client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")), mode=instructor.Mode.TOOLS)

def process_ticket(raw_text: str) -> TicketExtraction:
    """
    Sanitizes raw ticket text locally, then passes the clean text 
    to the LLM to extract structured data using our schema.
    """
    # Sanitize PII locally using our regex sanitizer
    clean_text = sanitize_text(raw_text)
    
    # Send sanitized text to OpenAI with our Pydantic schema
    extracted_data = client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=TicketExtraction,
        messages=[
            {
                "role": "system",
                "content": "You are an enterprise incident routing assistant. Extract key incident details from the request."
            },
            {
                "role": "user",
                "content": clean_text
            }
        ]
    )
    
    return extracted_data


if __name__ == "__main__":
    sample_raw_ticket = (
        "URGENT! Our production PostgreSQL database is crashing with OutOfMemory errors. "
        "Can someone restart the DB cluster? Contact me at 555-0199 or email dev@company.com."
    )
    
    print("--- PROCESSING TICKET THROUGH LLM ---")
    result = process_ticket(sample_raw_ticket)
    
    print("\n--- EXTRACTED STRUCTURED OUTPUT ---")
    print(f"Category:          {result.category}")
    print(f"Urgency Level:     {result.urgency_level}")
    print(f"Requested Actions: {result.requested_actions}")
    print(f"Summary:           {result.summary}")