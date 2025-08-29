from django.shortcuts import render, redirect
from django.conf import settings
from . import services

def pokemon_list(request):
    error = None
    try:
        types = services.get_types().get("results", [])
        abilities = services.get_all_abilities()
    except Exception as e:
        types, abilities = [], []
        error = f"Failed to load filter lists: {e}"

    q = request.GET.get("q")
    type_name = request.GET.get("type")
    ability = request.GET.get("ability")
    page = int(request.GET.get("page", "1"))
    page_size = int(request.GET.get("page_size", settings.PAGE_SIZE))

    try:
        if type_name:
            data = services.filter_pokemon_by_type(type_name, page=page, page_size=page_size)
            results = data["results"]; total = data["count"]
        elif ability:
            data = services.filter_pokemon_by_ability(ability, page=page, page_size=page_size)
            results = data["results"]; total = data["count"]
        elif q:
            data = services.search_pokemon(q, page=page, page_size=page_size)
            results = data["results"]; total = data["count"]
        else:
            offset = (page-1) * page_size
            data = services.list_pokemon(offset=offset, limit=page_size)
            total = data.get("count", 0)
            results = []
            for item in data.get("results", []):
                try:
                    results.append(services.get_pokemon(item["name"]))
                except Exception:
                    pass
        has_next = page * page_size < total
        has_prev = page > 1
    except services.PokeAPIError as e:
        error = str(e)
        results, total, has_next, has_prev = [], 0, False, False

    return render(request, "pokedex/list.html", {
        "types": types,
        "abilities": abilities,
        "pokemon_list": results,
        "page": page, "page_size": page_size,
        "has_next": has_next, "has_prev": has_prev,
        "q": q or "", "type_selected": type_name or "", "ability_selected": ability or "",
        "total": total, "error": error,
    })

def pokemon_detail(request, identifier):
    error = None
    try:
        pokemon = services.get_pokemon(identifier)
        species = services.get_pokemon_species(identifier)
        evolution_names = services.evo_chain_names(services.get_evolution_chain_by_pokemon(identifier))
    except Exception as e:
        pokemon, species, evolution_names = None, None, []
        error = f"Could not load Pokémon: {e}"

    if request.GET.get("compare_with"):
        other = request.GET["compare_with"].strip()
        if other:
            return redirect(f"/compare/?a={identifier}&b={other}")

    return render(request, "pokedex/detail.html", {
        "pokemon": pokemon, "species": species, "evolution_names": evolution_names, "error": error
    })

# def compare_view(request):
#     a = request.GET.get("a", "").strip() or "pikachu"
#     b = request.GET.get("b", "").strip() or "bulbasaur"
#     error = None
#     try:
#         pa = services.get_pokemon(a)
#         pb = services.get_pokemon(b)
#     except Exception as e:
#         pa = pb = None
#         error = f"Compare failed: {e}"
#     return render(request, "pokedex/compare.html", {"a": pa, "b": pb, "a_name": a, "b_name": b, "error": error})
def compare_view(request):
    a_name = (request.GET.get("a") or "pikachu").strip()
    b_name = (request.GET.get("b") or "bulbasaur").strip()

    error = None
    try:
        a = services.get_pokemon(a_name)
    except Exception as e:
        a, error = None, f"Couldn't load {a_name}: {e}"
    try:
        b = services.get_pokemon(b_name)
    except Exception as e:
        b = None
        error = (error + " | " if error else "") + f"Couldn't load {b_name}: {e}"

    # 👉 pass a real list to the template
    pair = [p for p in (a, b) if p]

    return render(
        request,
        "pokedex/compare.html",
        {"pair": pair, "a_name": a_name, "b_name": b_name, "error": error},
    )

def coverage_view(request):
    team = request.GET.get("team", "pikachu,bulbasaur,charizard")
    names = [x.strip() for x in team.split(",") if x.strip()][:6]
    error = None
    try:
        summary = services.team_coverage(names)
    except Exception as e:
        summary = {}
        error = f"Coverage failed: {e}"
    return render(request, "pokedex/coverage.html", {"team": names, "summary": summary, "error": error})

def average_view(request):
    team = request.GET.get("team", "pikachu,bulbasaur,charizard")
    names = [x.strip() for x in team.split(",") if x.strip()][:6]
    error = None
    try:
        avg = services.average_stats(names)
    except Exception as e:
        avg = {}
        error = f"Average calc failed: {e}"
    return render(request, "pokedex/average.html", {"team": names, "avg": avg, "error": error})

def evolution_view(request, identifier):
    try:
        evo = services.get_evolution_chain_by_pokemon(identifier)
    except Exception as e:
        evo = {"error": str(e)}
    return render(request, "pokedex/evolution.html", {"evo": evo})
