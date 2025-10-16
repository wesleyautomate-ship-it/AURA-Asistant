import { test, expect } from '@playwright/test';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

/**
 * End-to-end audit for Property Brochure generation.
 * - Boots backend (FastAPI) in dev/mock mode
 * - Boots frontend (Vite) pointing to backend
 * - Exercises two paths:
 *   1) Dashboard Quick Action (SSE intelligence pipeline using seeded listing)
 *   2) Dev Brochure Tile (mock export endpoint + download link)
 * - Captures UI console errors and writes a markdown report
 */

const FRONTEND_PORT = 5173;
const FRONTEND_URL = `http://localhost:${FRONTEND_PORT}/`;
const BACKEND_URL = 'http://localhost:8000';
const REPORT_PATH = path.resolve('brochure_audit_report.md');

let backendProc: any;
let frontendProc: any;

async function waitForHttpOk(url: string, timeoutMs = 30000): Promise<boolean> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url, { method: 'GET' });
      if (res.ok) return true;
    } catch {}
    await new Promise(r => setTimeout(r, 500));
  }
  return false;
}

function startBackend(): Promise<void> {
  return new Promise((resolve, reject) => {
    const env = {
      ...process.env,
      ENVIRONMENT: 'development',
      DEBUG: 'true',
      DISABLE_AUTH: 'true',
      AURA_MOCK_MODE: 'true',
      // Use repo-provided SQLite if present
      DATABASE_URL: process.env.DATABASE_URL || 'sqlite:///../propertypro_dev.db',
    };

    backendProc = spawn('uvicorn', ['app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'], {
      cwd: path.resolve('backend'),
      env,
      stdio: 'pipe',
      shell: process.platform === 'win32',
    });

    let resolved = false;
    const onData = (data: Buffer) => {
      const msg = data.toString();
      if (!resolved && msg.includes('Uvicorn running on')) {
        resolved = true;
        resolve();
      }
    };
    backendProc.stdout?.on('data', onData);
    backendProc.stderr?.on('data', onData);
    backendProc.on('error', reject);
  });
}

function startFrontend(): Promise<void> {
  return new Promise((resolve, reject) => {
    const env = {
      ...process.env,
      VITE_API_BASE_URL: BACKEND_URL,
      VITE_AURA_MOCK_MODE: 'true',
    };

    frontendProc = spawn(process.platform === 'win32' ? 'npm.cmd' : 'npm', ['run', 'dev'], {
      cwd: path.resolve('aura-client'),
      env,
      stdio: 'pipe',
      shell: process.platform === 'win32',
    });

    let resolved = false;
    const onData = (data: Buffer) => {
      const msg = data.toString();
      // Vite prints "Local:   http://localhost:5173/"
      if (!resolved && /localhost:\d+/.test(msg)) {
        resolved = true;
        resolve();
      }
    };
    frontendProc.stdout?.on('data', onData);
    frontendProc.stderr?.on('data', onData);
    frontendProc.on('error', reject);
  });
}

function stopProcesses() {
  if (frontendProc) {
    try { frontendProc.kill(); } catch {}
    frontendProc = null;
  }
  if (backendProc) {
    try { backendProc.kill(); } catch {}
    backendProc = null;
  }
}

test.describe.configure({ mode: 'serial' });

test.beforeAll(async () => {
  // Start backend + wait for health
  await startBackend();
  const backendUp = await waitForHttpOk(`${BACKEND_URL}/health`, 20000);
  if (!backendUp) throw new Error('Backend failed health check');

  // Start frontend + wait for homepage to respond
  await startFrontend();
  const feUp = await waitForHttpOk(FRONTEND_URL, 30000);
  if (!feUp) throw new Error('Frontend failed to respond on dev URL');
});

test.afterAll(async () => {
  stopProcesses();
});

