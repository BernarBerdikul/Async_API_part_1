from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from models.film import FilmPagination
from models.person import DetailResponsePerson, PersonPagination
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get("/search", response_model=PersonPagination)
async def person_search(
    query: str,
    person_service: PersonService = Depends(get_person_service),
    page: int = 1,
    page_size: int = 10,
) -> PersonPagination:
    persons: Optional[dict] = await person_service.search_person(
        query=query, page=page, page_size=page_size
    )
    if not persons:
        """Если персоны не найдены, отдаём 404 статус"""
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="persons not found"
        )
    return PersonPagination(**persons)


@router.get("/{person_id}", response_model=DetailResponsePerson)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> DetailResponsePerson:
    person = await person_service.get_person(person_id=person_id)
    return DetailResponsePerson(
        uuid=person.id,
        full_name=person.full_name,
        role=person.roles[0],
        film_ids=person.film_ids,
    )


@router.get("/{person_id}/film/", response_model=FilmPagination)
async def person_details(
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
    page: int = 1,
    page_size: int = 10,
) -> FilmPagination:
    person = await person_service.get_person(person_id=person_id)
    person_films = await person_service.get_person_films(
        film_ids=person.film_ids, page=page, page_size=page_size
    )
    if not person_films:
        """Если персона не найдена, отдаём 404 статус"""
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="person's films not found"
        )
    return FilmPagination(**person_films)
