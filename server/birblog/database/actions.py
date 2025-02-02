import datetime
import pydantic
import typing
import sqlmodel
import sqlalchemy.exc
import sys
import click

from birblog.database.models import Bird, Observation, Record, AlternativeName
from birblog.wikidata import get_bird_data
from birblog.database.query import check_has_entry

POSTGRES_URL_PATTERN: typing.Pattern[str] = (
    r"^postgresql:\/\/"  # Protocol
    r"(?P<username>[a-zA-Z0-9._%+-]+)"  # Username
    r"(:(?P<password>[^@:/]+))?"  # Optional password
    r"@(?P<host>[a-zA-Z0-9.-]+)"  # Host
    r"(:(?P<port>\d+))?"  # Optional port
    r"\/(?P<database>[a-zA-Z0-9_-]+)"  # Database name
    r"(\?(?P<params>.*))?$"  # Optional query parameters
)


def database_error_handler(action_func: typing.Callable) -> typing.Callable:
    def _wrapper(*args, **kwargs) -> typing.Any:
        try:
            action_func(*args, **kwargs)
        except sqlalchemy.exc.OperationalError as e:
            click.secho(e.args[0], fg="red", bold=True)
            sys.exit(122)

    _wrapper.__name__ = action_func.__name__
    return _wrapper


@pydantic.validate_call
@database_error_handler
def initialise_database(
    sql_database: typing.Annotated[str, pydantic.Field(pattern=POSTGRES_URL_PATTERN)],
) -> None:
    _engine = sqlmodel.create_engine(sql_database, echo=True)
    Observation.metadata.create_all(_engine)
    Record.metadata.create_all(_engine)
    AlternativeName.metadata.create_all(_engine)
    Bird.metadata.create_all(_engine)


def add_bird(
    sql_database: typing.Annotated[str, pydantic.Field(pattern=POSTGRES_URL_PATTERN)],
    bird: str
) -> Bird:
    _engine = sqlmodel.create_engine(sql_database, echo=True)
    with sqlmodel.Session(_engine) as session:
        if (_existing_bird := check_has_entry(bird, sql_database)):
            return session.get(Bird, _existing_bird)
        _bird = get_bird_data(bird)
        session.add(_bird)
        session.commit()
        return _bird


def add_observation(
    sql_database: typing.Annotated[str, pydantic.Field(pattern=POSTGRES_URL_PATTERN)],
    birds: list[str],
    observed_at: datetime.datetime,
) -> None:
    _engine = sqlmodel.create_engine(sql_database, echo=True)
    _records: list[Record] = []

    for bird in birds:
        _bird: Bird | None = None
        _existing_bird: int | None = None
        if not (_existing_bird := check_has_entry(bird, sql_database)):
            _bird = get_bird_data(bird)
        _records.append(Record(bird_id=_existing_bird, bird=_bird))

    with sqlmodel.Session(_engine) as session:
        _observation = Observation(log_time=observed_at, records=_records)
        session.add(_observation)
        session.commit()


def get_bird(
    bird_id: int,
    sql_database: typing.Annotated[str, pydantic.Field(pattern=POSTGRES_URL_PATTERN)]
) -> Bird | None:
    _engine = sqlmodel.create_engine(sql_database, echo=True)
    with sqlmodel.Session(_engine) as session:
        return session.get(Bird, bird_id)
