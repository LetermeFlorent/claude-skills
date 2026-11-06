import { color, type Project } from "./board";

/** Plot symbols drawn on a 24x24 grid; the server picks one per project. */
const ICONS: Record<string, string> = {
    star: "M12 2l2.9 6.6 7.1.6-5.4 4.7 1.6 7L12 17.3 5.8 20.9l1.6-7L2 9.2l7.1-.6z",
    bolt: "M13 2L4 14h6l-1 8 9-12h-6z",
    heart: "M12 21s-7.5-4.6-9.5-9C1 8.5 3.5 5 7 5c2 0 3.5 1 5 3 1.5-2 3-3 5-3 3.5 0 6 3.5 4.5 7-2 4.4-9.5 9-9.5 9z",
    moon: "M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z",
    diamond: "M12 2l8 10-8 10-8-10z",
    flame: "M12 2c1 4 6 6 6 12a6 6 0 0 1-12 0c0-3 2-5 3-7 0 2 1 3 2 3 0-3-1-5 1-8z",
    crown: "M3 18h18l-1-10-5 4-3-7-3 7-5-4z",
    leaf: "M5 20C4 10 10 4 20 4c0 10-6 16-15 16z",
};

/** The project's symbol centred on 0,0 with radius r, in its color, ringed by the background. */
export function Glyph({ p, r }: { p: Project; r: number }) {
    const k = r / 12;
    return (
        <path
            d={ICONS[p.icon] ?? ICONS.star}
            fill={color(p)}
            stroke="var(--bg)"
            strokeWidth={3 / k}
            strokeLinejoin="round"
            paintOrder="stroke"
            transform={`translate(${-r} ${-r}) scale(${k})`}
        />
    );
}

export function GlyphIcon({ p, className = "size-5" }: { p: Project; className?: string }) {
    return (
        <svg viewBox="-16 -16 32 32" className={`flex-none ${className}`} aria-hidden="true">
            <Glyph p={p} r={14} />
        </svg>
    );
}
