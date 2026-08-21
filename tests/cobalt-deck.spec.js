const { test, expect } = require("@playwright/test");

const deckUrl =
  process.env.COBALT_DECK_URL ||
  "http://127.0.0.1:1313/research/cobalt-consensus-governance-decision/";

test("renders the complete Cobalt decision and supports navigation", async ({
  page,
}) => {
  const runtimeErrors = [];
  page.on("pageerror", (error) => runtimeErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") runtimeErrors.push(message.text());
  });
  await page.goto(deckUrl, { waitUntil: "networkidle" });
  await expect(page.locator(".slide")).toHaveCount(18);
  await expect(page.locator(".human-blurb")).toHaveCount(18);
  await expect(page.locator("#currentSlide")).toHaveText("01");
  await expect(page.locator("#slide-5")).toContainText("LIVE AUTHORIZATION");
  await expect(page.locator("#slide-8")).toContainText("13 / 13");
  await expect(page.locator("#slide-8")).toContainText("0 / 3");
  await expect(page.locator("#slide-14")).toContainText(
    "No credible production chain",
  );
  await page.keyboard.press("End");
  await expect(page.locator("#currentSlide")).toHaveText("18");
  await expect(page.locator("#slide-18")).toContainText(
    "candidate governance ratifier",
  );
  await page.locator("#sourcesButton").click();
  await expect(page.locator("#sourceDialog")).toBeVisible();
  await expect(page.locator("#sourceDialog a")).toHaveCount(17);
  await page.locator("#sourceClose").click();
  expect(runtimeErrors).toEqual([]);
});

test("keeps dense decision slides usable on a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${deckUrl}#slide-8`, { waitUntil: "networkidle" });
  await expect(page.locator("#currentSlide")).toHaveText("08");
  await expect(page.locator("#slide-8 .phase-roadmap article")).toHaveCount(4);
  await page.goto(`${deckUrl}#slide-17`, { waitUntil: "networkidle" });
  await expect(page.locator("#slide-17 .decision-table")).toBeVisible();
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  expect(overflow).toBe(false);
});

test("keeps every slide inside the desktop presentation frame", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(deckUrl, { waitUntil: "networkidle" });
  for (let index = 0; index < 18; index += 1) {
    await page.locator(".deck-dots button").nth(index).click();
    await expect(page.locator(`#slide-${index + 1}`)).toHaveClass(/is-active/);
    await page.waitForTimeout(800);
    const bounds = await page
      .locator(`#slide-${index + 1}`)
      .evaluate((slide) => {
        const frame = slide.getBoundingClientRect();
        const technical = [
          ...slide.querySelectorAll(
            ":scope > .slide__content > :not(.human-blurb)",
          ),
        ].map((element) => element.getBoundingClientRect());
        const blurb = slide
          .querySelector(".human-blurb")
          .getBoundingClientRect();
        return {
          contentTop:
            Math.min(...technical.map((rect) => rect.top)) - frame.top,
          contentBottom:
            Math.max(...technical.map((rect) => rect.bottom)) - frame.top,
          blurbTop: blurb.top - frame.top,
          blurbBottom: blurb.bottom - frame.top,
        };
      });
    expect(
      bounds.contentTop,
      `slide ${index + 1} starts beneath the header`,
    ).toBeGreaterThanOrEqual(67);
    expect(
      bounds.contentBottom,
      `slide ${index + 1} clears its plain-English line`,
    ).toBeLessThanOrEqual(bounds.blurbTop - 2);
    expect(
      bounds.blurbBottom,
      `slide ${index + 1} clears the controls`,
    ).toBeLessThanOrEqual(834);
  }
});
