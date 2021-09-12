class AbstractClient:
    client = None

    def check_client(self):
        assert self.client is not None, 'Client not implemented'

    def get_client(self):
        self.check_client()
        return self.client
