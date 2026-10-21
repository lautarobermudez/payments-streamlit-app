from app import filters
from app.views import orders

orders.render(filters.sidebar())
