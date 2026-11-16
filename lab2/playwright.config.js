// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./e2e",
  workers: 1, // тесты делят один журнал results.xlsx на сервере
  reporter: [["list"]],
  use: { browserName: "chromium", headless: true },
  webServer: [
    { command: "python e2e/e2e_server.py 5101", url: "http://127.0.0.1:5101/", reuseExistingServer: false },
    { command: "python e2e/e2e_server.py 5102 --missing", url: "http://127.0.0.1:5102/", reuseExistingServer: false },
  ],
});
