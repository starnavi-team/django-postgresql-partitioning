# Django partitioning
Django partitioning is a package for Django,
which implement PostgreSQL
[table partitioning](https://www.postgresql.org/docs/10/static/ddl-partitioning.html)
on the fly, at the database level.
It creates several triggers and functions and inserts them directly into the database.
After setup partitioning, record will be inserted into the correct partition,
if partition doesn't exist, it will be created for you automatically.

## Requirements
- Django >=1.11 <=5.0
- PostgreSQL >= 8.0
- psycopg2-binary >=2.7.5 <= 2.9.9

## Installation
Install using `pip`...

```bash
$ pip install django-partitioning
```

## Configuration
- Add `partitioning` to `INSTALLED_APPS`:
```
INSTALLED_APPS = [
    ...
    partitioning,
]
```

- Add partitioning configuration to your models:
```
from partitioning.decorators import partitioning


@partitioning([
    {'type': 'list', 'column': 'tag'},
    {'type': 'range_month', 'column': 'created'},
])
class Message(models.Model):
    text = models.TextField()
    tag = models.CharField(max_length=255)
    created = models.DateTimeField()

```

- Lastly setup partitioning:
```bash
$ python manage.py setup_partitioning app_name
```

## Available settings
`type` - partition type, currently supported:
- list
- range_day
- range_week
- range_month
- range_year

`column` - column, used to determine which partition record belongs to.

## Testing

Install requirements.

```bash
$ pip install -r requirements.txt
```

Use the excellent [tox](http://tox.readthedocs.org/en/latest/) testing tool to run the tests against all supported versions of Python and Django. Install tox globally, and then simply run:

```bash
$ tox
```
