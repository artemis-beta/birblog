import sqlmodel

from birblog.database.models import AlternativeName

def check_has_entry(bird_name: str, endpoint: str) -> int | None:
    _engine = sqlmodel.create_engine(endpoint)
    with sqlmodel.Session(_engine) as session:
        _query = sqlmodel.select(AlternativeName).where(
            AlternativeName.name == bird_name.lower()
        )
        try:
            _alternative_name = next(session.exec(_query))
        except StopIteration:
            return None
        
        return _alternative_name.bird_id
