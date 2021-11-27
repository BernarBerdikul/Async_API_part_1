from typing import Optional, List, Dict

from pydantic import BaseModel

from src.models.mixin import BaseModelMixin
from src.models.person import FilmPerson
from src.models.genre import FilmGenre
<<<<<<< HEAD
=======

>>>>>>> etl_gesammelt

class ElasticFilm(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = None
    genre: Optional[List[str]] = None
    director: Optional[List[str]] = None
    actors: Optional[List[Dict[str, str]]] = None
    writers: Optional[List[Dict[str, str]]] = None


class ListResponseFilm(BaseModelMixin):
    """ Schema for Film work list """
    title: str
    imdb_rating: Optional[float] = None


class DetailResponseFilm(ListResponseFilm):
    """ Schema for Film work detail """
    description: Optional[str] = None
    genre: Optional[List[FilmGenre]] = []
    actors: Optional[List[FilmPerson]] = []
    writers: Optional[List[FilmPerson]] = []
    directors: Optional[List[FilmPerson]] = []
