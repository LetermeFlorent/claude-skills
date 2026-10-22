from itertools import combinations

MAX_HEAVY = 2


def nested(first, second):
    return first == second or first.startswith(second + "/") or second.startswith(first + "/")


def shared_writes(first, second):
    return [a if len(a) >= len(b) else b for a in first["writes"] for b in second["writes"] if nested(a, b)]


def pair_problems(first, second):
    names = f"{first['name']} and {second['name']}"
    problems = []
    for path in shared_writes(first, second):
        problems.append(f"{names} both write {path}")
    for kind, field in (("port", "ports"), ("MCP instance", "instances")):
        for value in sorted(set(first[field]) & set(second[field])):
            problems.append(f"{names} both use {kind} {value}")
    if first["commits"] and second["commits"] and first["tree"] == second["tree"]:
        problems.append(f"{names} both commit in {first['tree']}: one git index")
    return problems


def single_problems(agent):
    problems = []
    if agent["rebuild"]:
        problems.append(f"{agent['name']} rebuilds an image or recreates a container: the main session does it once")
    return problems


def check_plan(agents):
    problems = []
    for agent in agents:
        problems += single_problems(agent)
    for first, second in combinations(agents, 2):
        problems += pair_problems(first, second)
    heavy = [agent["name"] for agent in agents if agent["heavy"]]
    if len(heavy) > MAX_HEAVY:
        problems.append(f"{len(heavy)} heavy agents ({', '.join(heavy)}): at most {MAX_HEAVY} at a time")
    return problems
