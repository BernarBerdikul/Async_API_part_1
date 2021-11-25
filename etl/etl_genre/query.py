query = """
    SELECT id, name, updated_at
    FROM content.genre
    WHERE updated_at > '%s'
    ORDER BY updated_at;
"""