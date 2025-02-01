import sqlmodel
import datetime

class Observation(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    log_time: datetime.datetime 
    records: list["Record"] = sqlmodel.Relationship(back_populates="observation")

class Bird(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    taxon_name: str = sqlmodel.Field(unique=True)
    mass: float | None
    wingspan: float
    wikidata_id: str
    records: list["Record"] =sqlmodel.Relationship(back_populates="bird")
    alternative_names: list["AlternativeName"] = sqlmodel.Relationship(back_populates="bird")
    images: list["Image"] = sqlmodel.Relationship(back_populates="bird")

class Image(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    data: bytes
    bird_id: int | None = sqlmodel.Field(default=None, foreign_key="bird.id")
    bird: Bird | None = sqlmodel.Relationship(back_populates="images")

class AlternativeName(sqlmodel.SQLModel, table=True):
    __tablename__ = "alternative_name"
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(unique=True)
    bird_id: int | None = sqlmodel.Field(foreign_key="bird.id")
    bird: Bird | None = sqlmodel.Relationship(back_populates="alternative_names")

class Record(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    bird_id: int = sqlmodel.Field(foreign_key="bird.id")
    bird: Bird | None = sqlmodel.Relationship(back_populates="records")
    observation_id: int | None = sqlmodel.Field(foreign_key="observation.id")
    observation: Observation | None = sqlmodel.Relationship(back_populates="records")