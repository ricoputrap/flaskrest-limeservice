
# Limeservice

Lorem ipsum dolor sit amet blablabla.


## Tech Stack

**Server:** Python, Flask, Flask-RESTful, Flask-SQLAlchemy, flask-marshmallow, Flask-Migrate

**Database:** PostgreSQL (`psycopg2-binary`)

  
## Run Locally

Clone the project

```bash
  git clone https://github.com/ricoputrap/flaskrest-limeservice
```

Go to the project directory
```bash
  cd flaskrest-limeservice
```

Prepare & activate virtual environment
```bash
  python -m venv env
  source env/bin/activate
```

Install dependencies
```bash
  pip install -r requirements.txt
```

Copy and adjust `.env.example` to `.env`.

Run the docker container
```bash
  docker-compose up -d
```

Start the server
```bash
  python3 wsgi.py
```

Run the latest version of db migration file
```bash
  flask db upgrade
```