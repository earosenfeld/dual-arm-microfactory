const { chromium } = require("playwright");

const baseUrl = process.env.DEMO_URL || "http://127.0.0.1:8770/docs/demo/";

async function canvasStats(frameOrPage) {
  return frameOrPage.evaluate(() => {
    const canvas = document.querySelector("#robotViewport canvas");
    const gl = canvas?.getContext("webgl2") || canvas?.getContext("webgl");
    if (!canvas || !gl) return { ok: false, reason: "missing canvas or WebGL context" };

    const width = Math.min(220, gl.drawingBufferWidth);
    const height = Math.min(140, gl.drawingBufferHeight);
    const x = Math.max(0, Math.floor((gl.drawingBufferWidth - width) / 2));
    const y = Math.max(0, Math.floor((gl.drawingBufferHeight - height) / 2));
    const pixels = new Uint8Array(width * height * 4);
    gl.readPixels(x, y, width, height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);

    let nonDark = 0;
    let bright = 0;
    for (let i = 0; i < pixels.length; i += 4) {
      const sum = pixels[i] + pixels[i + 1] + pixels[i + 2];
      if (sum > 28) nonDark += 1;
      if (sum > 120) bright += 1;
    }

    return {
      ok: nonDark > width * height * 0.04 && bright > width * height * 0.002,
      drawingBufferWidth: gl.drawingBufferWidth,
      drawingBufferHeight: gl.drawingBufferHeight,
      nonDark,
      bright,
    };
  });
}

async function withBrowser(callback) {
  const browser = process.env.PLAYWRIGHT_CDP_ENDPOINT
    ? await chromium.connectOverCDP(process.env.PLAYWRIGHT_CDP_ENDPOINT)
    : await chromium.launch({
        args: ["--disable-gpu", "--enable-unsafe-swiftshader"],
      });
  try {
    await callback(browser);
  } finally {
    await browser.close();
  }
}

async function smokeWorkbench(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });

  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.waitForSelector("#scenarioButtons .scenario-button", { timeout: 12000 });
  await page.waitForFunction(() => {
    return document.querySelectorAll("#scenarioButtons .scenario-button").length >= 5
      && document.querySelectorAll("#metricGrid .metric").length >= 8
      && document.querySelector("#replayFrame");
  }, null, { timeout: 12000 });

  const frameElement = await page.waitForSelector("#replayFrame", { timeout: 5000 });
  const frame = await frameElement.contentFrame();
  if (!frame) throw new Error("replay iframe did not expose a content frame");
  await frame.waitForSelector("#robotViewport canvas", { timeout: 12000 });
  await frame.waitForTimeout(700);
  const stats = await canvasStats(frame);
  if (!stats.ok) throw new Error(`embedded dashboard canvas appears blank: ${JSON.stringify(stats)}`);

  await page.click("#recordingModeButton");
  await page.waitForFunction(() => {
    return document.querySelector("#replayFrame")?.getAttribute("src")?.includes("?cinematic=1");
  }, null, { timeout: 5000 });

  const result = await page.evaluate(() => ({
    scenarios: document.querySelectorAll("#scenarioButtons .scenario-button").length,
    metrics: document.querySelectorAll("#metricGrid .metric").length,
    frameSrc: document.querySelector("#replayFrame")?.getAttribute("src"),
    mode: document.querySelector("#frameMode")?.innerText.trim(),
  }));
  if (result.scenarios !== 5 || result.metrics < 8 || result.mode !== "VIDEO MODE") {
    throw new Error(`unexpected workbench state: ${JSON.stringify(result)}`);
  }
  if (errors.length > 0) throw new Error(`browser errors: ${errors.join(" | ")}`);
  await page.close();
}

async function smokeCinematic(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });

  await page.goto(new URL("belt_slip/dashboard.html?cinematic=1", baseUrl).toString(), {
    waitUntil: "networkidle",
  });
  await page.waitForSelector(".cinematic-overlay", { timeout: 12000 });
  await page.waitForFunction(() => {
    return document.body.classList.contains("cinematic-mode")
      && document.querySelectorAll("#cinematicChapters .chapter-pill").length >= 6
      && document.querySelector("#robotViewport canvas");
  }, null, { timeout: 12000 });
  await page.waitForTimeout(2200);

  const result = await page.evaluate(() => ({
    time: document.querySelector("#cinematicTime")?.textContent,
    hiddenHud: getComputedStyle(document.querySelector(".hud")).display,
    hiddenToolbar: getComputedStyle(document.querySelector(".viewport-toolbar")).display,
    activeChapters: document.querySelectorAll(".chapter-pill.active").length,
  }));
  const stats = await canvasStats(page);
  if (!stats.ok) throw new Error(`cinematic canvas appears blank: ${JSON.stringify(stats)}`);
  if (result.hiddenHud !== "none" || result.hiddenToolbar !== "none" || result.activeChapters !== 1) {
    throw new Error(`unexpected cinematic state: ${JSON.stringify(result)}`);
  }
  if (result.time === "0.0s") throw new Error("cinematic autoplay did not advance replay time");
  if (errors.length > 0) throw new Error(`browser errors: ${errors.join(" | ")}`);
  await page.close();
}

async function smokePreview(browser) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });

  await page.goto(new URL("belt_slip/dashboard.html?preview=1", baseUrl).toString(), {
    waitUntil: "networkidle",
  });
  await page.waitForSelector("#robotViewport canvas", { timeout: 12000 });
  await page.waitForFunction(() => document.body.classList.contains("preview-mode"), null, {
    timeout: 12000,
  });
  await page.waitForTimeout(1900);

  const result = await page.evaluate(() => ({
    time: document.querySelector("#currentTime")?.textContent,
    hiddenHud: getComputedStyle(document.querySelector(".hud")).display,
    hiddenControls: getComputedStyle(document.querySelector(".controls")).display,
    hiddenToolbar: getComputedStyle(document.querySelector(".viewport-toolbar")).display,
  }));
  const stats = await canvasStats(page);
  if (!stats.ok) throw new Error(`preview canvas appears blank: ${JSON.stringify(stats)}`);
  if (
    result.hiddenHud !== "none"
    || result.hiddenControls !== "none"
    || result.hiddenToolbar !== "none"
  ) {
    throw new Error(`unexpected preview chrome state: ${JSON.stringify(result)}`);
  }
  if (result.time === "0.0s") throw new Error("preview autoplay did not advance replay time");
  if (errors.length > 0) throw new Error(`browser errors: ${errors.join(" | ")}`);
  await page.close();
}

(async () => {
  await withBrowser(async (browser) => {
    await smokeWorkbench(browser);
    await smokeCinematic(browser);
    await smokePreview(browser);
  });
  console.log("browser smoke checks passed");
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
