import re
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SubscriptionParser:
    """
    Parses email content to extract subscription details using heuristics/regex.
    Designed to be extensible for LLM integration.
    """

    CURRENCY_SYMBOLS = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "USD": "USD",
        "EUR": "EUR",
        "GBP": "GBP"
    }

    # Regex patterns for cost extraction
    COST_PATTERNS = [
        r'total\s*(?:price|cost|amount)?\s*[:\-\s]*\s*([$€£])\s*(\d+(?:\.\d{2})?)',  # Total: $10.99
        r'charged\s*[:\-\s]*\s*([$€£])\s*(\d+(?:\.\d{2})?)',                         # Charged $10.99
        r'([$€£])\s*(\d+(?:\.\d{2})?)\s*(?:was|has been)\s*charged',                 # $10.99 was charged
        r'amount\s*[:\-\s]*\s*([$€£])\s*(\d+(?:\.\d{2})?)',                          # Amount: $10.99
        r'renew(?:al)?\s*price\s*[:\-\s]*\s*([$€£])\s*(\d+(?:\.\d{2})?)',            # Renewal price: $10.99
        r'price\s*[:\-\s]*\s*([$€£])\s*(\d+(?:\.\d{2})?)',                           # Price: $10.99
    ]

    CYCLE_PATTERNS = {
        "monthly": [r'per month', r'/mo', r'monthly', r'every month'],
        "yearly": [r'per year', r'/yr', r'yearly', r'annually', r'annual', r'every year', r'next year']
    }

    CATEGORY_KEYWORDS = {
        "Entertainment": ["netflix", "spotify", "hulu", "disney", "youtube", "prime video", "hbo", "cinema", "music", "game", "steam", "playstation", "xbox", "nintendo"],
        "Software": ["github", "adobe", "jetbrains", "slack", "zoom", "google workspace", "microsoft 365", "dropbox", "atlassian", "linear", "vercel", "aws", "cloud", "hosting", "domain", "vpn"],
        "Utilities": ["electric", "water", "gas", "internet", "broadband", "mobile", "phone", "att", "verizon", "t-mobile", "vodafone", "comcast", "xfinity"],
        "Shopping": ["amazon", "ebay", "walmart", "target", "shopify", "order"],
        "News": ["nytimes", "wsj", "washington post", "guardian", "substack", "medium", "bloomberg"],
        "Health": ["gym", "fitness", "yoga", "meditation", "health", "insurance", "medical"],
        "Food": ["uber eats", "doordash", "grubhub", "hellofresh", "blue apron", "instacart"]
    }

    def parse_email(self, subject: str, body: str, sender: str) -> Optional[Dict[str, Any]]:
        """
        Main entry point. Returns a dict of subscription details or None if not a subscription.
        """
        # 1. First check: Is this even a subscription email?
        confidence = self._calculate_confidence(subject, body, sender)
        if confidence < 0.4:  # Threshold
            return None

        # 2. Extract details
        service_name = self._extract_service_name(sender, subject)
        cost, currency = self._extract_cost(body) or (None, "USD")
        cycle = self._extract_cycle(body, subject)
        category = self._extract_category(service_name, subject, body)

        return {
            "service_name": service_name,
            "cost": cost,
            "currency": currency,
            "billing_cycle": cycle,
            "category": category,
            "confidence_score": confidence,
            "status": "active" # Default assumption for found receipts
        }

    def _calculate_confidence(self, subject: str, body: str, sender: str) -> float:
        """
        Returns a score 0.0 - 1.0 indicating likelihood this is a subscription receipt/notice.
        """
        text = (subject + " " + body).lower()
        score = 0.0

        # Keywords
        strong_keywords = ["subscription", "recurring", "membership", "auto-renew"]
        weak_keywords = ["receipt", "invoice", "payment", "billing", "confirmed", "total"]

        if any(k in text for k in strong_keywords):
            score += 0.6  # Bumped to 0.6 to pass >0.5 check reliably
        if any(k in text for k in weak_keywords):
            score += 0.3

        # Sender keywords (noreply, billing, etc usually indicate automated transactional mail)
        sender_lower = sender.lower()
        if "billing" in sender_lower or "noreply" in sender_lower or "no-reply" in sender_lower:
            score += 0.1

        return min(score, 1.0)

    def _extract_service_name(self, sender: str, subject: str) -> str:
        """
        Extracts 'Netflix' from 'Netflix <info@netflix.com>' or 'Your Netflix Subscription'.
        """
        # Try to parse "Name <email>" format
        match = re.match(r'"?([^"<]+)"?\s*<.+>', sender)
        if match:
            name = match.group(1).strip()
            # Filter out generic names
            if name.lower() not in ["billing", "support", "no-reply", "noreply", "receipts"]:
                return name.title()

        # Fallback: Extract domain from email
        email_match = re.search(r'<([^>]+)>', sender)
        if not email_match:
             # Maybe sender is just 'info@netflix.com'
             email_match = re.search(r'[\w\.-]+@([\w\.-]+)', sender)

        if email_match:
            email = email_match.group(1) # e.g. "netflix.com" or "billing.netflix.com"
            # Get the main domain part
            parts = email.split('.')
            if len(parts) >= 2:
                # heuristic: take the second to last part (netflix.com -> netflix)
                # unless it's co.uk, then take third to last? simplistic for now.
                domain = parts[-2]
                if domain in ["mail", "email", "support", "billing", "notifications"]:
                    if len(parts) > 2:
                        domain = parts[-3]
                return domain.title()

        return "Unknown Service"

    def _extract_cost(self, body: str) -> Optional[tuple[float, str]]:
        """
        Returns (amount, currency_code).
        """
        # Normalize body slightly
        text = body.replace("\n", " ").strip()

        for pattern in self.COST_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the last match? Or the first?
                # Receipts often have subtotal, tax, TOTAL. Total is usually last or largest.
                # Let's try to find the one explicitly labeled "Total" first.

                # If the regex specifically matched "Total", it's good.
                # My regexes above include the keyword.

                # matches is a list of tuples (symbol, amount)
                symbol, amount_str = matches[0]
                try:
                    amount = float(amount_str)
                    currency = self.CURRENCY_SYMBOLS.get(symbol, "USD")
                    return amount, currency
                except ValueError:
                    continue

        return None

    def _extract_cycle(self, body: str, subject: str) -> Optional[str]:
        text = (subject + " " + body).lower()

        for cycle_name, patterns in self.CYCLE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return cycle_name

        return "monthly" # Default fallback? Or None?

    def _extract_category(self, service_name: str, subject: str, body: str) -> str:
        # Check service name first (higher priority)
        service_lower = service_name.lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(k in service_lower for k in keywords):
                return category

        # Then check subject/body (we can reuse the fact that text usually contains service name,
        # or just concatenate only subject+body if we wanted strictly those.
        # But for simplicity and to match previous logic's intent efficiently:)
        text = (subject + " " + body).lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(k in text for k in keywords):
                return category

        return "Other"
