
#  Airport API Service

It's system for tracking flights from airports across the whole globe writing on DRF.


## Installing using GitHub
Install PostgresSQL and create db

Clone the project

```bash
  git clone https://github.com/vkleshko/Airport-API-Service.git
```

Go to the project directory

```bash
  cd airport-api-service
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Set up environment variables:

```
  set DB_HOST=<your db hostname>
  set DB_NAME=<your db name>
  set DB_USER=<your db username>
  set DB_PASSWORD=<your db user password>
  set SECRET_KEY=<your secret key>
  set API_KEY=<get it at 'https://app.mailjet.com/account/apikeys'>
  set API_SECRET=<get it at 'https://app.mailjet.com/account/apikeys'>
```

Migrate Database

```bash
  python manage.py migrate
```

Runserver

```bash
  python manage.py runserver
```

## Run with Docker
Docker should be installed

```bash
  docker-compose build
  docker-compose up
```

## Getting access

- create user via /api/user/register/
- get access token via /api/user/token/
- verify your email via /api/user/verify-email/


## Features

- JWT authenticated
- Email verification
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/ or /api/doc/redoc/ 
- Aircraft information management
- Creation and planning of flights
- Order processing
- Issuance of tickets
- Filtering crews, airports, routs, airplanes, airplane types and flights


## Running Tests

To run tests, run the following command

```bash
  python manage.py test
```
