from django.conf import settings
from django.core.cache import cache
import requests
from urllib.parse import urljoin

BASE = getattr(settings, "POKEAPI_BASE_URL", "https://pokeapi.co/api/v2")
TTL = getattr(settings, "CACHE_TTL", 3600)

class PokeAPIError(Exception):
    pass

def _get(url, params=None, ttl=TTL):
    key = f"poke:{url}:{params}"
    data = cache.get(key)
    if data is not None:
        return data
    try:
        resp = requests.get(url, params=params, timeout=30)
    except requests.RequestException as e:
        raise PokeAPIError(f"Network error to PokeAPI: {e}")
    if resp.status_code != 200:
        raise PokeAPIError(f"PokeAPI error {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    cache.set(key, data, ttl)
    return data

def list_pokemon(offset=0, limit=20):
    url = urljoin(BASE + "/", "pokemon/")
    return _get(url, params={"offset": offset, "limit": limit})

def get_pokemon(identifier):
    url = urljoin(BASE + "/", f"pokemon/{identifier}/")
    return _get(url)

def get_pokemon_species(identifier):
    url = urljoin(BASE + "/", f"pokemon-species/{identifier}/")
    return _get(url)

def get_types():
    url = urljoin(BASE + "/", "type/")
    return _get(url)

def get_type_detail(name):
    url = urljoin(BASE + "/", f"type/{name}/")
    return _get(url)

def get_ability_detail(name):
    url = urljoin(BASE + "/", f"ability/{name}/")
    return _get(url)

def get_all_abilities():
    url = urljoin(BASE + "/", "ability/")
    data = _get(url, params={"limit": 10000})
    return [a["name"] for a in data.get("results", [])]

def get_evolution_chain_by_pokemon(identifier):
    species = get_pokemon_species(identifier)
    evo_url = species.get("evolution_chain", {}).get("url")
    if not evo_url:
        return None
    return _get(evo_url)

def filter_pokemon_by_type(type_name, page=1, page_size=24):
    td = get_type_detail(type_name)
    all_entries = [p["pokemon"]["name"] for p in td.get("pokemon", [])]
    total = len(all_entries)
    start = (page - 1) * page_size
    end = start + page_size
    slice_names = all_entries[start:end]
    results = []
    for name in slice_names:
        try:
            results.append(get_pokemon(name))
        except Exception:
            pass
    return { "count": total, "results": results }

def filter_pokemon_by_ability(ability_name, page=1, page_size=24):
    ab = get_ability_detail(ability_name)
    all_entries = [p["pokemon"]["name"] for p in ab.get("pokemon", [])]
    total = len(all_entries)
    start = (page - 1) * page_size
    end = start + page_size
    slice_names = all_entries[start:end]
    results = []
    for name in slice_names:
        try:
            results.append(get_pokemon(name))
        except Exception:
            pass
    return { "count": total, "results": results }

def search_pokemon(query, page=1, page_size=24):
    try:
        p = get_pokemon(query.lower())
        return { "count": 1, "results": [p] }
    except Exception:
        limit_pages = 5
        aggregated = []
        for i in range(limit_pages):
            page_data = list_pokemon(offset=i*200, limit=200)
            for item in page_data.get("results", []):
                if query.lower() in item["name"]:
                    try:
                        aggregated.append(get_pokemon(item["name"]))
                    except Exception:
                        pass
        total = len(aggregated)
        start = (page - 1) * page_size
        end = start + page_size
        return { "count": total, "results": aggregated[start:end] }

def evo_chain_names(evo):
    if not evo or "chain" not in evo:
        return []
    names = []
    def walk(node):
        names.append(node["species"]["name"])
        for nxt in node.get("evolves_to", []):
            walk(nxt)
    walk(evo["chain"])
    return names

def average_stats(pokemon_names):
    totals = {}
    count = 0
    for n in pokemon_names:
        try:
            p = get_pokemon(n)
            for s in p.get("stats", []):
                key = s["stat"]["name"]
                totals[key] = totals.get(key, 0) + int(s["base_stat"])
            count += 1
        except Exception:
            continue
    if count == 0:
        return {}
    return {k: round(v / count, 2) for k, v in totals.items()}

def team_coverage(team_names):
    type_list = [t["name"] for t in get_types().get("results", [])]
    detail_cache = {t: get_type_detail(t) for t in type_list}
    rel = {}
    for t, d in detail_cache.items():
        dr = d.get("damage_relations", {})
        rel[t] = {
            "double_from": [x["name"] for x in dr.get("double_damage_from", [])],
            "half_from":   [x["name"] for x in dr.get("half_damage_from", [])],
            "no_from":     [x["name"] for x in dr.get("no_damage_from", [])],
        }
    team_types = []
    for n in team_names:
        try:
            p = get_pokemon(n)
            team_types.append([tt["type"]["name"] for tt in p.get("types", [])])
        except Exception:
            team_types.append([])
    summary = {t: {"weak": 0, "resist": 0, "immune": 0} for t in type_list}
    for attack_type in type_list:
        weak_set = set(rel[attack_type]["double_from"])
        resist_set = set(rel[attack_type]["half_from"])
        immune_set = set(rel[attack_type]["no_from"])
        for ptypes in team_types:
            if any(pt in immune_set for pt in ptypes):
                summary[attack_type]["immune"] += 1
            elif any(pt in weak_set for pt in ptypes):
                summary[attack_type]["weak"] += 1
            elif any(pt in resist_set for pt in ptypes):
                summary[attack_type]["resist"] += 1
    return summary
