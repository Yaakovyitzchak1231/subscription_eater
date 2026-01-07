from backend.parser import SubscriptionParser

def test_category_extraction():
    parser = SubscriptionParser()

    # Test cases
    assert parser._extract_category("Netflix", "Your subscription", "Body") == "Entertainment"
    assert parser._extract_category("Spotify", "Premium", "Body") == "Entertainment"
    assert parser._extract_category("GitHub", "Receipt", "Body") == "Software"
    assert parser._extract_category("Slack", "Invoice", "Body") == "Software"
    assert parser._extract_category("Unknown Service", "Your Netflix Subscription", "Body") == "Entertainment"
    assert parser._extract_category("Amazon", "Order", "Body") == "Shopping"

    # Test fallback
    assert parser._extract_category("Random Corp", "Invoice", "Body") == "Other"

def test_extract_category_priority():
    parser = SubscriptionParser()
    # Service name should take priority
    # If service is "Netflix" but body has "Amazon", it should still be Entertainment
    assert parser._extract_category("Netflix", "Amazon payment processed", "Body") == "Entertainment"
