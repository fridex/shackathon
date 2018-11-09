import connexion

app = connexion.App(__name__)
application = app.app
app.add_api('swagger.yaml')

def a():
    return {'hello': 'translate'}
