from sanic import Sanic

from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.accounts import accounts_bp
from app.routes.payments import payments_bp
from app.routes.webhook import webhook_bp

app = Sanic("TestApp")

app.blueprint(auth_bp)
app.blueprint(users_bp)
app.blueprint(accounts_bp)
app.blueprint(payments_bp)
app.blueprint(webhook_bp)
