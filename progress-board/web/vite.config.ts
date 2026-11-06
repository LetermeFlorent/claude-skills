import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

const board = "http://127.0.0.1:8790";

export default defineConfig({
    base: "./",
    plugins: [react(), tailwindcss()],
    resolve: { alias: { "@": path.resolve(import.meta.dirname, "./src") } },
    build: { outDir: "../site", emptyOutDir: true, chunkSizeWarningLimit: 1000 },
    server: { proxy: { "/events": board, "/_cfg": board, "/_del": board, "/_clear": board } },
});
