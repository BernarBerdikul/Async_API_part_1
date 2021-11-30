
def get_params_films_to_elastic(
        page_size: int, page: int, genre: str = None, query: str = None):
    """
    :param page:
    :param page_size:
    :param genre: фильтрует фильмы по жанру
    :param query: находит фильмы по полю title
    :return: возвращает правильный body для поиска в Elasticsearch
    """
    if genre is None:
        genre_search = []
    else:
        genre_search = [{"term": {"genre": genre}}]

    body = {
        "size": page_size,
        "from": (page - 1) * page_size,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "title": {
                            "query": query,
                            "fuzziness": "auto"
                        }
                    }
                },
                "filter": genre_search
            }
        }}

    if query is None:
        body = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {},
                    },
                    "filter": genre_search
                }
            }}

    return body
