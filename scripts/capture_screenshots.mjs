import { chromium } from "playwright";

const baseUrl = process.env.ARTIFACT_URL || "http://localhost:5973";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1040 } });
await page.goto(baseUrl, { waitUntil: "networkidle" });

await page.screenshot({ path: "docs/images/launch-cockpit.png", fullPage: false });

const captures = [
  ["Extraction Queue", "docs/images/extraction-queue.png"],
  ["Schema Governance", "docs/images/schema-governance.png"],
  ["Buyer Brief", "docs/images/buyer-brief.png"],
];

for (const [label, path] of captures) {
  await page.getByRole("button", { name: label }).click();
  await page.waitForTimeout(250);
  await page.screenshot({ path, fullPage: false });
}

await browser.close();
console.log("Captured portfolio artifact screenshots.");
