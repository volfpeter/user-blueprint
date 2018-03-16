"""
Flask user handler blueprint.
"""

# Imports
# ----------------------------------------


from flask import Blueprint,\
                  redirect,\
                  render_template,\
                  request,\
                  url_for

from flask_login import current_user,\
                        login_required,\
                        logout_user

from werkzeug.urls import url_parse

from user_blueprint.user import UserHandler,\
                                LoginForm, LoginData,\
                                PasswordResetForm,\
                                RegistrationForm, RegistrationData,\
                                RequestPasswordResetForm


# Typing imports
# ----------------------------------------


# Metadata
# ------------------------------------------------------------


__author__ = "Peter Volf"


# Blueprint
# ----------------------------------------


user_blueprint: Blueprint = Blueprint("auth", __name__, template_folder="templates")
"""
The "user" blueprint.
"""


# Global properties.
# ----------------------------------------


user_handler: UserHandler = UserHandler()
"""
The user handler the blueprint is using to interact with the user database.
"""


# Blueprint routes
# ----------------------------------------


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """
    View function for the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    login_error = ""
    form = LoginForm()
    if form.validate_on_submit():
        if user_handler.login_user(LoginData.from_form(form)):
            next_page = request.args.get("next")
            if not is_internal_url(next_page):
                next_page = url_for("index")
            return redirect(next_page)
        else:
            login_error = "Invalid username or password."

    return render_template("login.html", form=form, title="Log In", login_error=login_error)


@user_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    View function for the logout page.
    """
    logout_user()
    return redirect(url_for(".login"))


@user_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """
    View function for the registration page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm(user_handler)
    if form.validate_on_submit():
        if user_handler.insert_user(RegistrationData.from_form(form)):
            return redirect(url_for(".login"))

    return render_template("register.html", form=form, title="Register")


@user_blueprint.route("/request_password_reset", methods=["GET", "POST"])
def request_password_reset():
    """
    View function for the page where the visitor can request a password reset for an email address.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user_handler.send_password_reset_email(form.email.data)
        return render_template(
            "request_password_reset.html",
            title="Reset Password",
            form=form,
            message="Password reset email sent."
        )

    return render_template(
        "request_password_reset.html",
        title="Reset Password",
        form=form,
        message=""
    )


@user_blueprint.route("/reset/<token>", methods=['GET', 'POST'])
def reset(token: str):
    """
    View function for the page where the user can reset her or his password.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    user = user_handler.get_user_for_reset_token(token)
    if user is None:
        return redirect(url_for(".login"))

    form = PasswordResetForm()
    if form.validate_on_submit():
        from passlib.hash import argon2
        user_handler.update_password(user, argon2.hash(form.password.data))
        return redirect(url_for(".login"))

    return render_template(
        "reset_password_with_token.html",
        title="Reset Password",
        token=token,
        form=form
    )


# Methods
# ----------------------------------------


def is_internal_url(url: str) -> bool:
    """
    Returns whether the given URL is internal to the application.

    Arguments:
        url (str): The URL to check.

    Returns:
        Whether the given URL is internal to the application.
    """
    return url is not None and url_parse(url).netloc == ""
