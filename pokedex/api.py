from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.conf import settings
from . import services

def _card(p):
    image = p.get("sprites", {}).get("other", {}).get("official-artwork", {}).get("front_default") or             p.get("sprites", {}).get("front_default")
    return {
        "id": p.get("id"),
        "name": p.get("name"),
        "image": image,
        "types": [t["type"]["name"] for t in p.get("types", [])],
        "height": p.get("height"),
        "weight": p.get("weight"),
        "stats": { s["stat"]["name"]: s["base_stat"] for s in p.get("stats", []) },
    }

def _ok(data, status=200):
    return JsonResponse(data, status=status)

def _err(message, status=502, hint=None):
    payload = {"error": message}
    if hint:
        payload["hint"] = hint
    return JsonResponse(payload, status=status)

@require_GET
def pokemon_index(request):
    try:
        q = request.GET.get("q")
        type_name = request.GET.get("type")
        ability_name = request.GET.get("ability")
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", settings.PAGE_SIZE))

        if type_name:
            data = services.filter_pokemon_by_type(type_name, page=page, page_size=page_size)
            return _ok({"count": data["count"], "results": [_card(p) for p in data["results"]]})

        if ability_name:
            data = services.filter_pokemon_by_ability(ability_name, page=page, page_size=page_size)
            return _ok({"count": data["count"], "results": [_card(p) for p in data["results"]]})

        if q:
            data = services.search_pokemon(q, page=page, page_size=page_size)
            return _ok({"count": data["count"], "results": [_card(p) for p in data["results"]]})

        offset = (page-1) * page_size
        data = services.list_pokemon(offset=offset, limit=page_size)
        enriched = []
        for item in data.get("results", []):
            try:
                enriched.append(_card(services.get_pokemon(item["name"])))
            except Exception:
                pass
        return _ok({"count": data.get("count", 0), "results": enriched})
    except services.PokeAPIError as e:
        return _err(str(e), hint="The Pokémon escaped our request. Try again.")
    except Exception as e:
        return _err(f"Unexpected error: {e}", status=500)

@require_GET
def pokemon_detail(request, identifier):
    try:
        p = services.get_pokemon(identifier)
        species = services.get_pokemon_species(identifier)
        evo = services.get_evolution_chain_by_pokemon(identifier)
        evo_names = services.evo_chain_names(evo)
        flavor = ""
        for ft in species.get("flavor_text_entries", []):
            if ft.get("language", {}).get("name") == "en":
                flavor = ft.get("flavor_text", "").replace("\n", " ").replace("\f", " ")
                break
        return _ok({
            "pokemon": _card(p) | {"abilities": [a["ability"]["name"] for a in p.get("abilities", [])]},
            "species": {"name": species.get("name"), "flavor_text": flavor},
            "evolution": {"names": evo_names},
        })
    except services.PokeAPIError as e:
        return _err(str(e), hint="Double-check the name or ID.")
    except Exception as e:
        return _err(f"Unexpected error: {e}", status=500)

@require_GET
def compare_api(request):
    a = request.GET.get("a")
    b = request.GET.get("b")
    if not a or not b:
        return _err("Provide a and b query params", status=400)
    try:
        pa = services.get_pokemon(a)
        pb = services.get_pokemon(b)
        return _ok({"a": _card(pa), "b": _card(pb)})
    except services.PokeAPIError as e:
        return _err(str(e))
    except Exception as e:
        return _err(f"Unexpected error: {e}", status=500)

@require_GET
def types_api(request):
    try:
        t = services.get_types()
        return _ok(t)
    except Exception as e:
        return _err(str(e))

@require_GET
def abilities_api(request):
    try:
        names = services.get_all_abilities()
        return _ok({"count": len(names), "results": names})
    except Exception as e:
        return _err(str(e))

@require_GET
def evolution_api(request, identifier):
    try:
        evo = services.get_evolution_chain_by_pokemon(identifier)
        return _ok({"names": services.evo_chain_names(evo)})
    except Exception as e:
        return _err(str(e))

@require_GET
def coverage_api(request):
    team = request.GET.get("team", "")
    names = [x.strip() for x in team.split(",") if x.strip()]
    try:
        summary = services.team_coverage(names[:6])
        return _ok({"team": names[:6], "coverage": summary})
    except Exception as e:
        return _err(str(e))

@require_GET
def average_api(request):
    team = request.GET.get("team", "")
    names = [x.strip() for x in team.split(",") if x.strip()][:6]
    try:
        avg = services.average_stats(names)
        return _ok({"team": names, "average_stats": avg})
    except Exception as e:
        return _err(str(e))
