# Puppeteer HTML-to-Image Screenshot Recipe

Used when no image generation API key is configured -- render an infographic as HTML+CSS and screenshot with headless Chrome.

## Quick Install

```bash
npm install puppeteer
```

## Minimal Screenshot Script

```js
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 780 });
  await page.goto('file:///path/to/input.html', {
    waitUntil: 'networkidle0',
    timeout: 30000
  });
  await page.screenshot({
    path: 'output.png',
    type: 'png',
    fullPage: true
  });
  await browser.close();
  const fs = require('fs');
  const size = fs.statSync('output.png').size;
  console.log('Screenshot saved: ' + size + ' bytes');
})();
```

## Infographic Design Tips

- **Background**: `#0f1729` (dark navy) with subtle gradient overlays
- **Primary accent**: `#38bdf8` (sky blue) for left/standard elements
- **Secondary accent**: `#2dd4bf` (teal) for right/advanced elements
- **Text**: `#e2e8f0` primary, `#94a3b8` secondary, `#64748b` for labels
- **Cards**: `rgba(30,64,110,0.5)` with `1px solid rgba(56,189,248,0.15)` for glass-morphism
- **Bar charts**: Use `linear-gradient` with `box-shadow` for glow effects
- **Animations**: `@keyframes glow-pulse` for breathing glow on highlighted elements

## Pitfalls

- `--no-sandbox` is mandatory in container/WSL environments
- `headless: 'new'` is the correct modern headless mode
- Always use `file:///` protocol for local HTML files
- `networkidle0` wait ensures all CSS/fonts are loaded
- Set timeout >= 30000ms for complex pages with animations
- Save both `.html` source and `.png` screenshot
- PNG output is usually 200-500 KB for a 1280x780 infographic
