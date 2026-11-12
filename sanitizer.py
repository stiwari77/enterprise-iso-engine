import re

def sanitize_text(raw_text: str) -> str:
    """
    Scans raw input text and redacts sensitive PII (API keys, credit cards, emails, phone numbers, passwords)
    using ordered regex patterns.
    """
    cleaned_text = raw_text

    # 1. Redact Passwords (catches "password is XYZ!", "pwd: XYZ", "pass=XYZ")
    password_pattern = r'(?i)\b(password|pass|pwd)\b\s*[:=is]+\s*([^\s,.]+)'
    cleaned_text = re.sub(password_pattern, r'\1 is <PASSWORD>', cleaned_text)

    # 2. Redact API Keys / Secrets (e.g., sk_live_...)
    api_key_pattern = r'\b(sk_[a-zA-Z0-9_\-]+|ghp_[a-zA-Z0-9_\-]+|AKIA[0-9A-Z]{16})\b'
    cleaned_text = re.sub(api_key_pattern, '<API_KEY>', cleaned_text)

    # 3. Redact Email Addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    cleaned_text = re.sub(email_pattern, '<EMAIL_ADDRESS>', cleaned_text)

    # 4. Redact Credit Card Numbers (13 to 16 continuous digits)
    card_pattern = r'\b\d{13,16}\b'
    cleaned_text = re.sub(card_pattern, '<CREDIT_CARD>', cleaned_text)

    # 5. Redact Phone Numbers (3 digits - 4 digits OR standard 10-digit formats)
    phone_pattern = r'\b(\+?\d{1,3}[\s\.-]?)?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{4}\b|\b\d{3}-\d{4}\b'
    cleaned_text = re.sub(phone_pattern, '<PHONE_NUMBER>', cleaned_text)

    return cleaned_text


if __name__ == "__main__":
    sample_ticket = (
        "Hi team, my password is SuperSecret123! and my API key is sk_live_999999999999999999999999. "
        "Please call me at 555-0199 or email user@company.com. Card ends in 4111111111111111."
    )
    
    print("--- RAW TEXT ---")
    print(sample_ticket)
    
    print("\n--- SANITIZED TEXT ---")
    print(sanitize_text(sample_ticket))