import type { KnipConfig } from 'knip';

const config: KnipConfig = {
    // Entry point aplikasi Vue + Vite biasanya di sini
    entry: ['index.html', 'src/main.ts', 'src/main.js'],

    // Lokasi file source code
    project: ['src/**/*.{ts,js,vue}'],

    // Abaikan file definisi tipe otomatis (jika pakai auto-import)
    ignore: ['components.d.ts', 'auto-imports.d.ts'],
};

export default config;