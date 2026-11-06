import { useEffect, useState } from "react";
import type { Key } from "react-aria-components";
import { Settings01, Trash01 } from "@untitledui/icons";
import { Dialog, DialogTrigger, Modal, ModalOverlay } from "@/components/application/modals/modal";
import { Tabs } from "@/components/application/tabs/tabs";
import { ButtonGroup, ButtonGroupItem } from "@/components/base/button-group/button-group";
import { Button } from "@/components/base/buttons/button";
import { ButtonUtility } from "@/components/base/buttons/button-utility";
import { InputNumber } from "@/components/base/input/input-number";
import { last, post, type Cfg, type Project } from "@/lib/board";
import { GlyphIcon } from "@/lib/glyphs";
import { ProjectList } from "@/legend";

const FIELDS = [
    { key: "window", label: "Temps visible sur la largeur", unit: 60, suffix: "min", max: 1440 },
    { key: "done", label: "Projet fini retiré après", unit: 60, suffix: "min", max: 10080 },
    { key: "idle", label: "Projet sans nouvelle retiré après", unit: 86400, suffix: "j", max: 60 },
] as const;
const CONFIRM_FOR = 4000, PANEL_H = "min-h-[244px]";

/** Dark follows the system unless the settings force a theme; the choice stays in this browser. */
export function applyTheme() {
    const pick = localStorage.getItem("theme");
    const dark = pick ? pick === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.classList.toggle("dark-mode", dark);
}

/** The settings button and its window. Durations live on the server (it removes projects). */
export function Settings({ projects, cfg }: { projects: Project[]; cfg: Cfg }) {
    return (
        <DialogTrigger>
            <Button size="sm" color="tertiary" iconLeading={Settings01} className="fixed top-2 right-3 z-20">
                Réglages
            </Button>
            <ModalOverlay isDismissable className="bg-overlay/25 backdrop-blur-[2px]">
                <Modal className="max-w-[440px]">
                    <Dialog aria-label="Réglages">{({ close }) => <Panel projects={projects} cfg={cfg} close={close} />}</Dialog>
                </Modal>
            </ModalOverlay>
        </DialogTrigger>
    );
}

function Panel({ projects, cfg, close }: { projects: Project[]; cfg: Cfg; close: () => void }) {
    const [tab, setTab] = useState<Key>("cfg");
    return (
        <div className="flex flex-col gap-5 p-6">
            <Tabs selectedKey={tab} onSelectionChange={setTab}>
                <Tabs.List type="underline" size="sm">
                    <Tabs.Item id="cfg" label="Réglages" />
                    <Tabs.Item id="proj" label="Projets" badge={projects.length || undefined} />
                </Tabs.List>
                <Tabs.Panel id="cfg" className={`${PANEL_H} pt-5`}>
                    <Durations cfg={cfg} />
                </Tabs.Panel>
                <Tabs.Panel id="proj" className={`${PANEL_H} pt-3`}>
                    <Projects projects={projects} />
                </Tabs.Panel>
            </Tabs>
            <div className="flex items-center gap-3">
                {tab === "proj" && <ClearAll disabled={!projects.length} />}
                <Button size="sm" color="secondary" className="ml-auto" onPress={close}>
                    Fermer
                </Button>
            </div>
        </div>
    );
}

/** Shows the values the server kept (it caps them); a field remounts when the server answers. */
function Durations({ cfg }: { cfg: Cfg }) {
    const [theme, setTheme] = useState(localStorage.getItem("theme") ?? "system");
    const choose = (keys: Set<Key>) => {
        const v = String([...keys][0]);
        if (v === "system") localStorage.removeItem("theme");
        else localStorage.setItem("theme", v);
        setTheme(v);
        applyTheme();
    };
    return (
        <div className="flex flex-col gap-3">
            {FIELDS.map((f) => (
                <div key={f.key} className="flex items-center gap-3">
                    <span className="flex-1 text-sm text-secondary">{f.label}</span>
                    <InputNumber
                        key={cfg[f.key]}
                        aria-label={f.label}
                        size="sm"
                        className="w-28"
                        minValue={1}
                        maxValue={f.max}
                        defaultValue={Math.round(cfg[f.key] / f.unit)}
                        onChange={(n) => n >= 1 && post(`/_cfg?${f.key}=${Math.round(n) * f.unit}`)}
                    />
                    <span className="w-7 text-sm text-tertiary">{f.suffix}</span>
                </div>
            ))}
            <div className="mt-3 flex items-center gap-3 border-t border-secondary pt-5">
                <span className="flex-1 text-sm text-secondary">Thème</span>
                <ButtonGroup size="sm" aria-label="Thème" selectedKeys={[theme]} disallowEmptySelection onSelectionChange={choose}>
                    <ButtonGroupItem id="system">Système</ButtonGroupItem>
                    <ButtonGroupItem id="light">Clair</ButtonGroupItem>
                    <ButtonGroupItem id="dark">Sombre</ButtonGroupItem>
                </ButtonGroup>
            </div>
        </div>
    );
}

function Projects({ projects }: { projects: Project[] }) {
    if (!projects.length) return <p className="pt-2 text-sm text-tertiary">Aucun projet</p>;
    return (
        <ProjectList
            projects={projects}
            maxHeight={236}
            row={(p) => (
                <div className="flex min-w-0 flex-1 items-center gap-3">
                    <GlyphIcon p={p} className="size-4" />
                    <span className="min-w-0 flex-1 truncate text-sm">{p.name}</span>
                    <span className="text-sm text-tertiary">{last(p).v} %</span>
                    <ButtonUtility size="xs" color="tertiary" icon={Trash01} tooltip="Retirer" aria-label={`Retirer ${p.name}`} onPress={() => post("/_del/" + encodeURIComponent(p.name))} />
                </div>
            )}
        />
    );
}

/** Two presses: the first asks, the second erases; the question goes away by itself. */
function ClearAll({ disabled }: { disabled: boolean }) {
    const [sure, setSure] = useState(false);
    useEffect(() => {
        if (!sure) return;
        const t = setTimeout(() => setSure(false), CONFIRM_FOR);
        return () => clearTimeout(t);
    }, [sure]);
    const press = () => {
        if (sure) post("/_clear");
        setSure(!sure);
    };
    return (
        <Button size="sm" color={sure ? "primary-destructive" : "tertiary-destructive"} isDisabled={disabled} onPress={press}>
            {sure ? "Effacer tous les projets ?" : "Tout effacer"}
        </Button>
    );
}
