from django.urls import path
from . import views, api

urlpatterns = [
    path("pokemon/", views.pokemon_list, name="pokemon_list"),
    path("pokemon/<slug:identifier>/", views.pokemon_detail, name="pokemon_detail"),
    path("compare/", views.compare_view, name="compare"),
    path("coverage/", views.coverage_view, name="coverage"),
    path("average/", views.average_view, name="average"),
    path("evolution/<slug:identifier>/", views.evolution_view, name="evolution"),
    path("api/pokemon/", api.pokemon_index, name="api_pokemon_index"),
    path("api/pokemon/<slug:identifier>/", api.pokemon_detail, name="api_pokemon_detail"),
    path("api/compare/", api.compare_api, name="api_compare"),
    path("api/types/", api.types_api, name="api_types"),
    path("api/abilities/", api.abilities_api, name="api_abilities"),
    path("api/evolution/<slug:identifier>/", api.evolution_api, name="api_evolution"),
    path("api/coverage/", api.coverage_api, name="api_coverage"),
    path("api/average/", api.average_api, name="api_average"),
]
