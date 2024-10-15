
# Totem Deployment

## How To Deploy Locally ?

Once you have checkout this repository with `git clone`, you can run the docker containers locally with

`docker compose up --build` (or without the `--build` option, to avoid buiding the docker image).

Then, to load local data to ease the development, use

`docker compose exec django ./manage.py populate` (See the `commands` section for more details).

This is done, you can go to `http://localhost:8000` to enjoy the public website, or on `http://localhost:8000/admin` to access the native django administration (login and password are `admin`).

When coding, python code is automatically reloaded. Jinja2 Template requires a container restart (maybe a build).


## Environment Variables

Here is a list of required environment variables to run the django container of the Totem Service. They are split in categories, usually prefixed by the component name. Only native django settings and totem business-related are prefixed by `TOTEM_`.

### Django

 - `TOTEM_DEBUG`: boolean, indicating if django should run in debug mode or not. Default is `False`.
 - `TOTEM_SECRET_KEY`: string, the django secret key.
  - `TOTEM_CSRF_TRUSTED_ORIGINS`: comma separated complete url of trusted origins. Django 4 required it. Example: `http://localhost:8104,https://mydomain.com:8104`


### Postgres

- `POSTGRES_NAME`: string, the name of the django database to use
- `POSTGRES_USER`: string, username to access the psql server
- `POSTGRES_PASSWORD`: string, user password to access the psql server
- `POSTGRES_HOST`: string, the URL of the psql server
- `POSTGRES_PORT`: string, the port of psql server
