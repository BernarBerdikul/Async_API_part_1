from typing import List, Optional
from pydantic import BaseModel
from src.models.mixin import BaseModelMixin, PaginationMixin
from uuid import UUID


class ElasticPerson(BaseModel):
    id: str
    full_name: str
    roles: Optional[List[str]] = []
    film_ids: Optional[List[UUID]] = []


class FilmPerson(BaseModelMixin):
    """ Schema for Film work detail """
    full_name: str


class DetailResponsePerson(FilmPerson):
    """ Schema for Person detail """
    role: str
    film_ids: Optional[List[UUID]] = []


class PersonPagination(PaginationMixin):
    persons: List[DetailResponsePerson] = []
