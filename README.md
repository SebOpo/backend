Prerequisites
---------------------------------

- Docker: Desktop or standalone ([docker.com](https://www.docker.com/))
- Stackoverflow proficiency


Project installation
---------------------------------
Project uses `Makefile` to keep useful scripts in one place. You can join commands with `&&` to run them in one line.
ex: `make && make exec`.

- Create a `.env` new file:
`.env` in the root folder of the project and fill it out the same as `.env.example`
- Initialize and check if tests are passing:
```
make pre-start
```
- Start the project:
```
make
```

Update DB models
---------------------------------
If you have changed any models (or made any changes that require migrating the db) run:

Get shell of the application container.
``` 
make exec 
``` 
In the spawned shell run:
```
alembic revision --autogenerate -m "Note text"
```

To apply changes of the revision, simply restart the project (it runs `alembic upgrade head` on start).
```
make
```

Run the tests with:
---------------------------------
```
make test
```

Run the project with :
---------------------------------
```
make
```

You can access Swagger docs by this [Link](http://localhost:7000/docs)

## Useful links :
- [Understanding the folder structure](https://lucid.app/lucidchart/f026bddf-3a41-4920-be8f-642f8e5b9691/edit?viewport_loc=106%2C-170%2C3328%2C1662%2C0_0&invitationId=inv_68cd2001-96e2-4d90-a944-2a32cd593611)
- [Fastapi](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Shapely](https://shapely.readthedocs.io/en/stable/)
- [Geopy](https://geopy.readthedocs.io/en/stable/)
- [OSMNX](https://osmnx.readthedocs.io/en/stable/)