import { defineConfig } from "vite";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";
import https from "https";
import react from "@vitejs/plugin-react";
import { log } from "console";

if (
    process.env.npm_lifecycle_event === "build" &&
    !process.env.CI &&
    !process.env.SHOPIFY_API_KEY
) {
    console.warn(
        "\nBuilding the frontend app without an API key. The frontend build will not run without an API key. Set the SHOPIFY_API_KEY environment variable when running the build command.\n"
    );
}

const proxyOptions = {
    target: `http://127.0.0.1:${process.env.BACKEND_PORT}`,
    changeOrigin: false,
    secure: true,
    ws: false,
};
const host = process.env.HOST
    ? process.env.HOST.replace(/https?:\/\//, "")
    : "localhost";
console.log("ENVS: ", process.env);
let hmrConfig;
if (host === "localhost") {
    hmrConfig = {
        protocol: "ws",
        host: "localhost",
        port: 64999,
        clientPort: 64999,
    };
} else {
    hmrConfig = {
        protocol: "wss",
        host: host,
        port: process.env.FRONTEND_PORT,
        clientPort: 443,
    };
}

// const getPlugins = (mode) => {};

export default defineConfig(({ mode }) => {
    const config = {
        root: dirname(fileURLToPath(import.meta.url)),
        plugins: [react()],
        define: {
            "process.env.SHOPIFY_API_KEY": JSON.stringify(
                process.env.SHOPIFY_API_KEY
            ),
        },
        resolve: {
            preserveSymlinks: true,
        },
        build: {
            outDir: resolve(__dirname, "../static/reactUI"),
            emptyOutDir: true,
            assetsDir: ".",
            manifest: true,
            rollupOptions: {
                output: {
                    entryFileNames: "[name].js",
                    assetFileNames: "[name].[ext]",
                },
            },
        },
        server: {
            host: "localhost",
            // host: host,
            port: process.env.FRONTEND_PORT,
            hmr: hmrConfig,
            proxy: {
                "^/(\\?.*)?$": proxyOptions,
                "^/api(/|(\\?.*)?$)": proxyOptions,
            },
        },
    };
    if (mode === "production") {
        config["base"] = "/static/reactUI/";
    }
    // console.log("Config", config);
    return config;
});
