import { readFileSync, writeFileSync } from "node:fs";
import { expect, test, type Page } from "@playwright/test";

const ROOT = new URL("../../", import.meta.url);
const file = (path: string) => new URL(path, ROOT).pathname;
const KOPPEJAN = file("tests/fixtures/koppejan.sli");
const SOILS = file("examples/soils.csv");
const TERZAGHI = file("tests/fixtures/terzaghi.sld");
const DARCY = file("tests/fixtures/darcy.sld");

let violations: string[];

test.beforeEach(async ({ page }) => {
  violations = [];
  // a blocked script, style or worker shows up as a console message
  page.on("console", (message) => {
    if (/Content Security Policy|Refused to/i.test(message.text())) violations.push(message.text());
  });
  page.on("pageerror", (error) => violations.push(error.message));
  // everything comes from the site itself, nothing from a CDN or font service
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (!["http:", "https:"].includes(url.protocol)) return;
    if (url.hostname !== "localhost") violations.push(`request to another server: ${request.url()}`);
  });
  await page.addInitScript(() => localStorage.setItem("language", "en"));
});

test.afterEach(() => {
  expect(violations, "no Content Security Policy violations or page errors").toEqual([]);
});

const menu = (page: Page, name: string) =>
  page.getByRole("navigation", { name: "Menu" }).getByRole("button", { name, exact: true });

// the button in the content, the menu has an item with the same name
const contentButton = (page: Page, name: string) => page.locator("main").getByRole("button", { name, exact: true });

async function open(page: Page, hash = "") {
  await page.goto(`./${hash}`);
  await expect(page.getByRole("status")).toHaveText("Ready", { timeout: 60_000 });
}

test("diagnostics pass", async ({ page }) => {
  await page.goto("./#diagnose");
  const steps = page.locator("ol.steps li");
  await expect(steps).toHaveCount(6);
  await expect(page.locator("ol.steps li.ok")).toHaveCount(6, { timeout: 60_000 });
  await expect(page.locator("ol.steps li.failed")).toHaveCount(0);
  await expect(steps.nth(4)).toContainText("koppejan.bj.sli");
});

test("converts a Koppejan calculation", async ({ page }) => {
  await open(page);
  await page.locator('input[accept=".csv"]').setInputFiles(SOILS);
  await expect(page.getByText("9 soils")).toBeVisible();
  await page.locator('input[accept=".sli"]').first().setInputFiles(KOPPEJAN);
  await expect(page.getByText("NEN-Koppejan → NEN-Bjerrum")).toBeVisible();

  await contentButton(page, "Convert").click();
  await expect(page.getByText("Converted to koppejan.bj.sli")).toBeVisible();
  await expect(page.getByText("The calculation uses Terzaghi, Darcy is preferred.")).toBeVisible();

  const [download] = await Promise.all([
    page.waitForEvent("download"),
    contentButton(page, "Download").click(),
  ]);
  expect(download.suggestedFilename()).toBe("koppejan.bj.sli");
  const text = readFileSync(await download.path(), "latin1");
  expect(text).toContain("1 : Model = NEN - Bjerrum\r\n");
  expect(text).toContain("FILENAME   : koppejan.bj.sli\r\n");
  expect(text).toContain("SoilCa=0.0170000\r\n");
});

test("shows soils that are missing from the soils file", async ({ page }, testInfo) => {
  await open(page);
  const soils = testInfo.outputPath("soils.csv");
  writeFileSync(soils, readFileSync(SOILS, "utf-8").replace("Peat A;", "Other;"));
  await page.locator('input[accept=".csv"]').setInputFiles(soils);
  await page.locator('input[accept=".sli"]').first().setInputFiles(KOPPEJAN);

  await expect(page.getByText("Not in the soils file: Peat A")).toBeVisible();
  await expect(contentButton(page, "Convert")).toBeDisabled();
});

test("shows the soil parameters and uses them for the conversion", async ({ page }) => {
  await open(page);
  await menu(page, "Soil parameters").click();
  await page.locator('input[accept=".sli"]').nth(1).setInputFiles(KOPPEJAN);

  const table = page.locator("table");
  await expect(table.locator("tbody tr")).toHaveCount(9);
  // rr, cr and calpha are placeholders in a Koppejan calculation
  await expect(table.locator("td.placeholder")).toHaveCount(27);

  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Download as soils.csv" }).click(),
  ]);
  const csv = readFileSync(await download.path(), "utf-8");
  expect(csv.split("\n")[0]).toBe("code;yd;ys;cp;cap;cs;cas;rr;cr;calpha;pop;ocr;cv;k");

  await page.getByRole("button", { name: "Convert →" }).click();
  await expect(page.getByText("9 soils")).toBeVisible();
});

test("compares the time-settlement curves of calculations", async ({ page }) => {
  await open(page);
  await menu(page, "Results").click();
  await page.locator('input[accept=".sld"]').setInputFiles([TERZAGHI, DARCY]);

  // one line per calculation, for the selected vertical
  await expect(page.locator("path.line")).toHaveCount(2);
  const select = page.getByLabel("Vertical", { exact: true });
  await expect(select).toHaveValue("1");
  await expect(select.locator("option")).toHaveText(["Vertical 1 (x = 5 m)", "Vertical 2 (x = 15 m)"]);

  await select.selectOption("2");
  await page.getByRole("button", { name: "Show table" }).click();
  const tables = page.locator(".tables table");
  await expect(tables).toHaveCount(2);
  await expect(tables.nth(0)).toContainText("terzaghi.sld");
  await expect(tables.nth(1)).toContainText("darcy.sld");
  for (const table of await tables.all()) await expect(table).toContainText("0.2500000");
});

