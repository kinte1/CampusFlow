def validate_title(title):
    """Validate a support ticket title."""
    if not isinstance(title, str):
        raise ValueError("Ticket title must be text.")

    title = title.strip()

    if not title:
        raise ValueError("Ticket title cannot be empty.")

    return title

def validate_category(category):
    """Validate a support ticket category."""
    allowed_categories = {"Network", "Hardware", "Software", "Other"}

    if not isinstance(category, str):
        raise ValueError("Category must be text.")

    category = category.strip().title()

    if category not in allowed_categories:
        raise ValueError(
            f"Invalid category. Choose one of: {', '.join(sorted(allowed_categories))}."
        )

    return category
