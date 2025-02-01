import pydantic
import toml
import typing

class DatabaseConfig(pydantic.BaseModel):
    port: pydantic.PositiveInt
    domain: str | None = "localhost"
    username: str
    password: pydantic.SecretStr
    database: str

    @property
    def url(self) -> str:
        return ( f"postgresql://{self.username}:"
            f"{self.password.get_secret_value()}@"
            f"{self.domain}/{self.database}"
        )


class BirbLogConfig(pydantic.BaseModel):
    database: DatabaseConfig

    @classmethod
    @pydantic.validate_call
    def load(cls, config_file: pydantic.FilePath) -> typing.Self:
        with config_file.open() as in_f:
            return BirbLogConfig(**toml.load(in_f))