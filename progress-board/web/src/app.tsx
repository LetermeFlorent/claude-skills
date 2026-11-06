import { useEffect, useState } from "react";
import { Chart } from "@/chart";
import { LegendRow, ProjectList } from "@/legend";
import { useBoard } from "@/lib/board";
import { applyTheme, Settings } from "@/settings";

export function App() {
    const { projects, cfg, ready } = useBoard();
    const [picked, setPicked] = useState<string | null>(null);
    const [lit, setLit] = useState<string | null>(null);
    const focus = projects.some((p) => p.name === picked) ? picked : null;
    // A click on a line or a legend row brings that project into view and fades the others; a second click undoes it.
    const pick = (name: string | null) => setPicked((f) => (name === null || f === name ? null : name));
    const hidden = !ready || !projects.length ? "pointer-events-none opacity-0" : "";

    useEffect(() => {
        const system = matchMedia("(prefers-color-scheme: dark)");
        system.addEventListener("change", applyTheme);
        return () => system.removeEventListener("change", applyTheme);
    }, []);

    return (
        <div className="grid h-dvh grid-cols-[minmax(0,1fr)_272px] gap-8 px-10 pt-8 pb-6 max-[760px]:grid-cols-[minmax(0,1fr)] max-[760px]:grid-rows-[minmax(0,1fr)_auto] max-[760px]:gap-3 max-[760px]:px-3 max-[760px]:pb-2">
            <div className={`grid min-h-0 ${hidden}`}>
                <Chart projects={projects} window={cfg.window} lit={lit} focus={focus} onPick={pick} />
            </div>
            <aside className={`min-h-0 pt-10 max-[760px]:pt-0 ${hidden}`}>
                <ProjectList
                    projects={projects}
                    maxHeight="var(--list-h)"
                    onHover={(p) => setLit(p?.name ?? null)}
                    onPick={(p) => pick(p.name)}
                    row={(p) => <LegendRow p={p} dim={!!focus && focus !== p.name} />}
                />
            </aside>
            {ready && !projects.length && (
                <div className="pointer-events-none fixed inset-0 grid place-items-center text-[15px] text-[color:var(--muted)]">Aucun projet</div>
            )}
            <Settings projects={projects} cfg={cfg} />
        </div>
    );
}
