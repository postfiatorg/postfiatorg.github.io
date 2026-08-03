const { test, expect } = require('@playwright/test');

const deckUrl = process.env.DECK_URL || 'http://127.0.0.1:1313/research/post-fiat-no-limit-holdings/';

test('renders fourteen scenes and supports keyboard navigation', async ({ page }) => {
  const runtimeErrors = [];
  page.on('pageerror', (error) => runtimeErrors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error') runtimeErrors.push(message.text());
  });

  await page.goto(deckUrl, { waitUntil: 'networkidle' });

  await expect(page.locator('.slide')).toHaveCount(14);
  await expect(page.locator('#slide-1')).toHaveClass(/is-active/);
  await expect(page.locator('#currentSlide')).toHaveText('01');
  await expect(page.locator('.world__layer[data-world="network"]')).toHaveClass(/is-active/);

  await page.keyboard.press('ArrowRight');
  await expect(page.locator('#currentSlide')).toHaveText('02');
  await expect(page.locator('#slide-2')).toHaveClass(/is-active/);

  await page.locator('.deck-dots button').nth(13).click();
  await expect(page.locator('#currentSlide')).toHaveText('14');
  await expect(page.locator('#slide-14 .deal-doors article')).toHaveCount(2);
  await expect(page.locator('#slide-14')).toContainText('TVL investment');
  await expect(page.locator('#slide-14')).toContainText('Post Fiat token sale');

  await page.locator('#sourcesButton').click();
  await expect(page.locator('#sourceDialog')).toBeVisible();
  await expect(page.locator('[data-source-slide="14"]')).toBeVisible();
  await page.locator('#sourceClose').click();

  const imagesLoaded = await page.locator('img').evaluateAll((images) =>
    images.every((image) => image.complete && image.naturalWidth > 0)
  );
  expect(imagesLoaded).toBe(true);
  expect(runtimeErrors).toEqual([]);
});

test('keeps the private FX scene usable on a phone viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${deckUrl}#slide-5`, { waitUntil: 'networkidle' });

  await expect(page.locator('#currentSlide')).toHaveText('05');
  await expect(page.locator('#slide-5')).toContainText('18/18');
  await expect(page.locator('#slide-5')).toContainText('10×');
  await expect(page.locator('#slide-5 .product-shot img')).toBeVisible();

  const viewportOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > window.innerWidth
  );
  expect(viewportOverflow).toBe(false);
});

test('honors reduced motion', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(deckUrl, { waitUntil: 'networkidle' });
  await page.mouse.move(1300, 800);

  const transform = await page.locator('.world__layer.is-active').evaluate((element) =>
    getComputedStyle(element).transform
  );
  expect(transform === 'none' || transform.includes('matrix')).toBe(true);
  await expect(page.locator('.slide')).toHaveCount(14);
});
