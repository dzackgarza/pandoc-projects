const esbuild = require('esbuild');

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

/**
 * @type {import('esbuild').Plugin}
 */
const esbuildProblemMatcherPlugin = {
  name: 'esbuild-problem-matcher',

  setup(build) {
    build.onStart(() => {
      console.log('[watch] build started');
    });
    build.onEnd((result) => {
      result.errors.forEach(({ text, location }) => {
        console.error(`✘ [ERROR] ${text}`);
        console.error(`    ${location.file}:${location.line}:${location.column}:`);
      });
      console.log('[watch] build finished');
    });
  },
};

async function buildExtension(entryPoint, outfile, isWatch) {
  const ctx = await esbuild.context({
    entryPoints: [entryPoint],
    bundle: true,
    format: 'cjs',
    minify: production,
    sourcemap: !production,
    sourcesContent: false,
    platform: 'node',
    outfile: `dist/${outfile}`,
    external: ['vscode'],
    logLevel: 'silent',
    plugins: [
      esbuildProblemMatcherPlugin,
    ],
  });
  
  if (isWatch) {
    await ctx.watch();
  } else {
    await ctx.rebuild();
    await ctx.dispose();
  }
}

async function main() {
  // Build the alpha version
  await buildExtension('src/alpha/alpha.extension.ts', 'alpha/alpha.extension.js');
  await buildExtension('src/alpha/alphaEditor.ts', 'alpha/alphaEditor.js');
  
  // Build the beta version (for reference, not used by default)
  await buildExtension('src/beta/extensionFIX.ts', 'beta/extensionFIX.js');
  await buildExtension('src/beta/extension.ts', 'beta/extension.js');
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});