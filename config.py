token = ''

proxy = True
class proxy_settings():
    def __init__(self, address = '', port = '', user = '', password = ''):
        self.address = address
        self.port = port
        self.user = user
        self.password = password


database = 'datasets'
collection = 'habrahabr'
id_prefix = 'habr_'
model = 'habr_model'

