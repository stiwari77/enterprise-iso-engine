import requests
import json

# Curated test benchmark across diverse enterprise incident scenarios
TEST_CASES = [
    {
        "raw_text": "CRITICAL: Production database down on billing-svc! Transactions failing across checkout.",
        "expected_category": "database",
        "expected_urgency": "CRITICAL",
        "expected_team": "Database Reliability Engineering"
    },
    {
        "raw_text": "Users are unable to log in via SSO due to OAuth token timeout on authentication gateway.",
        "expected_category": "account_access",
        "expected_urgency": "HIGH",
        "expected_team": "Identity & Access Management"
    },
    {
        "raw_text": "Low priority: Please update the team documentation for the new internal API endpoint release.",
        "expected_category": "other",
        "expected_urgency": "LOW",
        "expected_team": "Tier-1 Support Operations"
    },
    {
        "raw_text": "WARNING: Memory utilization on payment processing worker nodes has crossed 92%.",
        "expected_category": "billing",
        "expected_urgency": "HIGH",
        "expected_team": "Finance Operations"
    }
]

def run_evaluation():
    """Runs automated extraction and routing validation against the FastAPI backend."""
    print("🚀 Starting Enterprise ISO Engine Evaluation Suite...\n")
    passed = 0
    total = len(TEST_CASES)

    for i, test in enumerate(TEST_CASES, 1):
        try:
            res = requests.post(
                "http://127.0.0.1:8000/tickets", 
                json={"raw_text": test["raw_text"]}
            )
            
            if res.status_code != 201:
                print(f"❌ Test {i} failed with status code {res.status_code}: {res.text}")
                continue
            
            data = res.json()
            
            # Evaluate field accuracy
            cat_match = data["category"].lower() == test["expected_category"].lower()
            urg_match = data["urgency_level"].upper() == test["expected_urgency"].upper()
            team_match = data["target_team"].lower() == test["expected_team"].lower()

            if cat_match and urg_match and team_match:
                print(f"✅ Test {i} PASSED: [{data['ticket_id']}] -> Routed to {data['target_team']}")
                passed += 1
            else:
                print(f"❌ Test {i} FAILED:")
                print(f"   Input:    {test['raw_text']}")
                print(f"   Expected: Category={test['expected_category']}, Urgency={test['expected_urgency']}, Team={test['expected_team']}")
                print(f"   Got:      Category={data['category']}, Urgency={data['urgency_level']}, Team={data['target_team']}")
                
        except Exception as e:
            print(f"❌ Test {i} encountered an exception: {e}")

    accuracy = (passed / total) * 100
    print("\n" + "=" * 50)
    print(f"📊 Evaluation Complete: {passed}/{total} tests passed ({accuracy:.1f}% Accuracy)")
    print("=" * 50)

if __name__ == "__main__":
    run_evaluation()