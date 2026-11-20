RULES = [
    ("body_bend", "max", 5, "body faceted: neighbour faces bend {v:.1f} degrees, 5 at most (Subdivision 2, smooth)"),
    ("wing_tris", "min", 300, "wing {k} has {v:.0f} triangles, 300 at least (12 rows or more)"),
    ("wingspan", "min", 1.0, "wingspan is {v:.2f} times snout to tail tip, 1.0 at least"),
    ("plate_width", "min", 0.25, "widest plate in {k} is {v:.2f} of torso width, 0.25 at least"),
    ("spread", "min", 0.1, "pieces in {k} all one size: spread {v:.2f}, 0.1 at least"),
    ("belly", "min", 1.1, "belly only {v:.2f} times as light as the back, 1.1 at least"),
    ("saturation", "min", 0.25, "hide colour grey: saturation {v:.2f}, 0.25 at least"),
    ("relief", "min", 0.06, "normal map {k} flat: spread {v:.3f}, 0.06 at least (raise Bump distance)"),
    ("horn_curve", "min", 0.08, "horn {k} straight: bends {v:.2f} of its length, 0.08 at least"),
]


def parse_rows(specs):
    rows = {}
    for spec in specs or []:
        name, _, count = spec.rpartition(":")
        if not name or not count.isdigit():
            return None, f"row {spec!r} is not NAME:COUNT"
        rows[name] = int(count)
    return rows, None


def parse_measure(line):
    parts = line.split()
    if len(parts) != 4 or parts[0] != "measure":
        return None
    try:
        return parts[1], parts[2], float(parts[3])
    except ValueError:
        return None


def verdicts(measures, rows):
    refused, kept = [], 0
    for key, item, value in measures:
        if key == "count":
            if value < rows.get(item, 0):
                refused.append(f"{item} has {value:.0f} pieces, the design sheet says {rows[item]}")
            else:
                kept += 1
            continue
        rule = next((r for r in RULES if r[0] == key), None)
        if rule is None:
            continue
        bad = value > rule[2] if rule[1] == "max" else value < rule[2]
        if bad:
            refused.append(rule[3].format(k=item, v=value))
        else:
            kept += 1
    return refused, kept
