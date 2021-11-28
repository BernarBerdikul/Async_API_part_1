from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.models.person import DetailResponsePerson, PersonPagination
from src.services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/search', response_model=PersonPagination)
async def person_search(
    query: str,
    person_service: PersonService = Depends(get_person_service),
    page: int = 1, page_size: int = 10
) -> PersonPagination:
    persons: Optional[dict] = await person_service.search_person(
        query=query, page=page, page_size=page_size
    )
    if not persons:
        """ Если персоны не найдены, отдаём 404 статус """
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='persons not found')
    return PersonPagination(**persons)


@router.get('/{person_id}', response_model=DetailResponsePerson)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> DetailResponsePerson:
    person = await person_service.get_by_id(person_id=person_id)
    if not person:
        """ Если персона не найдена, отдаём 404 статус """
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')
    return DetailResponsePerson(
        uuid=person.id,
        full_name=person.full_name,
        role=person.roles[0],
        film_ids=person.film_ids
    )
