// 메신저 캡처 → SNS 스토리(세로 9:16) 형식 이미지로 합성해 PNG로 저장 (가상 서비스 모양, 로고 없음)
// 사용: node tools/make_story.mjs <캡처 이미지> <출력 png> "<스토리 글>" "@태그1 @태그2"
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import { readFileSync } from 'node:fs';
import { extname, resolve } from 'node:path';

const [src, out, caption = '', tagsArg = ''] = process.argv.slice(2);
if (!src || !out) { console.error('사용: node tools/make_story.mjs <캡처> <출력.png> "<스토리 글>" "@태그 @태그"'); process.exit(1); }
const mime = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' }[extname(src).toLowerCase()] || 'image/png';
const data = 'data:' + mime + ';base64,' + readFileSync(resolve(src)).toString('base64');
const tags = tagsArg.split(/\s+/).filter(Boolean);
const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const html = `<!doctype html><meta charset="utf-8"><style>
  * { box-sizing: border-box; margin: 0; }
  body { width: 1080px; height: 1920px; overflow: hidden; font-family: "Apple SD Gothic Neo", "Noto Sans KR", "WenQuanYi Zen Hei", sans-serif; color: #fff; }
  .story { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #1c2a3f; }
  .bg { position: absolute; inset: -80px; background: url("${data}") center / cover no-repeat; filter: blur(60px) saturate(1.3) brightness(.55); }
  .bars { position: absolute; top: 28px; left: 24px; right: 24px; display: flex; gap: 8px; }
  .bars i { flex: 1; height: 5px; border-radius: 4px; background: rgba(255,255,255,.4); }
  .bars i.done { background: #fff; }
  .who { position: absolute; top: 52px; left: 28px; right: 28px; display: flex; align-items: center; gap: 16px; font-size: 30px; font-weight: 600; }
  .who .pic { width: 76px; height: 76px; border-radius: 50%; background: linear-gradient(135deg,#f7c59f,#d98cb3); border: 3px solid #fff; display: grid; place-items: center; overflow: hidden; }
  .who .pic svg { width: 60px; height: 60px; margin-top: 14px; }
  .who .name { filter: blur(7px); letter-spacing: .04em; }
  .who .time { font-weight: 400; opacity: .75; font-size: 28px; }
  .who .more { margin-left: auto; font-size: 44px; letter-spacing: 2px; opacity: .9; line-height: 1; }
  .who .x { font-size: 46px; font-weight: 300; margin-left: 28px; line-height: 1; }
  .shot { position: absolute; left: 50%; top: 300px; width: 880px; transform: translateX(-50%) rotate(-1.5deg); border-radius: 28px; overflow: hidden; box-shadow: 0 30px 80px rgba(0,0,0,.55); }
  .shot img { display: block; width: 100%; }
  .cap { position: absolute; left: 50%; top: 214px; transform: translateX(-50%) rotate(-4deg); background: #fff; color: #111; font-weight: 900; font-size: 58px; padding: 14px 34px; border-radius: 16px; white-space: nowrap; letter-spacing: -.03em; box-shadow: 0 10px 30px rgba(0,0,0,.35); }
  .tags { position: absolute; left: 0; right: 0; top: 1450px; display: flex; justify-content: center; gap: 22px; flex-wrap: wrap; padding: 0 60px; }
  .tags span { background: rgba(255,255,255,.95); color: #1f2937; font-weight: 800; font-size: 40px; padding: 12px 30px; border-radius: 18px; letter-spacing: -.02em; }
  .tags span::before { content: ""; }
  .reply { position: absolute; left: 28px; right: 28px; bottom: 48px; display: flex; align-items: center; gap: 24px; }
  .reply .box { flex: 1; height: 92px; border: 2.5px solid rgba(255,255,255,.75); border-radius: 50px; padding: 0 36px; display: flex; align-items: center; font-size: 32px; opacity: .9; }
  .reply svg { width: 58px; height: 58px; }
</style>
<div class="story">
  <div class="bg"></div>
  <div class="bars"><i class="done"></i><i class="done"></i><i></i></div>
  <div class="who">
    <span class="pic"><svg viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="8" r="5"/><path d="M1 26c1.8-6.5 6-10 11-10s9.2 3.5 11 10z"/></svg></span>
    <span class="name">choi_iseo.__</span><span class="time">2시간</span>
    <span class="more">···</span><span class="x">×</span>
  </div>
  <div class="shot"><img src="${data}"></div>
  ${caption ? `<div class="cap">${esc(caption)}</div>` : ''}
  <div class="tags">${tags.map(t => `<span>${esc(t)}</span>`).join('')}</div>
  <div class="reply">
    <div class="box">메시지 보내기</div>
    <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8"><path d="M12 21s-7-4.6-9.5-9A5.3 5.3 0 0112 6a5.3 5.3 0 019.5 6c-2.5 4.4-9.5 9-9.5 9z"/></svg>
    <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8"><path d="M21 3L3 10.5l7.5 2 2 7.5z"/><path d="M10.5 12.5L21 3"/></svg>
  </div>
</div>`;

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.setContent(html);
await page.waitForTimeout(300);
await page.screenshot({ path: resolve(out), clip: { x: 0, y: 0, width: 1080, height: 1920 }, type: 'png' });
await browser.close();
console.log('만듦:', out);
