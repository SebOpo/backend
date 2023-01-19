## Prerequisites

- Python 3.8 + ([Ubuntu manual](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-an-ubuntu-20-04-server))
- PostgreSQL 14 ([Ubuntu manual](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart))
- Stackoverflow proficiency


## Project installation

Install the requirements
```
pip install -r requirements.txt
```

Create a new file - `.env` in the root folder of the project and fill it out the same as `.env.example`

-----------------------------------------------

## Shell script (Option 1)

On windows - just type the following to the command line of your IDE:
```
pre_start.sh
```

On Unix systems - type this:
```
/usr/bin/bash pre_start.sh
```

------------------------------------------------
## Default (Option 2)

Next up, create the db (requires postgresSQL installed) with:

```
alembic upgrade heads
```


If you have changed any models (or made any changes that require migrating the db) run:
```
alembic revision --autogenerate -m "Note text"
```

You might need to enter venv for this (not sure) :

On unix systems :
```
source venv/bin/activate
```

On windows :
```
venv/Scripts/activate.bat
```

------------------------

Run the `populate_db.py` file in the root of the project

```
python populate_db.py
```

Run the tests with :
```
pytest 
```
---------------------------------
## Run the project with :
```
uvicorn app.main:app --reload --port 7000
```

You can access Swagger docs by this [Link](http://127.0.0.1:7000/docs)


## Useful links :
- [Understanding the folder structure](https://lucid.app/lucidchart/f026bddf-3a41-4920-be8f-642f8e5b9691/edit?viewport_loc=106%2C-170%2C3328%2C1662%2C0_0&invitationId=inv_68cd2001-96e2-4d90-a944-2a32cd593611)
- [Fastapi](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Shapely](https://shapely.readthedocs.io/en/stable/)
- [Geopy](https://geopy.readthedocs.io/en/stable/)
- [OSMNX](https://osmnx.readthedocs.io/en/stable/)