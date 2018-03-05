# Flask user handler blueprint

Flask blueprint that provides all the user handling features that are required by a web page:

- User registration.
- Automatic, safe password handling.
- Full user session management.
- Password reset functionality with JWTs.

## How to use

The blueprint requires the following components to be configured:

- `blueprint.user_handler`: See the documentation of the `UserHandler` class for the details.
- `LoginManager`: This `Flask-Login` component handles the session management of the Flask application. You need to create an instance of this class and configure it according to the documentation of `Flask-Login`.

A working demo Flask application showing all the described configuration is included in the library, see `demo.py`.

## Dependencies

The library requires the following dependencies to be installed.

- `Flask-Login`: User session management.
- `Passlib`: Password hashing and verification.
- `Argon2_cffi`: The preferred Argon2 backend for `Passlib`. See `Passlib`'s documentation for more options.

## License - MIT

The library is open-sourced under the conditions of the MIT [license](https://choosealicense.com/licenses/mit/).

## Credit

Miguel Grinberg's [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
