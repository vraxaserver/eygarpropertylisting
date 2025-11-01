# app/api/v1/endpoints/__init__.py
from app.api.v1.endpoints import properties
from app.api.v1.endpoints import reviews
from app.api.v1.endpoints import amenities
from app.api.v1.endpoints import my_properties
from app.api.v1.endpoints import experiences
from app.api.v1.endpoints import vendors
from app.api.v1.endpoints import coupons

__all__ = [
    'properties',
    'reviews',
    'amenities',
    'my_properties',
    'experiences',
    'vendors',
    'coupons'
]
