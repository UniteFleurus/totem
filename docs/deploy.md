
# Push Deployment


## Environment Variables

Here is a list of required environment variables to run the django container of the Insights Service. They are split in categories, usually prefixed by the component name. Only native django settings and insights business-related are prefixed by `TOTEM_`.

### Django

 - `TOTEM_DEBUG`: boolean, indicating if django should run in debug mode or not. Default is `False`.
 - `TOTEM_SECRET_KEY`: string, the django secret key.

### Postgres

- `POSTGRES_NAME`: string, the name of the django database to use
- `POSTGRES_USER`: string, username to access the psql server
- `POSTGRES_PASSWORD`: string, user password to access the psql server
- `POSTGRES_HOST`: string, the URL of the psql server
- `POSTGRES_PORT`: string, the port of psql server
