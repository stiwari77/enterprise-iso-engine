import pytest
from sanitizer import sanitize_text
from extractor import process_ticket
from schemas import TicketExtraction

# 1. Test Dataset (Diverse edge cases with fake PII and error logs)
TEST_SAMPLES = [
    {
        "raw": "My database account password is SuperSecret123! and my email is admin@company.com. Please reset access.",
        "forbidden": ["SuperSecret123!", "admin@company.com"],
        "expected_category": "account_access"
    },
    {
        "raw": "CRITICAL: Redis cache cluster unreachable on port 6379. Call on-call engineer at +1 555-0199 or 555-0188.",
        "forbidden": ["555-0199", "555-0188"],
        "expected_category": "database"
    },
    {
        "raw": "API token sk_live_999999999999999999999999 was leaked. Revoke it immediately. Contact tech@org.io.",
        "forbidden": ["sk_live_999999999999999999999999", "tech@org.io"],
        "expected_category": "other"
    },
    {
        "raw": "Billing failure for card ending 4111111111111111. User email billing-dept@corp.com needs a receipt.",
        "forbidden": ["4111111111111111", "billing-dept@corp.com"],
        "expected_category": "billing"
    },
    {
        "raw": "Network latency spiking over VPN. Reach me at 555-9988 or support-agent@enterprise.net.",
        "forbidden": ["555-9988", "support-agent@enterprise.net"],
        "expected_category": "network"
    }
]


# 2. Test local PII Redaction
@pytest.mark.parametrize("sample", TEST_SAMPLES)
def test_sanitizer_redacts_all_pii(sample):
    clean_text = sanitize_text(sample["raw"])
    
    # Assert no forbidden original PII strings remain
    for item in sample["forbidden"]:
        assert item not in clean_text, f"PII Leak Detected! Found '{item}' in: {clean_text}"


# 3. Test End-to-End LLM Extraction and Schema Validation
@pytest.mark.parametrize("sample", TEST_SAMPLES)
def test_extractor_returns_valid_pydantic_schema(sample):
    result = process_ticket(sample["raw"])
    
    # Assert result is an instantiated TicketExtraction object
    assert isinstance(result, TicketExtraction)
    
    # Assert key fields are populated correctly
    assert result.category in ["database", "billing", "account_access", "network", "other"]
    assert result.urgency_level in ["low", "medium", "high", "critical"]
    assert isinstance(result.requested_actions, list)
    assert len(result.summary) > 0