from codecs import open
from os import path
from setuptools import setup, find_packages

# Get the long description from the README file
with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="user-blueprint",
    version="0.3.0",
    description="Flask blueprint that provides all the user handling features that are required "
                "by a web application in a database-independent way, including user registration, "
                "login, session management, password reset functionality with JWTs, automatic "
                "password hashing with Argon2 and of course the all the required route "
                "implementations with the corresponding HTML templates (styled using BlueprintJS).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/volfpeter/user-blueprint",
    author="Peter Volf",
    author_email="do.volfp@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords="flask blueprint user authentication login registration session templates argon2",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.5",
    install_requires=[
        "flask>=0.12",
        "flask-login>=0.4",
        "flask-wtf>=0.14",
        "passlib>=1.7",
        "pyjwt>=1.5"
    ]
)
