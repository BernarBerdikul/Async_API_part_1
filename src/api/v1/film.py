from http import HTTPStatus
from typing import List
from fastapi_pagination import Page, add_pagination, paginate

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination.bases import AbstractPage

from src.api.v1.utils import FilmQueryParams
from src.models.film import DetailResponseFilm, ListResponseFilm
from src.models.person import FilmPerson
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/", response_model=Page[ListResponseFilm])
async def search_film_list(
        params: FilmQueryParams = Depends(),
        film_service: FilmService = Depends(get_film_service),

) -> AbstractPage[ListResponseFilm]:
    films = await film_service.get_all_films(params.sort, params.query, params.genre_filter)

    result = [
        ListResponseFilm(
                uuid=row.id,
                title=row.title,
                imdb_rating=row.imdb_rating
            )
        for row in films
    ]

    return paginate(result)


add_pagination(router)


@router.get('/{film_id}', response_model=DetailResponseFilm)
async def film_details(
        film_id: str, film_service: FilmService = Depends(get_film_service)
) -> DetailResponseFilm:
    film = await film_service.get_by_id(film_id)
    if not film:
        """ Если фильм не найден, отдаём 404 статус """
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    actors_list: List[FilmPerson] = [
        FilmPerson(
            **actor
        )
        for actor in film.actors
    ]
    writers_list: List[FilmPerson] = [
        FilmPerson(
            **writer
        )
        for writer in film.writers
    ]
    directors_list: List[FilmPerson] = [
        FilmPerson(
            **director
        )
        for director in film.directors
    ]

    return DetailResponseFilm(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        actors=actors_list,
        writers=writers_list,
        directors=directors_list,
    )