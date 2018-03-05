"""
Form implementations for the user blueprint.
"""

# Imports
# ----------------------------------------

from flask import url_for

from flask_login import UserMixin

from flask_wtf import FlaskForm

from wtforms import BooleanField,\
                    PasswordField,\
                    StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


# Typing imports
# ----------------------------------------


from typing import Callable, Mapping, Optional, NamedTuple


# Metadata
# ------------------------------------------------------------


__author__ = "Peter Volf"


# Classes
# ------------------------------------------------------------

class UserHandler(object):
    """
    Class whose instances provide the user blueprint access to the user database.

    `UserHandler` instances must be configured by using the following decorators
    on the application or database methods that implement the corresponding functionality:
    `password_getter`, `password_reset_email_sender`, `password_updater`, `reset_key_getter`,
    `user_getter`, `user_by_reset_key_getter`, `user_inserter`.

    Besides the aforementioned decorators, you must set the `reset_token_secret`
    property to the secret key you would like to sign reset tokens with.

    You can further configure the user handler by using the following decorators
    on the application methods that implement the corresponding functionality:
    `reset_token_validator`.
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialization.
        """

        self.reset_token_secret: str = None
        """
        The secret key to use to sign password reset tokens.
        """

        self._password_getter: Callable[[UserMixin], str] = None
        """
        Function that returns the given user's password (hash) from the database.
        """

        self._password_reset_email_sender: Callable[[UserMixin, str], bool] = None
        """
        Function that sends the given password reset link to the given user.
        """

        self._password_updater: Callable[[UserMixin, str], bool] = None
        """
        Function that updates the given user's password (hash) to the given new value.
        """

        self._reset_key_getter: Callable[[UserMixin], str] = None
        """
        Function that returns a password reset key that uniquely identifies the given user.
        """

        self._reset_token_validator: Callable[[Mapping], bool] = self._accept_reset_token
        """
        Function that executes extra validation on a valid JWT reset token.
        """

        self._user_by_reset_key_getter: Callable[[str], Optional[UserMixin]] = None
        """
        Function that returns the user corresponding to the given password reset key.
        """

        self._user_getter: Callable[[str], Optional[UserMixin]] = None
        """
        Function that takes a user identifier (username or email address) and return
        the corresponding user.
        """

        self._user_inserter: Callable[["RegistrationData"], bool] = None
        """
        Function that inserts the user - defined by the given registration data - to
        the database.
        """

    # Decorator Methods
    # ------------------------------------------------------------

    def password_getter(self, callback: Callable[[UserMixin], str]) -> Callable[[UserMixin], str]:
        """
        Decorator to use on the application or database method that returns a given
        user's password (or password hash to be more precise).
        """
        self._password_getter = callback
        return callback

    def password_reset_email_sender(self, callback: Callable[[UserMixin, str], bool]) -> Callable[[UserMixin, str], bool]:
        """
        Decorator to use on the application method that sends the given user the
        given password reset link.
        """
        self._password_reset_email_sender = callback
        return callback

    def password_updater(self, callback: Callable[[UserMixin, str], bool]) -> Callable[[UserMixin, str], bool]:
        """
        Decorator to use on the application or database method that updates the
        given user's password (hash) to the given new value.
        """
        self._password_updater = callback
        return callback

    def reset_key_getter(self, callback: Callable[[UserMixin], str]) -> Callable[[UserMixin], str]:
        """
        Decorator to user on the application or database method that returns the
        password reset key that uniquely identifies the given user.

        The method decorated with `user_by_reset_key_getter` must be able to identify
        the users corresponding to the reset keys `callback` returns.
        """
        self._reset_key_getter = callback
        return callback

    def reset_token_validator(self, callback: Callable[[Mapping], bool]) -> Callable[[Mapping], bool]:
        """
        Decorator to use on the application or database method that validates reset
        tokens. The decorated method receives the JWT token as a mapping.
        """
        self._reset_token_validator = callback
        return callback

    def user_getter(self, callback: Callable[[str], Optional[UserMixin]]) -> Callable[[str], Optional[UserMixin]]:
        """
        Decorator to use on the application or database method thar returns the user corresponding
        the given identifier (username or email address) if such a user exists.
        """
        self._user_getter = callback
        return callback

    def user_by_reset_key_getter(self, callback: Callable[[str], Optional[UserMixin]]) -> Callable[[str], Optional[UserMixin]]:
        """
        Decorator to use on the application or database method that can return the
        corresponding user for a reset key (generated by the method that is decorated
        with `reset_key_getter`).
        """
        self._user_by_reset_key_getter = callback
        return callback

    def user_inserter(self, callback: Callable[["RegistrationData"], bool]) -> Callable[["RegistrationData"], bool]:
        """
        Decorator to use on the method that iinserts the user - defined by the
        given registration data - to the database.
        """
        self._user_inserter = callback
        return callback

    # Methods
    # ------------------------------------------------------------

    def get_user(self, identifier: str) -> Optional[UserMixin]:
        """
        Returns the user corresponding to the given identifier that could be either
        a username or an email address.

        Arguments:
            identifier (str): The identifier of the queried user. It should be either
                              the username or the email address of the user.

        Returns:
            The user that has the given identifier or `None` if there is no such user.
        """
        return self._user_getter(identifier)

    def get_user_for_reset_token(self, token: str) -> Optional[UserMixin]:
        """
        Returns the user the given reset token belongs to.

        Arguments:
            token (str): The encoded reset token to get the corresponding user for.

        Returns:
            The user the reset token belongs to if the token is valid and
            such a user exists.
        """
        import jwt

        try:
            data: Mapping = jwt.decode(token, self.reset_token_secret)
            if not self._reset_token_validator(data):
                return None
        except:
            return None

        return self._user_by_reset_key_getter(data["reset_key"])

    def insert_user(self, data: "RegistrationData") -> bool:
        """
        Inserts a user to the database with the given registration data.

        Arguments:
            data (RegistrationData):  The data the user tries to register with.

        Returns:
            Whether the user has been successfully inserted to the database.
        """
        return self._user_inserter(data)

    def login_user(self, data: "LoginData") -> bool:
        """
        Logs in the user (through the application's login manager) described by
        the given login data if the user exists.

        Arguments:
            data (LoginData): The login data of the user to log in.

        Returns:
            `True` if the login data corresponds to an existing user and the
            entered password is correct, `False` otherwise.
        """
        user = self.get_user(data.username)
        if user is None:
            return False

        from passlib.hash import argon2

        try:
            if argon2.verify(data.password, self._password_getter(user)):
                from flask_login import login_user
                login_user(user, remember=data.remember)
                return True
        except Exception:
            # Catch everything the verify method can raise.
            pass

        return False

    def send_password_reset_email(self, email: str) -> bool:
        """
        Send a password reset email to the given user.

        Arguments:
            email (str): The email address of the user to send the password reset to.

        Returns:
            `True` if the reset email has been sent successfully, `False` otherwise.
        """
        from time import time
        import jwt

        user: UserMixin = self.get_user(email)
        if user is None:
            return False

        token: bytes = jwt.encode(
            {"reset_key": self._reset_key_getter(user), "exp": time() + 600},
            self.reset_token_secret
        )

        return self._password_reset_email_sender(user, url_for(".reset", token=token, _external=True))

    def update_password(self, user: UserMixin, password_hash: str) -> bool:
        """
        Updates the password of the given user.

        Arguments:
            user (UserMixin): The user whose password is to be updated.
            password_hash (str): The new password hash of the user.

        Returns:
            `True` if the password has been updated successfully, `False` otherwise.
        """
        return self._password_updater(user, password_hash)

    # Protected methods
    # ------------------------------------------------------------

    def _accept_reset_token(self, token: Mapping) -> bool:
        """
        The default token validator that accepts every token that is not `None`.

        Arguments:
            token (Mapping): The token to validate.

        Returns:
            `True` if `token` is not `None`, `False` otherwise.
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
            username=form.username.data.lower(),
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
        Initialization.

        Arguments:
            user_handler (UserHandler): The user handler to use to check the availability
                                        of the chosen username and email address.
        """
        super(RegistrationForm, self).__init__()

        self._user_handler: UserHandler = user_handler
        """
        The user handler to use to check the availability of the chosen username and email address.
        """

    # Additional validator methods
    # ------------------------------------------------------------

    def validate_username(self, username: StringField) -> None:
        """
        Validates the given `username`.

        The method is automatically called by the form's `validate_on_submit()` method.
        """
        if self._user_handler.get_user(username.data.lower()) is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email: StringField) -> None:
        """
        Validates the given `email`.

        The method is automatically called by the form's `validate_on_submit()` method.
        """
        if self._user_handler.get_user(email.data.lower()) is not None:
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
            username=form.username.data.lower(),
            email=form.email.data.lower(),
            first_name=form.first_name.data.title(),
            last_name=form.last_name.data.title(),
            password=argon2.hash(form.password.data)
        )


class RequestPasswordResetForm(FlaskForm):
    """
    Password reset request form.
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
