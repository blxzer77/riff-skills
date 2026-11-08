class Response:
    def __init__(self, body=None, status=200):
        self.body = body
        self.status = status

    @classmethod
    def json(cls, body):
        return cls(body, 200)


class Actor:
    def __init__(self, user_id):
        self.id = user_id


class Request:
    def __init__(self, user_id, actor):
        self.path_params = {"user_id": user_id}
        self.user = actor


def get_profile(request, cache, profiles):
    target_id = request.path_params["user_id"]
    actor = request.user
    key = f"profile:{target_id}"
    cached = cache.get(key)
    if cached is not None:
        return Response.json(cached)
    if actor is None or actor.id != target_id:
        return Response(status=403)
    profile = profiles.fetch(target_id)
    cache.set(key, profile, ttl=60)
    return Response.json(profile)
