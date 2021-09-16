import svelte from 'rollup-plugin-svelte';
import commonjs from '@rollup/plugin-commonjs';
import resolve from '@rollup/plugin-node-resolve';
import { terser } from 'rollup-plugin-terser';
import css from 'rollup-plugin-css-only';

export default {

	input: "src/entries/{{proc_slug}}.js",
	output: {
		sourcemap: false,
		format: 'iife',
		name: 'app',
		file: "public/build/{{proc_slug}}.js"
	},
	plugins: [
		svelte({
			compilerOptions: {
				dev: false
			}
		}),
		// we'll extract any component CSS out into
		// a separate file - better for performance
		css({ output: "{{proc_slug}}.css" }),

		// If you have external dependencies installed from
		// npm, you'll most likely need these plugins. In
		// some cases you'll need additional configuration -
		// consult the documentation for details:
		// https://github.com/rollup/plugins/tree/master/packages/commonjs
		resolve({
			browser: true,
			dedupe: ['svelte']
		}),
		commonjs(),

		terser()
	],
	watch: {
		clearScreen: false
	}
};
