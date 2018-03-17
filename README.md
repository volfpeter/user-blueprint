# Flask user handler blueprint

Lightweight Flask blueprint that provides all the user handling features that are required by a web application in a database-independent way, including:

- User registration, login and session management.
- Password reset functionality with JWTs.
- Automatic, safe password handling using [Argon2](https://en.wikipedia.org/wiki/Argon2).

The blueprint provides the following routes for a web application: `/login`, `/logout`, `/register`, `/request_password_reset`, `/reset/<token>` and `/verify/<token>`. All these routes interact with the user database through an instance of the `UserHandler` class that is a decorator-based database interface, similar in style to `Flask-Login`'s `LoginManager`. All the blueprint routes are backed by ready-to-use HTML templates that are formatted using [BlueprintJS](http://blueprintjs.com/docs/v2/).

## Installation

The project is available on PyPI as [`user-blueprint`](https://pypi.org/project/user-blueprint/), you can install it with `pip install user-blueprint`.

## How to use

The blueprint requires the following components to be configured:

- `blueprint.user_handler`: See the documentation of the `UserHandler` class for the details.
- `LoginManager`: This `Flask-Login` component handles the session management of the Flask application. You need to create an instance of this class and configure it according to the documentation of `Flask-Login`.

A working demo Flask application showing all the required configuration is included in the library, see `demo.py`.

## Dependencies

The library requires the following dependencies to be installed besides `Flask` itself.

- `Flask-Login`: User session management.
- `Flask-WTF`: `WTForms` integration for `Flask`.
- `Passlib`: Password hashing and verification.
- `PyJWT`: JSON Web Token implementation in Python.
- `Argon2_cffi`: The preferred Argon2 backend for `Passlib`. See `Passlib`'s documentation for more options.

## License - MIT

The library is open-sourced under the conditions of the MIT [license](https://choosealicense.com/licenses/mit/).

## Credit

Miguel Grinberg's [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
