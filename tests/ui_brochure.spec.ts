import { test } from '@playwright/test';

// Manual verification scaffold to ensure the brochure quick action behaves as expected.
// Execute locally with the backend intelligence service streaming PROPERTY_BROCHURE events.

test.describe('Dashboard brochure quick action', () => {
  test('preview modal streams and resolves brochure content (manual)', async () => {
    test.skip(true, 'Manual verification until SSE fixtures are available in CI');

    // Steps:
    // 1. Start the backend with seeded listings and the intelligence pipeline running.
    // 2. Launch the frontend via `npm run dev` and open `http://localhost:5173/`.
    // 3. Click the "Generate Brochure" quick action in the dashboard carousel.
    // 4. Confirm the modal progress tracker advances: init -> property lookup -> prompt build -> generating -> formatting -> completed.
    // 5. Ensure the preview lists the chosen listing title, price, highlights, and description.
    // 6. Wait for automatic navigation to `/content/:id` and verify the brochure detail layout exposes print/download controls.
  });
});
