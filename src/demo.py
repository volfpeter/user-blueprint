"""
Demo Flask application showing how to use the user blueprint.
"""


# Imports
# ----------------------------------------


from flask import Flask, url_for

from flask_login import LoginManager,\
                        UserMixin,\
                        current_user,\
                        login_required

from user_blueprint.blueprint import user_blueprint,\
                                     user_handler
from user_blueprint.user import RegistrationData,\
                                console_password_reset_email_sender,\
                                console_verification_email_sender


# Typing imports
# ----------------------------------------


from typing import Dict, Optional, Set, Union


# Metadata
# ------------------------------------------------------------


__author__ = "Peter Volf"


# Database
# ------------------------------------------------------------


class User(UserMixin):
    """
    User database model.
    """

    # Static variables
    # ------------------------------------------------------------

    _id_counter: int = 0

    # Initialization
    # ------------------------------------------------------------

    def __init__(self):
        """
        Initialization.
        """
        super(User, self).__init__()

        self.id: str = User.get_next_id()
        self.username: str = None
        self.email: str = None
        self.first_name: str = None
        self.last_name: str = None
        self.password: str = None
        self.verified: bool = False

    # Special methods
    # ------------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} <{self.username} {self.email}, {self.password}, {self.id}, {self.verified}>"

    # Class methods
    # ------------------------------------------------------------

    @classmethod
    def get_next_id(cls) -> str:
        """
        Increments the ID counter and returns its new value as a string.
        """
        cls._id_counter += 1
        return str(cls._id_counter)

    # Methods
    # ------------------------------------------------------------

    def get_id(self) -> str:
        """
        Returns the ID of the user.

        Flask-Login uses this method to get the user for a session ID.
        """
        return self.id


users: Dict[str, User] = {}
"""The user database."""


# Application configuration
# ------------------------------------------------------------


app = Flask(__name__)
app.secret_key = "some secret key, should be configured correctly from a config object"
app.register_blueprint(user_blueprint, url_prefix="/auth")

login_manager: LoginManager = LoginManager(app)
"""
The login manager to use in the application.
"""

login_manager.login_view = "auth.login"


# Login manager configuration
# ------------------------------------------------------------


@login_manager.user_loader
def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Returns the user that has the given ID in the database.

    Arguments:
        user_id (str): The ID of the user to fetch from the database.

    Returns:
        The user that has the given ID or `None` if no such user exists.
    """
    return users.get(user_id)


# User handler configuration
# ------------------------------------------------------------


user_handler.token_signing_key = "DemoResetTokenSecret"
user_handler.password_reset_email_sender(console_password_reset_email_sender)
user_handler.verification_email_sender(console_verification_email_sender)


@user_handler.user_by_reset_key_getter
@user_handler.user_getter
def get_user_by_identifier(identifier: str) -> Optional[User]:
    """
    Returns the user corresponding to the given identifier.

    Arguments:
        identifier (str): The identifier of the user to fetch.

    Returns:
        The user corresponding to the given identifier if such a user exists.
    """
    for user in users.values():
        # Allow login both with username and email address.
        if user.username == identifier:
            return user
        if user.email == identifier:
            return user
    return None


@user_handler.reset_key_getter
def get_user_identifier(user: User) -> str:
    """
    Returns the identifier of the given user.

    Arguments:
        user (User): The user whose identifier is required.

    Returns:
        The identifier of the given user.
    """
    return user.email


@user_handler.password_getter
def get_user_password(user: User) -> str:
    """
    Returns the password of the given user.

    Arguments:
        user (User): The user whose password is required.

    Returns:
        The password of the given user.
    """
    return user.password


@user_handler.user_inserter
def insert_user(data: RegistrationData) -> bool:
    """
    Inserts the user specified by the given registration form data to the database.

    Arguments:
        data (RegistrationData): The registration form data of the user to create.

    Returns:
        Whether the user has been created successfully.
    """
    if get_user_by_identifier(data.username) is not None:
        return False

    if get_user_by_identifier(data.email) is not None:
        return False

    user = User()
    user.username = data.username
    user.email = data.email
    user.first_name = data.first_name
    user.last_name = data.last_name
    user.password = data.password

    users[user.id] = user

    return True


@user_handler.verification_checker
def is_user_verified(user: User) -> bool:
    """
    Returns whether the given user's registration is verified.

    Arguments:
        user (User): The user to check.

    Returns:
        Whether the given user's registration is verified.
    """
    return user.verified


@user_handler.password_updater
def update_user_password(user: User, password_hash: str) -> bool:
    """
    Updates the password of the given user to the specified value.

    Arguments:
        user (User): The user whose password is to be updated.
        password_hash (str): The new password hash of the user.

    Returns:
        Whether the user's password has been updated successfully.
    """
    user.password = password_hash
    return True


@user_handler.registration_verifier
def verify_registration(user: User) -> None:
    """
    Verifies the given user's registration.

    Arguments:
        user (User): The user whose registration is to be verified.
    """
    user.verified = True


# View definitions
# ------------------------------------------------------------


@app.route("/")
@app.route("/index")
@login_required
def index():
    """
    View function for the index page.
    """
    user: User = current_user
    return \
        "<div>" +\
        f"<a href=\"{url_for('auth.logout')}\">Log out</a>" +\
        f"<h1>Welcome {str(user)}</h1>" +\
        "</div>"


# Entry
# ------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)
