import { useLayoutEffect, useMemo, useRef, useState, type PointerEvent } from "react";
import { ChevronLeftDouble, ChevronRightDouble } from "@untitledui/icons";
import { ButtonUtility } from "@/components/base/buttons/button-utility";
import { color, hhmm, type Project } from "@/lib/board";
import { Glyph } from "@/lib/glyphs";
import { L, layout, R, T, type Pt } from "@/lib/layout";

const HIT = 40, DRAG_MIN = 4;

type Props = { projects: Project[]; window: number; lit: string | null; focus: string | null; onPick: (name: string | null) => void };

/** One line per project, percent over clock time; drag to move through time, click a line to focus it. */
export function Chart({ projects, window, lit, focus, onPick }: Props) {
    const sc = useRef<HTMLDivElement>(null);
    const [size, setSize] = useState({ W: 0, H: 0 });
    const [sl, setSl] = useState(0);
    const [tip, setTip] = useState<Pt | null>(null);
    const [dragging, setDragging] = useState(false);
    const follow = useRef(true), center = useRef<string | null>(null), fitted = useRef("");
    const drag = useRef<{ x: number; s: number; moved: boolean } | null>(null);
    const lay = useMemo(() => layout(projects, window, size.W, size.H, sl), [projects, window, size, sl]);

    useLayoutEffect(() => {
        const el = sc.current!;
        const ro = new ResizeObserver(() => setSize({ W: el.clientWidth, H: el.clientHeight }));
        ro.observe(el);
        return () => ro.disconnect();
    }, []);
    useLayoutEffect(() => {
        center.current = focus;
    }, [focus]);
    // When the chart grows it stays on the newest time, unless moved back; a new focus brings its project to the middle.
    useLayoutEffect(() => {
        const el = sc.current!;
        if (!lay) return;
        const c = center.current && lay.ends.find((e) => e.p.name === center.current);
        const key = `${lay.CW}x${size.W}`;
        center.current = null;
        if (c) el.scrollLeft = c.x - size.W / 2;
        else if (follow.current && key !== fitted.current) el.scrollLeft = lay.CW - size.W;
        fitted.current = key;
        if (el.scrollLeft !== sl) setSl(el.scrollLeft);
    });

    const nearest = (e: PointerEvent) => {
        if (!lay?.pts.length) return null;
        const r = sc.current!.getBoundingClientRect(), mx = e.clientX - r.left + sl, my = e.clientY - r.top;
        const dist = (q: Pt) => Math.hypot(q.x - mx, q.y - my);
        const q = lay.pts.reduce((a, b) => (dist(b) < dist(a) ? b : a));
        return dist(q) <= HIT ? q : null;
    };
    const down = (e: PointerEvent) => {
        if (e.button) return;
        drag.current = { x: e.clientX, s: sl, moved: false };
        sc.current!.setPointerCapture(e.pointerId);
    };
    const move = (e: PointerEvent) => {
        const d = drag.current;
        if (!d) return setTip(nearest(e));
        const dx = e.clientX - d.x;
        if (!d.moved && Math.abs(dx) < DRAG_MIN) return;
        if (!d.moved) {
            d.moved = true;
            setDragging(true);
            setTip(null);
        }
        sc.current!.scrollLeft = d.s - dx;
    };
    const up = (e: PointerEvent) => {
        if (drag.current && !drag.current.moved) {
            const q = nearest(e);
            onPick(q ? q.p.name : null);
        }
        drag.current = null;
        setDragging(false);
    };
    const scrolled = () => {
        const el = sc.current!;
        follow.current = el.scrollLeft + el.clientWidth >= el.scrollWidth - 4;
        setSl(el.scrollLeft);
    };
    const glide = (left: number) =>
        sc.current!.scrollTo({ left, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });

    const lead = lit ?? focus;
    const dim = (p: Project) => (lead && lead !== p.name ? "dim" : "");
    const fade = "transition-opacity duration-200";
    const { W, H } = size, h = lay?.h ?? 0, P = (lay?.step ?? 0) * 5;
    const cursor = dragging ? "cursor-grabbing" : tip ? "cursor-pointer" : "cursor-grab";

    return (
        <div className="relative min-h-0">
            <div
                ref={sc}
                className={`absolute inset-0 touch-none overflow-hidden select-none ${cursor}`}
                onPointerDown={down}
                onPointerMove={move}
                onPointerUp={up}
                onPointerLeave={() => drag.current || setTip(null)}
                onScroll={scrolled}
            >
                {lay && (
                    <svg className="block h-full" style={{ width: lay.CW }} role="img" aria-label="Avancement de chaque projet dans le temps">
                        <defs>
                            <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                <path d="M0 0L10 5L0 10z" fill="var(--axis)" />
                            </marker>
                            <pattern id="paper" patternUnits="userSpaceOnUse" x={L} y={T} width={P} height={P}>
                                {[0, 1, 2, 3, 4].map((k) => (
                                    <g key={k} stroke={k ? "var(--grid)" : "var(--grid-strong)"}>
                                        <line x1={k * lay.step} x2={k * lay.step} y2={P} />
                                        <line y1={k * lay.step} y2={k * lay.step} x2={P} />
                                    </g>
                                ))}
                            </pattern>
                        </defs>
                        <rect x={L} y={T} width={lay.CW - L - R} height={h} fill="url(#paper)" />
                        <g fontSize="11.5" fill="var(--muted)" textAnchor="middle">
                            {lay.ticks.map((t) => (
                                <text key={t.x} x={t.x} y={T + h + 17} visibility={t.shown ? "visible" : "hidden"}>
                                    {t.lab}
                                </text>
                            ))}
                        </g>
                        <line x1={L} y1={T + h} x2={lay.CW - R + 12} y2={T + h} stroke="var(--axis)" strokeWidth="1.2" markerEnd="url(#arr)" />
                        <line x1={lay.vl} y1={T + h} x2={lay.vl} y2={T - 12} stroke="var(--axis)" strokeWidth="1.2" markerEnd="url(#arr)" />
                        <g fill="none" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round">
                            {lay.lines.map((l) => (
                                <path key={l.p.name} d={l.d} stroke={color(l.p)} className={`${fade} ${dim(l.p)}`} />
                            ))}
                        </g>
                        <g fill="none" strokeWidth="6" strokeLinecap="round">
                            {lay.lines.map((l) => (
                                <path key={l.p.name} d={l.dots} stroke={color(l.p)} className={`${fade} ${dim(l.p)}`} />
                            ))}
                        </g>
                        {lay.ends.map((e) => (
                            <g key={e.p.name} className={`${fade} ${dim(e.p)}`}>
                                {e.slide && (
                                    <line x1={e.slide.x1} x2={e.slide.x2} y1={e.y} y2={e.y} stroke={color(e.p)} strokeWidth="2" strokeDasharray={e.slide.dashed ? "3 4" : undefined} />
                                )}
                                {e.leader && <line x1={e.ix} x2={e.ix} y1={e.leader.y1} y2={e.leader.y2} stroke="var(--axis)" strokeDasharray="2 2" />}
                            </g>
                        ))}
                        <g fontSize="13" fontWeight="600" fill="var(--text)" stroke="var(--bg)" strokeWidth="4" paintOrder="stroke" textAnchor="middle">
                            {lay.ends.map((e) => (
                                <text key={e.p.name} x={e.label.x} y={e.label.y} className={`${fade} ${dim(e.p)}`}>
                                    {e.p.name}
                                </text>
                            ))}
                        </g>
                        {lay.ends.map((e) => (
                            <g key={e.p.name} transform={`translate(${e.ix} ${e.y})`} className={`${fade} ${dim(e.p)}`}>
                                <Glyph p={e.p} r={12} />
                            </g>
                        ))}
                        {tip && <circle cx={tip.x} cy={tip.y} r="4.5" fill="var(--bg)" stroke={color(tip.p)} strokeWidth="2" />}
                    </svg>
                )}
            </div>
            {lay && (
                <svg className="pointer-events-none absolute top-0 left-0 h-full overflow-visible" width={L} aria-hidden="true">
                    <rect width={L - 1} height={H} fill="var(--bg)" />
                    {[0, 50, 100].map((v) => (
                        <text key={v} x={L - 8} y={lay.y(v) + 4} textAnchor="end" fontSize="11.5" fill="var(--muted)">
                            {v}
                        </text>
                    ))}
                </svg>
            )}
            {lay && !lay.atStart && (
                <ButtonUtility className="absolute bg-primary" style={{ left: L + 2, top: T + lay.h + 4 }} size="xs" color="secondary" icon={ChevronLeftDouble} tooltip="Aller au début" onPress={() => glide(0)} />
            )}
            {lay && !lay.atEnd && (
                <ButtonUtility className="absolute right-0 bg-primary" style={{ top: T + lay.h + 4 }} size="xs" color="secondary" icon={ChevronRightDouble} tooltip="Aller à maintenant" onPress={() => glide(lay.CW)} />
            )}
            {tip && <Tip q={tip} x={tip.x - sl} W={W} />}
        </div>
    );
}

/** The value under the mouse, in the look of the Untitled UI tooltip. */
function Tip({ q, x, W }: { q: Pt; x: number; W: number }) {
    const side = x > W / 2 ? { right: W - x + 12 } : { left: x + 12 };
    const high = q.y > 70;
    return (
        <div
            className={`pointer-events-none absolute z-10 flex flex-col gap-0.5 rounded-lg bg-primary-solid px-3 py-2 whitespace-nowrap shadow-lg ${high ? "-translate-y-full" : ""}`}
            style={{ ...side, top: high ? q.y - 12 : q.y + 12 }}
        >
            <span className="flex items-baseline gap-3 text-xs font-semibold text-white">
                {q.p.name}
                <span className="ml-auto">{q.d.v} %</span>
            </span>
            <span className="text-xs font-medium text-tooltip-supporting-text">
                {hhmm(q.d.ts)}
                {q.d.s ? ` · ${q.d.s}` : ""}
            </span>
        </div>
    );
}
