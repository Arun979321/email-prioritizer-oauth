from datetime import datetime, timedelta
import random

def analyze_emails(emails, hours=24, top_n_summaries=3):
    """
    Mock email analysis function with risk and type classification.
    """
    now = datetime.utcnow()
    analyzed = []

    for email in emails:
        date_str = email.get("date", "")
        try:
            # Support multiple date formats
            email_date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").astimezone().replace(tzinfo=None)
        except Exception:
            try:
                email_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except Exception:
                email_date = now

        if now - email_date > timedelta(hours=hours):
            continue

        subject = email.get("subject", "")
        body = email.get("body", "")

        # Dummy scoring
        priority_score = min(len(subject + body) % 100 + 10, 100)
        sender = email.get("from", "").lower()
        subject = email.get("subject", "")
        body = email.get("body", "")

        if any(word in sender.lower() for word in ["hr@", "recruit", "hiring", "careers"]):
          category = "Work"
          category_confidence = 0.92
        elif any(word in subject.lower() for word in ["offer", "deal", "discount", "sale"]):
          category = "Promotions"
          category_confidence = 0.88
        elif any(word in subject.lower() for word in ["alert", "invoice", "payment", "transaction"]):
          category = "Finance"
          category_confidence = 0.9
        else:
          category = "Personal"
          category_confidence = 0.75
    
        summary = (body[:150] + "...") if len(body) > 150 else body

        # NEW — Risk and Type logic
        type_ = "Notification" if "alert" in subject.lower() else "General"
        risk_score = random.randint(0, 100)
        if risk_score > 70:
            risk_level = "High"
        elif risk_score > 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        urgent = priority_score > 75 or "urgent" in body.lower()

        analyzed.append({
            "id": email.get("id", ""),
            "from": email.get("from_", email.get("from", "unknown")),
            "to": email.get("to", ""),
            "subject": subject,
            "body": body,
            "date": email.get("date"),
            "priority_score": priority_score,
            "category": category,
            "category_confidence": category_confidence,
            "summary": summary,
            "urgent": urgent,
            "type": type_,
            "risk_score": risk_score,
            "risk_level": risk_level
        })

    return analyzed
