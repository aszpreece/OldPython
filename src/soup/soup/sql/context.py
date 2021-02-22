class Context:
    def __init__(self, username, logger, user_id):
        self.user_id = user_id
        self.username = username
        self.logger = logger