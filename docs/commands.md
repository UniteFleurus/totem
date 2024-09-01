
# Totem Useful Commands

All those commands are tools for developers or can be used as helpers in production environment (carefully of course). As they are django commands, some help can be found with

    docker-compose exec ./manage.py my_command --help

### Wait For Database

When starting the service, the database might not be ready to accept queries. Django will then crash. The command `wait_for_db` can be launched to make django wait before starting.

    docker-compose exec ./manage.py wait_for_db


### Tests

To run the test suite, use

    docker-compose exec django ./manage.py test --parallel --settings=totem.tests.settings

Specific test case can be specified with dot-notation like

    docker-compose exec django ./manage.py test user.tests.test_api --parallel --settings=totem.tests.settings

