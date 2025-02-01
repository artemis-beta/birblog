import wikidspark.query
import requests
import http
import typing
import flatdict
import urllib.parse
import tempfile

from birblog.database.models import Bird, Image, AlternativeName


def get_property(bird_id: str, property_id: str, bird_data: dict[str, typing.Any]) -> str:
    _data_flattened = flatdict.FlatterDict(bird_data, delimiter=".")
    
    _address: list[str] = [
        "entities",
        bird_id,
        "claims",
        property_id,
        "0",
        "mainsnak",
        "datavalue",
        "value"
    ]

    return _data_flattened[".".join(_address)]


def get_mass(bird_id: str, bird_data: dict[str, typing.Any]) -> float:
    _mass: dict[str, str] = get_property(bird_id, "P2067", bird_data)
    _value: float = float(_mass["amount"])
    _unit_conversion: dict[str, float] = {
        "Q41803": 0.001,
        "Q11570": 1.0
    }
    _key = _mass["unit"].rsplit("/")[-1]
    return _value * _unit_conversion[_key]


def get_wingspan(bird_id: str, bird_data: dict[str, typing.Any]) -> float:
    _mass: dict[str, str] = get_property(bird_id, "P2050", bird_data)
    _value: float = float(_mass["amount"])
    _unit_conversion: dict[str, float] = {
        "Q174728": 0.01,
        "Q174789": 0.001,
        "Q11573": 1.0,
    }
    _key = _mass["unit"].rsplit("/")[-1]
    return _value * _unit_conversion[_key]


def get_image(bird_id: str, bird_data: dict[str, typing.Any]) -> bytes | None:
    _file_name: str = urllib.parse.quote(get_property(bird_id, "P18", bird_data))
    _url: str = f"https://commons.wikimedia.org/wiki/Special:FilePath/{_file_name}"
    _response = requests.get(_url)

    if _response.status_code != http.HTTPStatus.OK:
        return None
    
    return _response.content
        

def get_bird_data(bird_name: str) -> Bird:
    _wikidspark_result: wikidspark.query.WikidataIDResponse = wikidspark.query.get_by_name(bird_name)
    if not _wikidspark_result.aliases:
        return None
    _aliases: set[str] = set(s.lower() for s in _wikidspark_result.aliases + [bird_name])
    _query_url: str = f"https://www.wikidata.org/wiki/Special:EntityData/{_wikidspark_result.id}.json"
    _result: requests.Response = requests.get(
        url=_query_url
    )
    
    if _result.status_code != http.HTTPStatus.OK:
        return None

    _taxon_name: str = get_property(_wikidspark_result.id, "P225", _result.json())
    _mass: float = get_mass(_wikidspark_result.id, _result.json())
    _image: bytes = get_image(_wikidspark_result.id, _result.json())
    _wingspan: float = get_wingspan(_wikidspark_result.id, _result.json())


    return Bird(
        taxon_name=_taxon_name,
        mass=_mass,
        wingspan=_wingspan,
        wikidata_id=_wikidspark_result.id,
        images=[
            Image(data=_image)
        ],
        alternative_names = [
        AlternativeName(name=alias)
            for alias in _aliases
        ]
    )



