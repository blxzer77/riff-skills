class SignupError(Exception):
    pass


def signup(db, mailer, email: str, name: str) -> int:
    """Create the user and send the welcome email. Returns the new user id."""
    if "@" not in email:
        raise SignupError("invalid email")
    user_id = db.insert_user(email, name)
    mailer.send(
        to=email,
        subject="Welcome to Tidepool",
        body=f"Hi {name}, your account is ready.",
    )
    return user_id
