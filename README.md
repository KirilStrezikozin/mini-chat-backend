# mini-chat backend

This repository stores the source for mini-chat backend. Built with
[FastAPI](https://fastapi.tiangolo.com/).

## Development

### Without Docker

1. To run the backend locally, first install the dependencies using `poetry`:

```sh
poetry install
```

2. Create a `.env` file (have a look at `.env.sample` for the list of necessary
variables). Below is an example:

```sh
PROJECT_NAME=minichat

DATABASE__POSTGRES_SERVER=localhost
DATABASE__POSTGRES_PORT=5432
DATABASE__POSTGRES_USER=postgres
DATABASE__POSTGRES_PASSWORD=12345
DATABASE__POSTGRES_DB=minichat-db

SITE_URL=https://minichat.localhost
ALLOW_ORIGINS=["${SITE_URL}"]
USE_SECURE_COOKIES=True

BACKEND_PORT=8000
BACKEND_HOST=localhost
BACKEND_URL=http://${BACKEND_HOST}:${BACKEND_PORT}
FRONTEND_PORT=3000
FRONTEND_URL=http://localhost:3000

S3__ENDPOINT_URL=CHANGE_THIS
S3__ACCESS_KEY_ID=CHANGE_THIS
S3__SECRET_ACCESS_KEY=CHANGE_THIS
S3__BUCKET_NAME=CHANGE_THIS
```

You will need to set credentials for an S3-compatible bucket in order to
have the message attachments functionality working.

3. Run database migrations:

```sh
alembic upgread head
```

4. Start the server using `uvicorn`:

```sh
cd src && uvicorn app.main:app
```

If the virtual environment was not activated automatically, run this command:

```sh
source $(poetry env info --path)/bin/activate
```

5. Visit `http://localhost:8000/docs` for OpenAPI docs.

### Docker-compose

`docker-compose.yaml` and `docker-compose.override.yaml` are provided to quickly
spin up the backend, frontend, local PostgreSQL and a reverse proxy for developing
and testing the app.

1. First, make sure you cloned the [frontend](https://github.com/KirilStrezikozin/mini-chat-frontend) and
this backend repository to neighbouring directories, like this:

```txt
.
├── backend
└── frontend
```

By default, running `docker compose` will set up [Caddy](https://caddyserver.com/)
as a reverse-proxy for containers running the backend and frontend for this project
and forward traffic to `https://minichat.localhost` on your local device.
You can still visit `http://localhost:8000` for the API and `http://localhost:3000`
for the frontend. Communication, including login and signup, will only work if
you disable CORS middleware in `src/app/main.py` and in `next.config.ts`, and
set `USE_SECURE_COOKIES=False` environment variable.

In order to be able to visit `https://minichat.localhost`, add the following to
`/etc/hosts`:

```txt
127.0.0.1 minichat.localhost
```

2. Build the images and start containers:

```sh
docker compose up -d --build
```

3. Run database migrations:

```sh
docker exec -it minichat-backend-dev bash
```

Inside the container:

```sh
cd ..
alembic upgread head
```

4. You should now be able to access the frontend at `https://minichat.localhost`.

Caddy will automatically set up HTTPS with self-trusted certificates for this
hostname.


You can also run `caddy` outside of docker. `Caddyfile` describes the same 
configuration for `https://minichat.localhost`. Install `caddy`, update `etc/hosts`,
run `npm run dev` inside the frontend directory, and use the following command
instead for `docker compose`:

```sh
docker compose -f docker-compose.yaml up -d --build
```

Then, run `caddy`:

```sh
caddy run
```

See also: the [frontend](https://github.com/KirilStrezikozin/mini-chat-frontend) repository.
