import {loadCaptionFonts} from './template-fonts';
import { type Cue, type Look, type Frame, defaultFrame, validateCues } from './captions';
import { outputDimensions, renderCaption, motionEnabled } from './render-caption';
let engine: import('@ffmpeg/ffmpeg').FFmpeg | null=null;
let loading: Promise<import('@ffmpeg/ffmpeg').FFmpeg> | null=null;
let locked=false;
async function ffmpeg(status:(text:string)=>void) {
  if(engine?.loaded)return engine;
  if(!loading)loading=(async()=>{
    status('Loading video tools for the first time…');
    const {FFmpeg}=await import('@ffmpeg/ffmpeg');const f=new FFmpeg();
    const chunks=await Promise.all([1,2].map(async n=>{const r=await fetch(`/ffmpeg/core-${n}.bin`);if(!r.ok)throw new Error('Video tools could not load. Check your connection and retry.');return r.arrayBuffer();}));
    const wasmURL=URL.createObjectURL(new Blob(chunks,{type:'application/wasm'}));
    let timer:ReturnType<typeof setTimeout>|undefined;
    try{await Promise.race([f.load({classWorkerURL:new URL('/ffmpeg/worker.js',location.origin).href,coreURL:new URL('/ffmpeg/ffmpeg-core.js',location.origin).href,wasmURL}),new Promise<never>((_,reject)=>{timer=setTimeout(()=>{f.terminate();reject(new Error('Video tools took too long to load. Check your connection and try again.'));},60000);})]);}finally{clearTimeout(timer);URL.revokeObjectURL(wasmURL);}
    engine=f;return f;
  })().catch(e=>{loading=null;throw e;});
  return loading;
}
async function run<T>(fn:(f:import('@ffmpeg/ffmpeg').FFmpeg)=>Promise<T>,status:(text:string)=>void):Promise<T> {
  if(locked)throw new Error('Another video operation is running. Please wait.');locked=true;
  try{return await fn(await ffmpeg(status));}catch(e){throw e instanceof Error?e:new Error(typeof e==='string'?e:'Video processing failed. Try a shorter video or 720p.');}finally{locked=false;}
}
const ext=(f:File)=>f.name.split('.').pop()?.toLowerCase() || 'mp4';
export async function extractAudio(file:File,status:(text:string)=>void) {
  return run(async f=>{
    const input='source.'+ext(file);try{
      status('Extracting speech audio…');await f.writeFile(input,new Uint8Array(await file.arrayBuffer()));
      const result=await f.exec(['-i',input,'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le','audio.wav']);
      if(result!==0)throw new Error('Could not extract audio. Check that the video has a playable audio track.');
      const audio=await f.readFile('audio.wav');return new File([audio as BlobPart],'audio.wav',{type:'audio/wav'});
    }finally{await f.deleteFile(input).catch(()=>{});await f.deleteFile('audio.wav').catch(()=>{});}
  },status);
}
export async function preparePreview(file:File,status:(text:string)=>void) {
  return run(async f=>{const input='source.'+ext(file);try{status('Preparing a browser-compatible preview…');await f.writeFile(input,new Uint8Array(await file.arrayBuffer()));
    const r=await f.exec(['-i',input,'-vf','scale=640:-2','-c:v','libx264','-preset','ultrafast','-crf','28','-c:a','aac','-movflags','+faststart','preview.mp4']);
    if(r!==0)throw new Error('This video could not be decoded.');return new Blob([await f.readFile('preview.mp4') as BlobPart],{type:'video/mp4'});
  }finally{await f.deleteFile(input).catch(()=>{});await f.deleteFile('preview.mp4').catch(()=>{});}},status);
}
export type ExportOptions={fps:30|60;quality:'Low'|'Medium'|'High';type:'video'|'green'|'blue'|'transparent';audio:boolean};
function crc32(bytes:Uint8Array){let crc=-1;for(const b of bytes){crc^=b;for(let i=0;i<8;i++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}return(crc^-1)>>>0;}
function zipStore(items:{name:string;data:Uint8Array}[]){const pieces:BlobPart[]=[],central:BlobPart[]=[];let offset=0,centralSize=0;const text=new TextEncoder();for(const item of items){const name=text.encode(item.name),crc=crc32(item.data),header=new Uint8Array(30+name.length),h=new DataView(header.buffer);h.setUint32(0,0x04034b50,true);h.setUint16(4,20,true);h.setUint32(14,crc,true);h.setUint32(18,item.data.length,true);h.setUint32(22,item.data.length,true);h.setUint16(26,name.length,true);header.set(name,30);pieces.push(header,item.data as BlobPart);const entry=new Uint8Array(46+name.length),v=new DataView(entry.buffer);v.setUint32(0,0x02014b50,true);v.setUint16(4,20,true);v.setUint16(6,20,true);v.setUint32(16,crc,true);v.setUint32(20,item.data.length,true);v.setUint32(24,item.data.length,true);v.setUint16(28,name.length,true);v.setUint32(42,offset,true);entry.set(name,46);central.push(entry);centralSize+=entry.length;offset+=header.length+item.data.length;}const end=new Uint8Array(22),e=new DataView(end.buffer);e.setUint32(0,0x06054b50,true);e.setUint16(8,items.length,true);e.setUint16(10,items.length,true);e.setUint32(12,centralSize,true);e.setUint32(16,offset,true);return new Blob([...pieces,...central,end],{type:'application/zip'});}
export async function burnVideo(file:File|null,cues:Cue[],look:Look,aspect:string,resolution:number,width:number,height:number,duration:number,status:(s:string)=>void,onProgress:(n:number)=>void,frame:Frame=defaultFrame,options:ExportOptions={fps:30,quality:'Medium',type:'video',audio:true}){
 validateCues(cues,duration);if(!cues.length||!duration)throw Error('Add timed captions before exporting.');if(options.type==='video'&&!file)throw Error('Attach your video first.');
 await loadCaptionFonts([look,...cues.map(c=>({...look,...c.look}))]);await document.fonts.ready;
 const dims=outputDimensions(width,height,aspect,resolution),canvas=document.createElement('canvas');canvas.width=dims.width;canvas.height=dims.height;const ctx=canvas.getContext('2d')!;const boundaries=new Set([0,duration]);cues.forEach(c=>{boundaries.add(c.start);boundaries.add(c.end);c.words?.forEach(w=>{for(const t of [w.start,w.end,w.end+.15])if(t>c.start&&t<c.end)boundaries.add(t);});});
 const animated=motionEnabled(look)||cues.some(c=>c.look&&motionEnabled({...look,...c.look}));const times=animated?Array.from({length:Math.ceil(duration*options.fps)+1},(_,i)=>Math.min(duration,i/options.fps)):[...boundaries].sort((a,b)=>a-b);if(times.length>18000)throw Error('Use a shorter clip, 30 fps, or static captions.');
 const items:{name:string;data:Uint8Array}[]=[],frames:{duration:number}[]=[];status('Drawing your caption frames…');let bytes=0;
 for(let i=0;i<times.length-1;i++){const t=animated?times[i]:(times[i]+times[i+1])/2;renderCaption(ctx,dims.width,dims.height,[...cues].reverse().find(c=>t>=c.start&&t<c.end),look,t);const blob=await new Promise<Blob>((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(Error('Caption frame failed.')),'image/png'));const data=new Uint8Array(await blob.arrayBuffer());bytes+=data.length;if(bytes>450*1024*1024)throw Error('Caption frames exceed local memory limits. Try 720p or 30 fps.');items.push({name:`caption-${i}.png`,data});frames.push({duration:times[i+1]-times[i]});onProgress(i/(times.length-1)*20);}
 const manifest={...options,...dims,duration,frames,frame,sourceWidth:width,sourceHeight:height};items.push({name:'manifest.json',data:new TextEncoder().encode(JSON.stringify(manifest))});const form=new FormData();form.append('frames',zipStore(items),'captions.zip');if(file&&(options.type==='video'||options.audio))form.append('media',file);status('Encoding your export locally…');const r=await fetch('/api/render-export',{method:'POST',body:form});const request=await r.json() as any;if(!r.ok)throw Error(request.error||'Export could not start.');
 const deadline=Date.now()+30*60*1000;while(Date.now()<deadline){await new Promise(resolve=>setTimeout(resolve,500));const j=await fetch('/api/jobs/'+request.jobId).then(r=>r.json()) as any;status(j.message||'Exporting…');if(typeof j.progress==='number')onProgress(j.progress);if(j.status==='failed')throw Error(j.error);if(j.status==='complete'){const result=await fetch(j.result.url);if(!result.ok)throw Error('The rendered file is unavailable.');onProgress(100);return result.blob();}}throw Error('Export took too long. Try a shorter video.');
}
