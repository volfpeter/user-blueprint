# Flask user handler blueprint

Flask blueprint that provides all the user handling features that are required by a web page:

- User registration.
- Automatic, safe password handling.
- Full user session management.
- Password reset functionality with JWTs.

## How to use

See the included demo Flask application (`demo.py`).

## Dependencies

The library requires the following dependencies to be installed.

- `Flask-Login`: User session management.
- `Passlib`: Password hashing and verification.
- `Argon2_cffi`: Argon2 backend for `Passlib`.

## License - MIT

The library is open-sourced under the conditions of the MIT [license](https://choosealicense.com/licenses/mit/).

## Credit

Miguel Grinberg's [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