test("refuses results with other verticals", async ({ page }, testInfo) => {
  await open(page);
  await menu(page, "Results").click();
  await page.locator('input[accept=".sld"]').setInputFiles(TERZAGHI);
  await expect(page.locator("path.line")).toHaveCount(1);

  const text = readFileSync(TERZAGHI, "latin1");
  const moved = testInfo.outputPath("moved.sld");
  writeFileSync(moved, text.replace("  15.0000000     =  X co-ordinate", "  16.0000000     =  X co-ordinate"), "latin1");
  // only the first vertical: cut from the second [Vertical] to the last [End of Vertical]
  const single = testInfo.outputPath("single.sld");
  const second = text.indexOf("[End of Vertical]") + "[End of Vertical]".length;
  writeFileSync(single, text.slice(0, second) + text.slice(text.lastIndexOf("[End of Vertical]") + "[End of Vertical]".length), "latin1");

  await page.locator('input[accept=".sld"]').setInputFiles([moved, single, DARCY]);
  await expect(page.getByText("vertical 2 is at x = 16 m, z = 0 m where it is at x = 15 m, z = 0 m in terzaghi.sld")).toBeVisible();
  await expect(page.getByText("has 1 vertical(s) where terzaghi.sld has 2")).toBeVisible();
  // the refused files are not added, the matching one is
  await expect(page.locator("path.line")).toHaveCount(2);
  await expect(page.locator("ul.files li")).toHaveCount(2);
});

test("shows the help and switches the language", async ({ page }) => {
  await open(page);
  await expect(page.locator("h1")).toHaveText("Convert");

  await page.getByRole("button", { name: "Help" }).click();
  const help = page.getByRole("dialog");
  await expect(help).toBeVisible();
  await expect(help).toContainText("LithoVox slicmd");
  await page.keyboard.press("Escape");
  await expect(help).toBeHidden();

  await page.getByRole("button", { name: "Language" }).click();
  await page.getByRole("button", { name: "NL" }).click();
  await expect(page.locator("h1")).toHaveText("Omzetten");
  await expect(menu(page, "Grondparameters")).toBeVisible();
});

test("folds the menu", async ({ page }) => {
  await open(page);
  await page.getByRole("button", { name: "Fold the menu" }).click();
  await expect(menu(page, "Results")).toBeHidden();
  await page.getByRole("button", { name: "Unfold the menu" }).click();
  await expect(menu(page, "Results")).toBeVisible();
});

test("edits the soil parameters before converting", async ({ page }) => {
  await open(page);
  await page.locator('input[accept=".csv"]').setInputFiles(SOILS);
  const table = page.locator(".soils-table");
  await expect(table.locator("tbody tr")).toHaveCount(9);

  // an invalid value stops the conversion until it is corrected
  const calpha = table.getByLabel("Peat A calpha");
  await calpha.fill("abc");
  await calpha.blur();
  await expect(page.getByText("'Peat A': invalid value 'abc' for column 'calpha'")).toBeVisible();
  await expect(calpha).toHaveClass(/invalid/);
  await page.locator('input[accept=".sli"]').first().setInputFiles(KOPPEJAN);
  await expect(contentButton(page, "Convert")).toBeDisabled();

  // a decimal comma is accepted
  await calpha.fill("0,02");
  await calpha.blur();
  await expect(page.getByText("edited", { exact: true })).toBeVisible();
  await expect(contentButton(page, "Convert")).toBeEnabled();
  await contentButton(page, "Convert").click();

  const [converted] = await Promise.all([page.waitForEvent("download"), contentButton(page, "Download").click()]);
  expect(readFileSync(await converted.path(), "latin1")).toContain("SoilCa=0.0200000\r\n");

  const [soilsFile] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Download soils file" }).click(),
  ]);
  expect(readFileSync(await soilsFile.path(), "utf-8")).toContain("Peat A;10.5;10.5;3.00E+01;5.00E+00;1.50E+02;8.00E+01;0.1;0.3;0,02;");
});

test("adds the soils a calculation misses", async ({ page }, testInfo) => {
  await open(page);
  const soils = testInfo.outputPath("soils.csv");
  writeFileSync(soils, readFileSync(SOILS, "utf-8").replace("Peat A;", "Other;"));
  await page.locator('input[accept=".csv"]').setInputFiles(soils);
  await page.locator('input[accept=".sli"]').first().setInputFiles(KOPPEJAN);
  await expect(page.getByText("Not in the soils file: Peat A")).toBeVisible();

  await page.getByRole("button", { name: "Add the 1 missing soil(s)" }).click();
  const table = page.locator(".soils-table");
  await expect(table.locator("tbody tr")).toHaveCount(10);
  await expect(table.getByLabel("Peat A yd")).toHaveValue("");
  await expect(page.getByText("Not in the soils file: Peat A")).toBeHidden();
  // the new soil still has no values
  await expect(contentButton(page, "Convert")).toBeDisabled();

  await table.getByRole("button", { name: "Remove Other" }).click();
  await expect(table.locator("tbody tr")).toHaveCount(9);
});
