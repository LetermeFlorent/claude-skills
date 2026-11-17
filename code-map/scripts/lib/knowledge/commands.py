from common import refuse
from knowledge import notes
from knowledge.recall import files_of


def drop_note(root, number):
    data = notes.load(root)
    if not notes.drop(data, number):
        refuse([f"no note #{number}"])
    notes.save(root, data)
    return [f"dropped note #{number}"]


def note(graph, root, args):
    if args.drop is not None:
        return drop_note(root, args.drop)
    text = (args.fact or "").strip()
    if not text:
        refuse(["give the fact to remember, or --drop <id>"])
    hashes = {}
    for target in args.about:
        paths = files_of(graph, target)
        if not paths:
            refuse([f"--about {target}: no symbol or file of that name"])
        hashes.update({path: notes.file_hash(root, path) for path in paths})
    data = notes.load(root)
    notes.add(data, text, hashes, args.about)
    notes.save(root, data)
    return ["saved " + notes.line(data["notes"][-1], False)]


def listing(root, stale_only):
    items = notes.load(root)["notes"]
    flagged = [(n, notes.is_stale(root, n)) for n in items]
    lines = [notes.line(n, stale) for n, stale in flagged if stale or not stale_only]
    stale_count = sum(stale for _, stale in flagged)
    return lines + [f"{len(items)} notes, {stale_count} stale"]
