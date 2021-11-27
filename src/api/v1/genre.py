from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.models.genre import DetailResponseGenre
from src.services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}', response_model=DetailResponseGenre)
async def genre_details(
        genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> DetailResponseGenre:
    genre = await genre_service.get_by_id(genre_id=genre_id)
    if not genre:
        """ Если жанр не найден, отдаём 404 статус """
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')
    return DetailResponseGenre(
        uuid=genre.id,
        name=genre.name,
    )
