from .schema_template import TEMPLATE_INDEX_BODY


FILM_WORK_INDEX_BODY: dict = {
  **TEMPLATE_INDEX_BODY,
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "uuid": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "ru_en",
        "fields": {
          "raw": {
            "type": "keyword"
          }
        }
      },
      "imdb_rating": {
        "type": "float"
      },
      "description": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "genre": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          },
          "uuid": {
            "type": "keyword"
          }
        }
      },
      "actors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "uuid": {
            "type": "keyword"
          },
          "full_name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "writers": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "uuid": {
            "type": "keyword"
          },
          "full_name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "directors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "uuid": {
            "type": "keyword"
          },
          "full_name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
    }
  }
}
