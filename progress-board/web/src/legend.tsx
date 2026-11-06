import { useMemo, type CSSProperties, type ReactNode } from "react";
import AnimatedList from "@/components/reactbits/animated-list";
import CountUp from "@/components/reactbits/count-up";
import { byHeight, last, type Project } from "@/lib/board";
import { GlyphIcon } from "@/lib/glyphs";
import { stepText } from "@/lib/layout";

/** React Bits list colors taken from the page: no tiles, a thin ring on the item under the mouse. */
export const LIST_STYLE = {
    "--al-tile": "transparent",
    "--al-tile-shadow": "none",
    "--al-tile-edge": "transparent",
    "--al-tile-highlight": "transparent",
    "--al-ink": "var(--text)",
    "--al-muted": "var(--muted)",
    "--al-ring": "var(--grid-strong)",
    "--al-ring-fill": "transparent",
    "--al-hover": "none",
    "--al-press": "none",
    "--al-active": "none",
    "--al-thumb": "var(--grid-strong)",
    "--al-accent": "var(--muted)",
} as CSSProperties;

type ListProps = { projects: Project[]; maxHeight: string | number; row: (p: Project) => ReactNode; onHover?: (p: Project | null) => void; onPick?: (p: Project) => void };

/** A React Bits AnimatedList over projects, highest line first. */
export function ProjectList({ projects, maxHeight, row, onHover, onPick }: ListProps) {
    const order = useMemo(() => byHeight(projects), [projects]);
    const items = useMemo(() => order.map((p) => ({ id: p.name, title: p.name })), [order]);
    return (
        <AnimatedList
            items={items}
            frame={false}
            className="al-list"
            animation="slide"
            width="100%"
            maxHeight={maxHeight}
            radius={10}
            gap={2}
            style={LIST_STYLE}
            onItemHover={onHover && ((i) => onHover(order[i] ?? null))}
            onItemSelect={onPick && ((_, i) => onPick(order[i]))}
            renderItem={(_, i) => row(order[i])}
        />
    );
}

/** Legend row: symbol, name, step (or end time), percent counting up to its new value. */
export function LegendRow({ p, dim }: { p: Project; dim: boolean }) {
    const v = last(p).v, done = v >= 100;
    return (
        <div className={`flex min-w-0 flex-1 items-center gap-3 transition-opacity duration-200 ${dim ? "opacity-35" : ""}`}>
            <GlyphIcon p={p} className={done ? "size-5 opacity-55" : "size-5"} />
            <div className="min-w-0 flex-1">
                <div className={`truncate ${done ? "text-[color:var(--muted)]" : "font-semibold"}`} title={p.name}>
                    {p.name}
                </div>
                <div className="truncate text-[12.5px] text-[color:var(--muted)]">{stepText(p) || " "}</div>
            </div>
            {!done && (
                <span className="text-2xl leading-none font-semibold">
                    <CountUp to={v} duration={0.8} trigger="load" />
                    <small className="ml-px text-[13px] font-normal text-[color:var(--muted)]">%</small>
                </span>
            )}
        </div>
    );
}
