from django import template
import json
register = template.Library()

@register.filter
def sprite_url(p):
    if not isinstance(p, dict):
        return None
    sprites = p.get("sprites") or {}
    other = sprites.get("other") or {}
    off = other.get("official-artwork") or {}
    return off.get("front_default") or sprites.get("front_default")

@register.filter
def pretty_json(obj):
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return ""
