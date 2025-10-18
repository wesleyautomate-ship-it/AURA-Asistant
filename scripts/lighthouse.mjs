#!/usr/bin/env node

import { execFile } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const target = process.argv[2] || 'http://localhost:4173';
const outputDir = resolve(__dirname, '../test-artifacts/lighthouse');

function runLighthouse(url) {
  return new Promise((resolvePromise, rejectPromise) => {
    const args = [
      url,
      '--chrome-flags="--headless"',
      `--output=json`,
      `--output-path=${outputDir}/lighthouse-report.json`,
      '--preset=desktop',
    ];

    const child = execFile('npx', ['lighthouse', ...args], { shell: true }, (error, stdout, stderr) => {
      if (error) {
        rejectPromise(new Error(`Lighthouse failed: ${stderr || error.message}`));
        return;
      }
      resolvePromise(stdout);
    });

    child.stdout?.pipe(process.stdout);
    child.stderr?.pipe(process.stderr);
  });
}

runLighthouse(target)
  .then(() => {
    console.log(`Lighthouse report generated at ${outputDir}/lighthouse-report.json`);
  })
  .catch((err) => {
    console.error(err.message);
    process.exitCode = 1;
  });
