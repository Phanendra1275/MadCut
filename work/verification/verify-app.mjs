import {createRequire} from 'node:module';
import {writeFile,mkdir} from 'node:fs/promises';
const require=createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {chromium}=require('playwright');
const browser=await chromium.launch({headless:true,channel:'chrome'});
const page=await browser.newPage({viewport:{width:1440,height:1080}});
const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.log('Page error:',e.message);});page.on('console',m=>{if(m.type()==='error')console.log('Browser:',m.text());});
await page.goto('http://localhost:5173',{waitUntil:'networkidle',timeout:120000});
await page.getByRole('button',{name:'Try an editable example'}).click();
await page.getByRole('textbox',{name:'Caption 1 text'}).fill('Nuvvu eeroju college ki vasthunnava?');
await page.getByRole('button',{name:'Telugu',exact:true}).click();
await page.getByRole('button',{name:/WhatsApp.*Like your chats/}).click();
await page.screenshot({path:'work/verification/desktop.png',fullPage:true});
const downloadEvent=page.waitForEvent('download');
await page.getByRole('button',{name:'Export',exact:true}).click();
await page.getByRole('button',{name:'.SRT',exact:true}).click();
await (await downloadEvent).saveAs('work/verification/verified.srt');
await page.keyboard.press('Escape');
await page.locator('input[type=file]').first().setInputFiles('work/verification/test-video.mp4');
await page.waitForFunction(()=>document.querySelector('video')?.duration===3);
await writeFile('work/verification/test.srt','1\n00:00:00,000 --> 00:00:01,500\nనువ్వు ఎక్కడికి వెళ్తున్నావు?\n\n2\n00:00:01,500 --> 00:00:03,000\nCollege ki velthunna.\n');
await page.locator('input[type=file]').nth(1).setInputFiles('work/verification/test.srt');
await page.getByRole('button',{name:/Minimal.*Simple & clear/}).click();
await page.waitForTimeout(1200);
await page.reload({waitUntil:'networkidle'});
await page.getByRole('textbox',{name:'Caption 1 text'}).waitFor();
await page.getByRole('button',{name:'Export',exact:true}).click();
await page.getByRole('combobox',{name:'Export resolution'}).click();
await page.getByRole('option',{name:'720p · Faster export'}).click();
const mp4Event=page.waitForEvent('download',{timeout:180000});
await page.getByRole('button',{name:'Export captioned video',exact:true}).click();console.log('Export started');
await (await mp4Event).saveAs('work/verification/burned.mp4');
await page.setViewportSize({width:390,height:844});
await page.screenshot({path:'work/verification/mobile.png',fullPage:true});
const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
console.log(JSON.stringify({pageErrors:errors,mobileOverflow:overflow,mp4:'work/verification/burned.mp4',draftReload:true}));
await browser.close();




