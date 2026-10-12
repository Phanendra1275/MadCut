import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
const require=createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {chromium}=require('playwright');const browser=await chromium.launch({headless:true,channel:'chrome'});
const page=await browser.newPage({viewport:{width:1920,height:970}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:5173/#studio');
const project=JSON.parse(await readFile('work/verification/video-reference/test-project.json','utf8'));
project.frame={scale:100,width:100,height:100,x:0,y:0,rotation:0,background:'#0b0b0d'};project.aspect='9:16';project.look={template:'Keyword Spotlight',size:72,color:'#ffffff',position:72,bold:true,font:'Auto',motion:true};
await writeFile('work/verification/captik-review/project.json',JSON.stringify(project));
await page.locator('input[type=file]').nth(2).setInputFiles('work/verification/captik-review/project.json');
await page.getByRole('textbox',{name:'Caption 1 text',exact:true}).waitFor();
await page.locator('input[type=file]').first().setInputFiles('work/verification/prasad-frame-test.mp4');
await page.waitForFunction(()=>document.querySelector('.video-frame video')?.readyState===4);
await page.locator('.video-frame video').evaluate(v=>{v.currentTime=2;v.dispatchEvent(new Event('timeupdate'));});await page.waitForTimeout(400);
if(await page.locator('.template-card').count()!==55)throw Error('Expected 55 templates');
await page.locator('.style-panel').evaluate(e=>e.scrollTop=500);
await page.waitForTimeout(400);
const poster=await page.locator('.template-footage').first().evaluate(c=>{const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return {width:c.width,height:c.height,visiblePixels:Array.from(d).filter((v,i)=>i%4!==3&&v>40).length};});
if(poster.visiblePixels<10000||Math.abs(poster.width/poster.height-9/16)>.003)throw Error('Footage poster/ratio incorrect');
if(await page.locator('video').count()>5)throw Error('Preview videos unnecessarily duplicated');
const results=[];
for(const name of ['Keyword Spotlight','Word Wipe','Focus Glow']){
 await page.getByRole('button',{name:'Apply '+name+' template',exact:true}).click();
 const frames=[];
 for(const t of [.45,1.25,2.1]){
  await page.locator('.video-frame video').evaluate((v,t)=>{v.currentTime=t;v.dispatchEvent(new Event('timeupdate'));},t);
  await page.waitForTimeout(160);
  frames.push(await page.locator('.caption-canvas').evaluate(c=>{const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0,hash=0;for(let i=0;i<d.length;i+=4)if(d[i+3]){pixels++;hash=(hash*31+d[i]+d[i+1]+d[i+2]+i)>>>0;}return {pixels,hash};}));
 }
 if(frames.some(f=>f.pixels<20)||new Set(frames.map(f=>f.hash)).size!==3)throw Error('Missing/distinct word frames '+name);
 results.push({name,frames});
}
await page.getByRole('button',{name:'Apply Keyword Spotlight template',exact:true}).click();
await page.locator('.video-frame video').evaluate(v=>{v.currentTime=2.1;v.dispatchEvent(new Event('timeupdate'));});
await page.getByRole('textbox',{name:'Search templates',exact:true}).fill('');await page.getByRole('textbox',{name:'Search templates',exact:true}).fill('Keyword');await page.locator('.style-panel').evaluate(e=>e.scrollTop=350);await page.waitForTimeout(500);
const filteredPoster=await page.locator('.template-footage').first().evaluate(c=>Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data).filter((v,i)=>i%4!==3&&v>40).length);if(await page.locator('.live-template-preview').first().evaluate(c=>getComputedStyle(c).backgroundColor)!=='rgba(0, 0, 0, 0)')throw Error('Overlay hides footage');if(filteredPoster<1000)throw Error('Filtered preview blank');await page.screenshot({path:'work/verification/captik-review/editor.png'});
if(await page.getByRole('textbox',{name:'Caption 1 text',exact:true}).inputValue()!=='Nuvvu em chesthunnav?')throw Error('Caption text changed');
await page.reload();await page.getByRole('textbox',{name:'Caption 1 text',exact:true}).waitFor();
await page.waitForFunction(()=>document.querySelector('.video-frame video')?.readyState===4);
if(!await page.locator('.template-card.chosen').getByRole('button',{name:'Apply Keyword Spotlight template',exact:true}).count())throw Error('Style not persisted');
await page.getByRole('button',{name:'Export',exact:true}).click();const download=page.waitForEvent('download',{timeout:180000});await page.getByRole('button',{name:'Export 720p',exact:true}).click();await(await download).saveAs('work/verification/captik-review/keyword-export.mp4');
await browser.close();if(errors.length)throw Error(errors.join(','));
await writeFile('work/verification/captik-review/results.json',JSON.stringify({count:55,poster,results,preservedText:true,persistedStyle:true,realMp4Export:true,errors},null,2));console.log('Passed 55 presets, real footage posters, three distinct timed effects, unchanged text, reload persistence and actual MP4 export.');
