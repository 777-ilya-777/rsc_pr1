class Session:
    def __init__(
        self,
        uid,
        datetime,
        locale
    ):
        self.uid = uid
        self.datetime = datetime
        self.locale = locale


class Prompt:
    def __init__(
        self,
        uid,
        datetime,
        parameter,
        session
    ):
        self.uid = uid
        self.datetime = datetime
        self.parameter = parameter
        self.session = session


class Feedback:
    def __init__(
        self,
        uid,
        datetime,
        response,
        status,
        error,
        prompt,
        cache_hit,
        duration
    ):
        self.uid = uid
        self.datetime = datetime
        self.response = response
        self.status = status
        self.error = error
        self.prompt = prompt
        self.cache_hit = cache_hit
        self.duration = duration