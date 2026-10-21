from app import filters
from app.views import statement

statement.render(filters.sidebar())
