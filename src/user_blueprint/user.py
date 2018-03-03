"""
Form implementations for the user blueprint.
"""

# Imports
# ----------------------------------------

from flask_login import UserMixin

from flask_wtf import FlaskForm

from wtforms import BooleanField,\
                    PasswordField,\
                    StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


# Typing imports
# ----------------------------------------


from typing import Callable, Dict, Mapping, Optional, NamedTuple


# Metadata
# ------------------------------------------------------------


__author__ = "Peter Volf"


# Classes
# ------------------------------------------------------------

class UserHandler(object):
    """
    Class whose instances provide the user blueprint access to the user database.

    `UserHandler` instances must be configured by using the following decorators
    on the application methods that implement the corresponding functionality:
        - `identifier_getter()`:
        - `password_getter()`:
        - `password_reset_email_sender()`:
        - `password_updater()`:
        - `user_getter()`:
        - `user_inserter()`:

    You can further configure the user handler by using the following decorators
    on the application methods that implement the corresponding functionality:
        - `reset_token_validator()`:
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self) -> None:
        self._identifier_getter: Callable[[UserMixin], str] = None
        """
        """

        self._password_getter: Callable[[UserMixin], str] = None
        """
        """

        self._password_reset_email_sender: Callable[[UserMixin, str], bool] = None
        """
        """

        self._password_updater: Callable[[UserMixin, str], bool] = None
        """
        """

        self._reset_token_validator: Callable[[Mapping], bool] = self._accept_reset_token
        """
        """

        self._user_getter: Callable[[str], Optional[UserMixin]] = None
        """
        """

        self._user_inserter: Callable[["RegistrationData"], bool] = None
        """
        """

    # Decorator Methods
    # ------------------------------------------------------------

    def identifier_getter(self, callback: Callable[[UserMixin], str]) -> Callable[[UserMixin], str]:
        """
        """
        self._identifier_getter = callback
        return callback

    def password_getter(self, callback: Callable[[UserMixin], str]) -> Callable[[UserMixin], str]:
        """
        """
        self._password_getter = callback
        return callback

    def password_reset_email_sender(self, callback: Callable[[UserMixin, str], bool]) -> Callable[[UserMixin, str], bool]:
        """
        """
        self._password_reset_email_sender = callback
        return callback

    def password_updater(self, callback: Callable[[UserMixin, str], bool]) -> Callable[[UserMixin, str], bool]:
        """
        """
        self._password_updater = callback
        return callback

    def reset_token_validator(self, callback: Callable[[Mapping], bool]) -> Callable[[Mapping], bool]:
        """
        """
        self._reset_token_validator = callback
        return callback

    def user_getter(self, callback: Callable[[str], UserMixin]) -> Callable[[str], Optional[UserMixin]]:
        """
        """
        self._user_getter = callback
        return callback

    def user_inserter(self, callback: Callable[["RegistrationData"], bool]) -> Callable[["RegistrationData"], bool]:
        """
        """
        self._user_inserter = callback
        return callback

    # Methods
    # ------------------------------------------------------------

    def get_identifier(self, user: UserMixin) -> str:
        """
        """
        return self._identifier_getter(user)

    def get_password_hash(self, user: UserMixin) -> str:
        """
        """
        return self._password_getter(user)

    def get_user(self, identifier: str) -> Optional[UserMixin]:
        """
        """
        return self._user_getter(identifier)

    def insert_user(self, data: "RegistrationData") -> bool:
        """
        """
        return self._user_inserter(data)

    def send_password_reset_email(self, user: UserMixin, reset_link: str) -> bool:
        """
        """
        return self._password_reset_email_sender(user, reset_link)

    def update_password(self, user: UserMixin, password_hash: str) -> bool:
        """
        """
        return self._password_updater(user, password_hash)

    def validate_reset_token(self, token: Mapping) -> bool:
        """
        """
        return self._reset_token_validator(token)

    # Protected methods
    # ------------------------------------------------------------

    def _accept_reset_token(self, token: Mapping) -> bool:
        """
        """
        return token is not None


class LoginForm(FlaskForm):
    """
    Login form.
    """

    # Form field definitions
    # ------------------------------------------------------------

    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=5, max=40)])
    password = PasswordField(
        "Password",
         validators=[DataRequired(), Length(min=8, max=40)])
    remember = BooleanField("Remember me")


class LoginData(NamedTuple):
    """
    The data of a login form.
    """

    # Properties
    # ------------------------------------------------------------

    username: str
    """
    The entered username.
    """

    password: str
    """
    The entered password (not hashed, so it can be verified).
    """

    remember: str
    """
    Whether the user checked the remember field.
    """

    # Static methods
    # ------------------------------------------------------------

    @staticmethod
    def from_form(form: LoginForm) -> "LoginData":
        """
        Returns the login data for the given login form.
        """
        return LoginData(
            username=form.username.data,
            password=form.password.data,
            remember=form.remember.data
        )


class PasswordResetForm(FlaskForm):
    """
    Form where the user can reset her or his password.
    """

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=40)])
    password2 = PasswordField(
        "Repeat Password",
        validators=[EqualTo("password", "Field must be equal to Password.")])


class RegistrationForm(FlaskForm):
    """
    Registration form.
    """

    # Form field definitions
    # ------------------------------------------------------------

    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=5, max=40)])
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()])
    first_name = StringField(
        "First name",
        validators=[DataRequired(), Length(min=3, max=40)])
    last_name = StringField(
        "Last name",
        validators=[DataRequired(), Length(min=3, max=40)])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=40)])
    password2 = PasswordField(
        "Repeat Password",
        validators=[EqualTo("password", "Field must be equal to Password.")])

    # Initialization
    # ------------------------------------------------------------

    def __init__(self, user_handler: UserHandler) -> None:
        """
        """
        super(RegistrationForm, self).__init__()

        self._user_handler: UserHandler = user_handler
        """
        """

    # Additional validator methods
    # ------------------------------------------------------------

    def validate_username(self, username: StringField) -> None:
        """
        """
        if self._user_handler.get_user(username.data) is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email:StringField) -> None:
        """
        """
        if self._user_handler.get_user(email.data) is not None:
            raise ValidationError("Please use a different email address.")


class RegistrationData(NamedTuple):
    """
    The data of a registration form.
    """

    # Properties
    # ------------------------------------------------------------

    username: str
    """
    The entered username.
    """

    email: str
    """
    The entered email.
    """

    first_name: str
    """
    The entered first name.
    """

    last_name: str
    """
    The entered last name.
    """

    password: str
    """
    The Argon2 hash of the entered password.
    """

    # Static methods
    # ------------------------------------------------------------

    @staticmethod
    def from_form(form: RegistrationForm) -> "RegistrationData":
        """
        Returns the registration data for the given registration form.
        """
        from passlib.hash import argon2

        return RegistrationData(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=argon2.hash(form.password.data)
        )


class RequestPasswordResetForm(FlaskForm):
    """
    Password reset request form.
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
