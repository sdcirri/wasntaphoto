import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({command, mode, ssrBuild}) => {
	const ret = {
		plugins: [vue()],
		resolve: {
			alias: {
				'@': fileURLToPath(new URL('./src', import.meta.url))
			}
		},
		test: {
			environment: 'jsdom',
			globals: true,
			include: ['tests/**/*.{test,spec}.js'],
			coverage: {
				provider: 'v8',
				reporter: ['text', 'html', 'lcov'],
				include: ['src/**/*.{js,vue}'],
				exclude: ['src/main.js', 'src/**/*.spec.js']
			}
		}
	};
	ret.define = {
		// Do not modify this constant, it is used in the evaluation.
		"__API_URL__": JSON.stringify("http://localhost:8000"),
	};
	return ret;
})
