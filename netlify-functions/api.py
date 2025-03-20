from app import app
from flask_lambda import function

@function
def handler(event, context):
    return app(event, context)
