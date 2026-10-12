import * as esbuild from 'esbuild'
import * as fs from 'fs';

const appconfig = JSON.parse(fs.readFileSync('./ievv_buildstatic.appconfig.json', 'utf8'));

if (process.argv.length != 3) {
    throw new Error('Invalid arguments.')
}

const mode = process.argv[2]

const config = {
    entryPoints: ['lib/django_cradmin_all.js'],
    bundle: true,
    outfile: `${appconfig.destinationfolder}/django_cradmin_all.js`,
    loader: { '.js': 'jsx' },
    logLevel: "info",

    // Browsers to target. Use this to get an updated list based on browserlist query:
    //  npm install --no-save browserslist-to-esbuild
    //  node_modules/.bin/browserslist-to-esbuild ">0.2%, not dead"
    // (not using browserslist-to-esbuild directly to keep uneeded dependencies down)
    target: ["chrome109", "edge124", "firefox115", "ios12.2", "opera109", "safari15.6"],
}

if (mode === 'production') {
    config.minify = true;
    config.sourcemap = true;
} else if (mode === 'watch') {
} else if (mode === 'dev') {
} else {
    throw new Error(`Invalid mode: ${mode}`);
}

console.log('Building with esbuild:', config);

if (mode === 'watch') {
    const run = async () => {
        const ctx = await esbuild.context(config);
        await ctx.watch();
    };
    run();
} else {
    await esbuild.build(config)
}