// E2E-проверка критериев приёмки ЛР2 через реальный браузер.
const { test, expect } = require("@playwright/test");

const URL = "http://127.0.0.1:5101/";

test.beforeEach(async ({ request, page }) => {
  await request.post(URL + "__e2e__/reset");
  await page.goto(URL);
});

async function pick(page, group, student) {
  await page.selectOption("#group", group);
  if (student) await page.selectOption("#student", { label: student });
}

test("группы из листов students.xlsx, студенты соответствуют листу", async ({ page }) => {
  await expect(page.locator("#group option")).toContainText(["ИТ-21", "ПИ-22", "Пустая-Группа"]);
  await pick(page, "ИТ-21");
  await expect(page.locator("#student option").nth(1)).toHaveText("Иванов Иван");
  await expect(page.locator("#student option")).toHaveCount(6); // плейсхолдер + 5 студентов
});

test("кнопка активна только при выбранных группе и студенте", async ({ page }) => {
  const btn = page.locator("#generate");
  await expect(btn).toBeDisabled();
  await pick(page, "ИТ-21");
  await expect(btn).toBeDisabled();
  await page.selectOption("#student", { label: "Иванов Иван" });
  await expect(btn).toBeEnabled();
});

test("пустая группа: список пуст, кнопка неактивна, без ошибок", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e));
  await pick(page, "Пустая-Группа");
  await expect(page.locator("#student option")).toHaveCount(1);
  await expect(page.locator("#generate")).toBeDisabled();
  expect(errors).toEqual([]);
});

test("генерация: окно с номером и тремя вопросами, строка в журнале сразу", async ({ page, request }) => {
  await pick(page, "ИТ-21", "Иванов Иван");
  await page.click("#generate");
  await expect(page.locator("#result")).toHaveClass(/open/);
  await expect(page.locator("#ticket-title")).toHaveText(/^Ваш билет № [1-5]$/);
  await expect(page.locator("#questions li")).toHaveCount(3);
  const rows = await (await request.get(URL + "__e2e__/journal")).json();
  expect(rows).toHaveLength(1);
  expect(rows[0].slice(0, 3)).toEqual(["ИТ-21", "Иванов", "Иван"]);
  expect(rows[0][5]).toBe(false);
});

test("ESC закрывает окно результата, приложение готово к следующему", async ({ page }) => {
  await pick(page, "ИТ-21", "Иванов Иван");
  await page.click("#generate");
  await expect(page.locator("#result")).toHaveClass(/open/);
  await page.keyboard.press("Escape");
  await expect(page.locator("#result")).not.toHaveClass(/open/);
  await expect(page.locator("#generate")).toBeEnabled();
  await page.selectOption("#student", { label: "Петров Петр" });
  await page.click("#generate");
  await expect(page.locator("#result")).toHaveClass(/open/);
});

test("повтор: тот же номер, новая строка в конце с Повтор=да", async ({ page, request }) => {
  await pick(page, "ИТ-21", "Иванов Иван");
  await page.click("#generate");
  await expect(page.locator("#result")).toHaveClass(/open/);
  const first = await page.locator("#ticket-title").textContent();
  await page.keyboard.press("Escape");
  await page.click("#generate");
  await expect(page.locator("#ticket-title")).toHaveText(first);
  await expect(page.locator("#repeat-badge")).toBeVisible();
  const rows = await (await request.get(URL + "__e2e__/journal")).json();
  expect(rows).toHaveLength(2);
  expect(rows[1][3]).toBe(rows[0][3]);
  expect([rows[0][5], rows[1][5]]).toEqual([false, true]);
  expect(rows[1][4] >= rows[0][4]).toBe(true); // хронологический порядок
});

test("заблокированный results.xlsx: сообщение и повтор без падения", async ({ page, request }) => {
  await request.post(URL + "__e2e__/lock/1");
  await pick(page, "ИТ-21", "Иванов Иван");
  await page.click("#generate");
  await expect(page.locator("#error")).toContainText("открыт в другой программе");
  await expect(page.locator("#retry")).toBeVisible();
  await expect(page.locator("#result")).not.toHaveClass(/open/);
  await request.post(URL + "__e2e__/lock/0");
  await page.click("#retry");
  await expect(page.locator("#result")).toHaveClass(/open/);
  const rows = await (await request.get(URL + "__e2e__/journal")).json();
  expect(rows).toHaveLength(1);
});

test("нет students.xlsx: понятное сообщение, страница работает", async ({ page }) => {
  await page.goto("http://127.0.0.1:5102/");
  await expect(page.locator("#error")).toContainText("students.xlsx");
  await expect(page.locator("#generate")).toBeDisabled();
});
