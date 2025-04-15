from flask import Blueprint

serviceTicket_bp = Blueprint('serviceTicket_bp', __name__)

from . import routes

