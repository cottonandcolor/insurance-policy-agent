import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        // Live Ollama quick mode can take several minutes end-to-end
        timeout: 600_000,
        proxyTimeout: 600_000,
      },
    },
  },
});
