from .element import Element


def nearest_gaps(selected: Element, all_elements: list[Element]) -> dict:
    """
    Returns the nearest gap in each direction from `selected` to other elements.
    Result: {direction: (distance_px, element) or None}
    """
    others = [e for e in all_elements if e.uid != selected.uid]

    directions = {
        "right":  lambda s, o: (o.x - s.x2,  o) if o.x  >= s.x2  and _v_overlap(s, o) else None,
        "left":   lambda s, o: (s.x  - o.x2, o) if o.x2 <= s.x   and _v_overlap(s, o) else None,
        "bottom": lambda s, o: (o.y  - s.y2, o) if o.y  >= s.y2  and _h_overlap(s, o) else None,
        "top":    lambda s, o: (s.y  - o.y2, o) if o.y2 <= s.y   and _h_overlap(s, o) else None,
    }

    result = {}
    for direction, fn in directions.items():
        best = None
        for other in others:
            val = fn(selected, other)
            if val is not None and val[0] >= 0:
                if best is None or val[0] < best[0]:
                    best = val
        result[direction] = best
    return result


def _v_overlap(a: Element, b: Element) -> bool:
    return a.y < b.y2 and b.y < a.y2


def _h_overlap(a: Element, b: Element) -> bool:
    return a.x < b.x2 and b.x < a.x2
