const fs = require("fs");
const path = require("path");

function requireDependency(name) {
  try {
    return require(name);
  } catch (error) {
    if (error.code !== "MODULE_NOT_FOUND") throw error;
    console.error(
      `Missing Node dependency "${name}". Install locally with: npm install --no-save playwright gifenc pngjs`
    );
    process.exit(1);
  }
}

const { chromium } = requireDependency("playwright");
const { GIFEncoder, quantize, applyPalette } = requireDependency("gifenc");
const { PNG } = requireDependency("pngjs");

const repoRoot = path.resolve(__dirname, "..");
const baseUrl = process.env.DEMO_URL || "http://127.0.0.1:8770/docs/demo/";
const scenario = process.env.SCENARIO || "belt_slip";
const outputPath = path.resolve(
  repoRoot,
  process.env.OUTPUT || "docs/assets/hero-demo.gif"
);
const frameCount = Number(process.env.FRAME_COUNT || 16);
const frameDelayMs = Number(process.env.FRAME_DELAY_MS || 170);
const warmupMs = Number(process.env.WARMUP_MS || 2300);
const colors = Number(process.env.GIF_COLORS || 128);

async function readCanvasStats(page) {
  return page.evaluate(() => {
    const canvas = document.querySelector("#robotViewport canvas");
    const gl = canvas?.getContext("webgl2") || canvas?.getContext("webgl");
    if (!canvas || !gl) return { ok: false, reason: "missing canvas or WebGL context" };

    const width = Math.min(260, gl.drawingBufferWidth);
    const height = Math.min(160, gl.drawingBufferHeight);
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
      nonDark,
      bright,
      width,
      height,
    };
  });
}

async function openBrowser() {
  if (process.env.PLAYWRIGHT_CDP_ENDPOINT) {
    return chromium.connectOverCDP(process.env.PLAYWRIGHT_CDP_ENDPOINT);
  }
  return chromium.launch({
    args: ["--disable-gpu", "--enable-unsafe-swiftshader"],
  });
}

async function main() {
  const browser = await openBrowser();
  try {
    const page = await browser.newPage({
      viewport: { width: 1280, height: 720 },
      deviceScaleFactor: 1,
    });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    const previewUrl = new URL(`${scenario}/dashboard.html?preview=1`, baseUrl).toString();
    await page.goto(previewUrl, { waitUntil: "networkidle" });
    await page.waitForSelector("#robotViewport canvas", { timeout: 12000 });
    await page.waitForTimeout(warmupMs);

    const stats = await readCanvasStats(page);
    if (!stats.ok) {
      throw new Error(`README preview canvas appears blank: ${JSON.stringify(stats)}`);
    }

    const viewport = page.locator("#robotViewport");
    const frames = [];
    for (let i = 0; i < frameCount; i += 1) {
      frames.push(await viewport.screenshot({ type: "png" }));
      await page.waitForTimeout(frameDelayMs);
    }

    if (errors.length > 0) {
      throw new Error(`browser errors: ${errors.join(" | ")}`);
    }

    const gif = GIFEncoder();
    let width = 0;
    let height = 0;
    frames.forEach((frame, i) => {
      const png = PNG.sync.read(frame);
      if (i === 0) {
        width = png.width;
        height = png.height;
      }
      if (png.width !== width || png.height !== height) {
        throw new Error(`frame ${i} changed size from ${width}x${height} to ${png.width}x${png.height}`);
      }
      const palette = quantize(png.data, colors, { format: "rgb565" });
      const indexed = applyPalette(png.data, palette, "rgb565");
      gif.writeFrame(indexed, width, height, {
        palette,
        delay: frameDelayMs,
        repeat: 0,
      });
    });
    gif.finish();

    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, Buffer.from(gif.bytes()));
    const sizeMb = fs.statSync(outputPath).size / (1024 * 1024);
    console.log(`Wrote ${path.relative(repoRoot, outputPath)} (${width}x${height}, ${sizeMb.toFixed(1)} MB)`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
