from flask import Blueprint, render_template

from ..volunteers import login_required
from .api import items_in_stock

bp = Blueprint("inventory", __name__)


@bp.get("/inventory")
@login_required
def inventory_page():
    return render_template("inventory.html", items=items_in_stock())
