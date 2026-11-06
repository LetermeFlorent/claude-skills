import { useEffect, useState } from "react";

export type Point = { ts: number; v: number; s?: string };
export type Project = { name: string; slot: number; icon: string; step?: string; history: Point[] };
export type Cfg = { window: number; done: number; idle: number };
type Message = { projects?: Project[]; cfg?: Cfg; v?: number; p?: Project };

export const last = (p: Project) => p.history[p.history.length - 1];
export const color = (p: Project) => `var(--s${(p.slot % 8) + 1})`;
export const post = (path: string) => fetch(path, { method: "POST" });
export const hhmm = (ts: number) => new Date(ts * 1000).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
export const hms = (ts: number) => new Date(ts * 1000).toLocaleTimeString("fr-FR");
export const dayh = (ts: number) =>
    new Date(ts * 1000).toLocaleString("fr-FR", { weekday: "short", hour: "2-digit", minute: "2-digit" });

/** Legend order: the chart from top to bottom. */
export const byHeight = (ps: Project[]) => [...ps].sort((a, b) => last(b).v - last(a).v || last(b).ts - last(a).ts);

/** Full state ({projects, cfg, v}) on connect, then one changed project ({p}); EventSource reconnects by itself. */
export function useBoard() {
    const [board, setBoard] = useState({ projects: [] as Project[], cfg: { window: 3600, done: 3600, idle: 3 * 86400 }, ready: false });
    useEffect(() => {
        let version: number | undefined;
        const events = new EventSource("events");
        events.onmessage = (e) => {
            const msg: Message = JSON.parse(e.data);
            if (msg.v) {
                if (version && msg.v !== version) return location.reload();
                version = msg.v;
            }
            setBoard((b) => {
                const all = msg.projects ?? [...b.projects];
                const p = msg.p;
                if (p) {
                    const i = all.findIndex((q) => q.name === p.name);
                    if (i < 0) all.push(p);
                    else all[i] = p;
                }
                return { projects: all.filter((q) => q.history?.length), cfg: msg.cfg ?? b.cfg, ready: true };
            });
        };
        return () => events.close();
    }, []);
    return board;
}
