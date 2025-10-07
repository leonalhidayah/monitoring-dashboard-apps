from views.config import ADV_MP_MAP_PROJECT
from views.render_pages import render_marketplace_page
from views.style import load_css

load_css()

project_name = "HPI"

render_marketplace_page(project_name, ADV_MP_MAP_PROJECT[project_name])
