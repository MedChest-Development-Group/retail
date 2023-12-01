# Retail Strategies Portal

The Retail Strategies Portal is a portal dashboard made by Dylan Calvin, Betty Chen, Michael Gathara, Joe Chang, and Vira Shankar; as their capstone project. The current project tends to be more of a prototype of which one can build upon. 

## Getting Started

These instructions will get your copy of the project up and running on your machine for development, semi-production and testing purposes.

### Project Structure
app/
├── __pycache__
├── blueprints/
│   ├── admin/
│   ├── city/
│   └── __init__.py
├── models/
│   ├── __pycache__
│   ├── __init__.py
│   ├── client_selector.py
│   ├── city_user.py
│   └── company_user.py
│   └── uploads.py
├── static/
│   ├── css/
│   ├── favicon_io/
│   ├── imgs/
│   ├── js/
│   └── favicon.png
│   └── old_favicon.ico
├── templates/
│   ├── admin/
│   ├── city/
│   ├── company/
│   ├── error/
│   └── _formhelpers.html
│   └── base.html
│   └── login.html
│   └── upload.html
├── __init__.py
├── config.py
└── env/
└── .gitignore
└── cards.db
└── cities.db
└── files.db
└── messages.db
└── README.md
└── requirements.pdf
└── requirements.txt
└── server.py
└── TODO.md
└── tokens.db
└── users.db

* The `blueprints` folder was meant to hold the routes, this is useful for changing the program to be more modular in the future
* The `models` folder holds the code for specific types of users. This folder is mostly unused for now, but can be expanded on in the future if you need a specific type of user to hold specific structures.
* The `static` folder holds css, js, and icons.
* The `templates` folder holds the html files for rendering templates 

### Prerequisites

- Python 3.9+ and Pip

We suggest creating a python environment to keep the libraries isolated. Thus the first step to setup would be:

* Linux and MacOS
```bash
python3 -m venv env/
source env/bin/activate
pip install -r requirements.txt
```

* Windows
```bash
py -m venv env/
cd env/Scripts
activate.bat
pip install -r requirements.txt
```

### Starting point
The starting point of the program is the `server.py` file. This file holds all the routes, creates the database functions for the different databases. 

The server file is well documentated where each function has it's own documentation that is in-line. 

To run the server:

```bash
python3 server.py
```

The admin page will be opened on the `port: 8123` and the regular users page will be opened on `port: 5000`