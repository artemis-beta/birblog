import click
import pathlib
import datetime
import typing
import pydantic

from birblog.database.actions import initialise_database, add_observation
from birblog.config import BirbLogConfig
from birblog.database.query import check_has_entry 


@click.group("birblog")
@click.option(
    "--config",
    "-c",
    "config_file",
    help="Configuration file",
    default=pathlib.Path.cwd().joinpath("birblog.toml"),
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path),
)
@click.pass_context
def birblog(ctx, config_file: pathlib.Path):
    """Bird logging server CLI"""
    ctx.obj = BirbLogConfig.load(config_file)


@birblog.group("server")
@click.pass_context
def server(_):
    """Manage the BirbLog server"""
    pass


@server.command("init")
@click.pass_context
def init_db(ctx):
    """Initialise the BirbLog Database"""
    initialise_database(ctx.obj.database.url)


@server.command("log")
@click.argument("bird_species")
@click.option(
    "--observed", help="Observation time in the form 'YYYY-MM-DDTHH:MM'", default=None
)
@click.pass_context
@pydantic.validate_call
def observation(
    ctx,
    bird_species: str,
    observed: typing.Annotated[
        str, pydantic.Field(pattern=r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
    ] | None = None,
) -> None:
    """Add an observation"""
    _observed = (
        datetime.datetime.strptime(observed, "%Y-%m-%dT%H:%M")
        if observed
        else datetime.datetime.now(datetime.UTC)
    )

    add_observation(
        sql_database=ctx.obj.database.url, birds=[bird_species], observed_at=_observed
    )
