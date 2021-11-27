from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.models.film import DetailResponseFilm
from src.models.person import FilmPerson
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get('/', response_model=DetailResponseFilm)
async def film_list(
        film_id: str, film_service: FilmService = Depends(get_film_service)
) -> DetailResponseFilm:
    pass


@router.get('/{film_id}', response_model=DetailResponseFilm)
async def film_details(
        film_id: str, film_service: FilmService = Depends(get_film_service)
) -> DetailResponseFilm:
    film = await film_service.get_by_id(film_id=film_id)
    if not film:
        """ Если фильм не найден, отдаём 404 статус """
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    actors_list: List[FilmPerson] = [
        FilmPerson(
            uuid=actor.get("id"),
            full_name=actor.get("name")
        )
        for actor in film.actors
    ]
    writers_list: List[FilmPerson] = [
        FilmPerson(
            uuid=actor.get("id"),
            full_name=actor.get("name")
        )
        for actor in film.writers
    ]
    return DetailResponseFilm(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        actors=actors_list,
        writers=writers_list,
    )