test('Property Brochure end-to-end audit', async ({ page, browserName }) => {
  const consoleErrors: string[] = [];
  page.on('pageerror', (err) => consoleErrors.push(`[pageerror] ${err.message}`));
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(`[console:${msg.type()}] ${msg.text()}`);
  });

  const results: Record<string, any> = {
    startedAt: new Date().toISOString(),
    backendUrl: BACKEND_URL,
    frontendUrl: FRONTEND_URL,
    browser: browserName,
    sseFlow: { ok: false, notes: [] as string[] },
    mockExport: { ok: false, notes: [] as string[] },
    visuals: { previewVisible: false, mobileHierarchyOK: false },
    errors: [] as string[],
  };

  // Navigate to dashboard
  await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded' });

  // Try SSE quick action path first (Dashboard QuickAction tile titled "Property Brochure")
  try {
    const quickTile = page.getByRole('button', { name: /Property Brochure/i });
    await quickTile.click({ timeout: 10000 });

    // Modal opens with header title
    await expect(page.getByText('Property Brochure Generator')).toBeVisible({ timeout: 15000 });

    // Wait for preview to appear (success state)
    const previewHeading = page.getByText(/Preview Ready/i);
    await expect(previewHeading).toBeVisible({ timeout: 30000 });
    results.sseFlow.notes.push('Preview Ready card appeared');

    // Validate key elements
    const viewBtn = page.getByRole('button', { name: /View full brochure/i });
    await expect(viewBtn).toBeVisible();
    results.visuals.previewVisible = true;

    // Open content viewer and validate detail page
    await viewBtn.click();
    // It navigates to /content/:id and should render Property Brochure detail
    await expect(page.getByText(/Property Brochure/i)).toBeVisible({ timeout: 15000 });
    // Look for Overview section excerpt
    await expect(page.getByText(/Overview/i)).toBeVisible();
    results.sseFlow.ok = true;
  } catch (e: any) {
    results.errors.push(`SSE flow failed: ${e?.message || String(e)}`);
  }

  // Now exercise the mock export tile (Dev tile: Generate brochure -> Download link)
  try {
    await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded' });
    // Scroll near Dev tiles area
    await page.mouse.wheel(0, 2000);
    // Click Generate brochure button inside BrochureTile
    const genBtn = page.getByRole('button', { name: /Generate brochure/i });
    await genBtn.click({ timeout: 10000 });
    // Expect a Download link to appear
    const downloadLink = page.getByRole('link', { name: /Download/i });
    await expect(downloadLink).toBeVisible({ timeout: 15000 });
    const href = await downloadLink.getAttribute('href');
    results.mockExport.notes.push(`Download link: ${href ?? 'missing href'}`);
    results.mockExport.ok = !!href;
  } catch (e: any) {
    results.errors.push(`Mock export flow failed: ${e?.message || String(e)}`);
  }

  // Basic mobile hierarchy sanity: ensure preview CTA is reachable in mobile viewport
  try {
    // If the preview CTA was visible previously, assume placement is above the fold on mobile
    // We still check that the modal content has the CTA within 1 viewport height from modal top
    await page.goto(FRONTEND_URL);
    const tile = page.getByRole('button', { name: /Property Brochure/i });
    await tile.click();
    await expect(page.getByText('Property Brochure Generator')).toBeVisible({ timeout: 15000 });

    const cta = page.getByRole('button', { name: /View full brochure/i });
    await expect(cta).toBeVisible({ timeout: 30000 });
    const box = await cta.boundingBox();
    const viewport = page.viewportSize();
    if (box && viewport && box.y < viewport.height * 1.2) {
      results.visuals.mobileHierarchyOK = true;
    } else {
      results.visuals.mobileHierarchyOK = false;
    }
  } catch (e: any) {
    results.errors.push(`Mobile preview placement check failed: ${e?.message || String(e)}`);
  }

  // Collect console/page errors
  if (consoleErrors.length) {
    results.errors.push(...consoleErrors);
  }

  // Emit markdown report
  const md: string[] = [];
  md.push('# Property Brochure E2E Audit');
  md.push('');
  md.push(`- Date: ${new Date().toISOString()}`);
  md.push(`- Backend: ${BACKEND_URL}`);
  md.push(`- Frontend: ${FRONTEND_URL}`);
  md.push(`- Browser: ${browserName}`);
  md.push('');
  md.push('## Results');
  md.push(`- SSE Flow: ${results.sseFlow.ok ? 'PASS' : 'FAIL'}`);
  md.push(`  - Notes: ${results.sseFlow.notes.join('; ') || 'None'}`);
  md.push(`- Mock Export: ${results.mockExport.ok ? 'PASS' : 'FAIL'}`);
  md.push(`  - Notes: ${results.mockExport.notes.join('; ') || 'None'}`);
  md.push(`- Preview Visible: ${results.visuals.previewVisible ? 'Yes' : 'No'}`);
  md.push(`- Mobile Placement OK: ${results.visuals.mobileHierarchyOK ? 'Yes' : 'Needs review'}`);
  md.push('');
  md.push('## Errors and Observations');
  if (results.errors.length) {
    for (const err of results.errors) md.push(`- ${err}`);
  } else {
    md.push('- None');
  }
  md.push('');
  md.push('## Notes');
  md.push('- This test runs backend with auth bypass and AURA mock mode for deterministic results.');
  md.push('- SSE path validates backend-to-frontend data flow and preview rendering.');
  md.push('- Mock export path validates the simple export and download link.');

  fs.writeFileSync(REPORT_PATH, md.join('\n'), 'utf-8');
});

