import { dayh, hhmm, hms, last, type Project, type Point } from "./board";

/** Room around the plot: the right margin lets a name sit beside its icon. */
export const L = 30, R = 110, T = 40, B = 24;
const TICK_EVERY = 110, JUMP_W = 30, PIN = 16, ICON_GAP = 26, ICON_STEP = 28, CHAR_W = 7, LABEL_H = 16;

export type Pt = { x: number; y: number; d: Point; p: Project };
type Box = { x: number; y: number; w: number; h: number };
export type End = Pt & {
    ix: number;
    slide: { x1: number; x2: number; dashed: boolean } | null;
    label: { x: number; y: number };
    leader: { y1: number; y2: number } | null;
};

/** Monotone cubic (Fritsch-Carlson): smooth, yet never bulges past a reported value or below the ground. */
export function smooth(ps: { x: number; y: number }[]) {
    const n = ps.length, d: number[] = [], m: number[] = [];
    let s = `M${ps[0].x} ${ps[0].y}`;
    if (n < 2) return s;
    for (let i = 0; i < n - 1; i++) {
        const dx = ps[i + 1].x - ps[i].x;
        d[i] = dx ? (ps[i + 1].y - ps[i].y) / dx : 0;
    }
    m[0] = d[0];
    m[n - 1] = d[n - 2];
    for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
    for (let i = 0; i < n - 1; i++) {
        if (!d[i]) {
            m[i] = m[i + 1] = 0;
            continue;
        }
        const a = m[i] / d[i], b = m[i + 1] / d[i], q = a * a + b * b;
        if (q > 9) {
            const t = 3 / Math.sqrt(q);
            m[i] = t * a * d[i];
            m[i + 1] = t * b * d[i];
        }
    }
    for (let i = 0; i < n - 1; i++) {
        const p0 = ps[i], p1 = ps[i + 1], dx = (p1.x - p0.x) / 3;
        s += dx ? `C${p0.x + dx} ${p0.y + m[i] * dx} ${p1.x - dx} ${p1.y - m[i + 1] * dx} ${p1.x} ${p1.y}` : `L${p1.x} ${p1.y}`;
    }
    return s;
}

/** At most `window` seconds fill the width; older time is reached by dragging. `sl` is the scroll offset. */
export function layout(projects: Project[], window: number, W: number, H: number, sl: number) {
    const w = W - L - R, h = H - T - B;
    if (w < 80 || h < 60) return null;
    const y = (v: number) => T + h - (v * h) / 100;
    const all = projects.flatMap((p) => p.history.map((d) => d.ts));
    const t0 = all.length ? Math.min(...all) : Date.now() / 1000 - 3600;
    const span = Math.max(60, Math.max(t0, ...all) - t0);
    const shown = Math.min(span, window), pxs = w / shown;
    const CW = L + span * pxs + R, x = (ts: number) => L + (ts - t0) * pxs;
    const vl = Math.max(0, Math.min(sl, CW - W)) + L, vr = vl - L + W;
    const atStart = vl - L < 2, atEnd = vr >= CW - 2;

    const fmt = shown < 600 ? hms : span > 20 * 3600 ? dayh : hhmm;
    const seen = new Set<string>(), ticks: { x: number; lab: string; shown: boolean }[] = [];
    for (let px = 0; px <= span * pxs + 0.5; px += TICK_EVERY) {
        const lab = fmt(t0 + px / pxs), tx = L + px, half = lab.length * 3.2;
        if (seen.has(lab)) continue;
        seen.add(lab);
        const room = [vl + (atStart ? 0 : JUMP_W), vr - (atEnd ? 0 : JUMP_W)];
        ticks.push({ x: tx, lab, shown: tx - half >= room[0] && tx + half <= room[1] });
    }

    const pts: Pt[] = [];
    const lines = projects.map((p) => {
        const hs = p.history.map((d) => ({ x: x(d.ts), y: y(d.v), d, p }));
        pts.push(...hs);
        // A dot per report; not the 0 % the server adds under the first one, nor the last, which wears the icon.
        const added = hs.length > 1 && hs[0].d.v === 0 && hs[1].d.ts === hs[0].d.ts && hs[1].d.v !== 0;
        return { p, d: smooth(hs), dots: hs.slice(added ? 1 : 0, -1).map((q) => `M${q.x} ${q.y}h0`).join(""), end: hs[hs.length - 1] };
    });
    const ends = pinIcons(lines.map((l) => l.end), vl, vr);
    placeLabels(ends, vl, vr, H);
    return { CW, h, step: h / 20, y, ticks, lines, ends, pts, vl, vr, atStart, atEnd };
}

/** An icon whose last report is out of view stays pinned to the edge; icons on the same spot step aside. */
function pinIcons(lasts: Pt[], vl: number, vr: number): End[] {
    const ends = lasts.map((e) => ({ ...e, ix: Math.min(Math.max(e.x, vl + PIN), vr - PIN), slide: null, label: { x: 0, y: 0 }, leader: null }) as End);
    ends.sort((a, b) => b.ix - a.ix || a.p.name.localeCompare(b.p.name)).forEach((e, k) => {
        const dir = e.x < vl + PIN ? ICON_STEP : -ICON_STEP;
        while (ends.slice(0, k).some((o) => Math.hypot(o.ix - e.ix, o.y - e.y) < ICON_GAP)) e.ix += dir;
        if (e.ix !== e.x) e.slide = { x1: e.ix, x2: e.x, dashed: e.x < vl || e.x > vr };
    });
    return ends;
}

/** Name above each icon; when taken, right, left, then below; last resort, climb or sink. */
function placeLabels(ends: End[], vl: number, vr: number, H: number) {
    const placed: Box[] = ends.map((e) => ({ x: e.ix - 14, y: e.y - 14, w: 28, h: 28 }));
    const hits = (lx: number, ly: number, lw: number, lh: number) =>
        placed.some((b) => lx < b.x + b.w + 2 && lx + lw + 2 > b.x && ly < b.y + b.h + 2 && ly + lh + 2 > b.y);
    const fit = (lx: number, lw: number) => Math.min(Math.max(lx, vl + 2), vr - lw - 2);
    [...ends].sort((a, b) => a.y - b.y || a.p.name.localeCompare(b.p.name)).forEach((e) => {
        const lw = e.p.name.length * CHAR_W + 6, lh = LABEL_H;
        const spots = [[e.ix - lw / 2, e.y - 18 - lh], [e.ix + 18, e.y - lh / 2], [e.ix - 18 - lw, e.y - lh / 2], [e.ix - lw / 2, e.y + 18]]
            .map(([a, b]) => [fit(a, lw), b])
            .filter(([, b]) => b >= 2 && b + lh <= H - 2);
        let [lx, ly] = spots.find(([a, b]) => !hits(a, b, lw, lh)) ?? spots[0] ?? [fit(e.ix - lw / 2, lw), 2];
        const dy = ly < e.y ? -(lh + 2) : lh + 2;
        while (hits(lx, ly, lw, lh) && ly + dy >= 2 && ly + dy + lh <= H - 2) ly += dy;
        placed.push({ x: lx, y: ly, w: lw, h: lh });
        e.leader = ly + lh < e.y - 24 ? { y1: ly + lh, y2: e.y - 13 } : null;
        e.label = { x: lx + lw / 2, y: ly + 12 };
    });
}

/** The legend's line under a finished project, else its current step. */
export const stepText = (p: Project) => (last(p).v >= 100 ? "fini à " + hhmm(last(p).ts) : p.step || "");
