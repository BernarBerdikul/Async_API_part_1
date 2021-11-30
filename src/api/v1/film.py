from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.utils import FilmQueryParams
from src.models.film import DetailResponseFilm, FilmPagination
from src.models.person import FilmPerson
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/", response_model=FilmPagination)
async def search_film_list(
        params: FilmQueryParams = Depends(),
        film_service: FilmService = Depends(get_film_service),
        page: int = 1, page_size: int = 10

) -> FilmPagination:
    films: Optional[dict] = await film_service.get_all_films(
        params.sort, page, page_size, params.query, params.genre_filter)

    if not films:
        """ Если жанры не найдены, отдаём 404 статус """
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films not found')

    return FilmPagination(**films)


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
