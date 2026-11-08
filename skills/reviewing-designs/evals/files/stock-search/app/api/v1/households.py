"""Household lookup for referral partners (social-services agencies)."""

from dataclasses import asdict

from flask import jsonify

from ...households.store import load
from . import bp


@bp.get("/households/<int:household_id>")
def get_household(household_id: int):
    household = load(household_id)
    if household is None:
        return jsonify(error="not found"), 404
    data = asdict(household)
    data.pop("email")  # partners never see contact details
    return jsonify(data)
