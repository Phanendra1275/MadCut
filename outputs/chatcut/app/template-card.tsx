import {loadCaptionFonts} from '../lib/template-fonts';
import {useEffect,useRef,type RefObject} from 'react';
import {renderCaption,wordTimeline} from '../lib/render-caption';
import type {Look,Cue,Frame} from '../lib/captions';
import type {Template} from '../lib/templates';
export function TemplatePreview({template,sample,look,preview,animate=true,media,mediaKey,frame,ratio=16/9,cue:sourceCue}:{template:Template;sample:string;look?:Partial<Look>;preview?:string;animate?:boolean;media?:RefObject<HTMLVideoElement|null>;mediaKey?:string;frame?:Frame;ratio?:number;cue?:Cue}){
 const ref=useRef<HTMLCanvasElement>(null),background=useRef<HTMLCanvasElement>(null),onFootage=!!mediaKey;
 useEffect(()=>{
  if(preview&&!animate&&!onFootage)return;
  const canvas=ref.current!,back=background.current!;let raf=0,previous=0,visible=false,disposed=false,fontsReady=false;const start=performance.now();
  const text=sourceCue?.text??sample,words=text.trim().split(/\s+/),duration=sourceCue?sourceCue.end-sourceCue.start:words.length*.26+.6;
  const cue:Cue={id:'preview',start:0,end:duration,text,words:sourceCue?wordTimeline(sourceCue).map(w=>({...w,start:w.start-sourceCue.start,end:w.end-sourceCue.start})):words.map((word,i)=>({word,start:i*.26,end:i===words.length-1?duration:(i+1)*.26}))};
  const styling:Look={template,size:onFootage?72:132,position:onFootage?76:50,color:'#ffffff',bold:true,...look,...(!onFootage?{size:132,position:50}:{})};
  const paint=(time:number)=>{if(fontsReady)renderCaption(canvas.getContext('2d')!,canvas.width,canvas.height,cue,styling,time);};
  function poster(){const v=media?.current;if(!visible||!onFootage||!v||v.readyState<2)return;const ctx=back.getContext('2d')!,w=back.width,h=back.height;ctx.fillStyle=frame?.background??'#0b0b0d';ctx.fillRect(0,0,w,h);const fit=Math.min(w/v.videoWidth,h/v.videoHeight);ctx.save();ctx.translate(w/2+(frame?.x??0)*w/100,h/2+(frame?.y??0)*h/100);ctx.rotate((frame?.rotation??0)*Math.PI/180);ctx.scale((frame?.scale??100)*(frame?.width??100)/10000,(frame?.scale??100)*(frame?.height??100)/10000);ctx.drawImage(v,-v.videoWidth*fit/2,-v.videoHeight*fit/2,v.videoWidth*fit,v.videoHeight*fit);ctx.restore();}
  function resize(){if(!visible){canvas.width=back.width=canvas.height=back.height=1;return;}canvas.width=back.width=onFootage?Math.min(400,Math.round(canvas.clientWidth*2)):Math.round(canvas.clientWidth*2);canvas.height=back.height=onFootage?Math.round(canvas.width/ratio):Math.round(canvas.clientHeight*2);poster();if(!animate)paint(cue.end-.03);}
  const resizeObserver=new ResizeObserver(resize);resizeObserver.observe(canvas);resize();
  function tick(now:number){raf=0;if(disposed||!visible)return;if(now-previous>=33){previous=now;paint(((now-start)/1000)%(cue.end+.6));}raf=requestAnimationFrame(tick);}
  const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible){resize();refresh();if(fontsReady){if(animate&&!raf)raf=requestAnimationFrame(tick);else if(!animate)paint(cue.end-.03);}}else{cancelAnimationFrame(raf);raf=0;resize();}});observer.observe(canvas);
  const v=media?.current;let videoFrame=0,posterTimer:ReturnType<typeof setTimeout>;function refresh(){if(!visible)return;poster();clearTimeout(posterTimer);posterTimer=setTimeout(()=>{if(!disposed&&visible)poster();},120);if(v?.requestVideoFrameCallback){if(videoFrame)v.cancelVideoFrameCallback(videoFrame);videoFrame=v.requestVideoFrameCallback(()=>{videoFrame=0;if(!disposed)poster();});}else requestAnimationFrame(()=>{if(!disposed)poster();});}v?.addEventListener('loadeddata',refresh);v?.addEventListener('seeked',refresh);refresh();
  loadCaptionFonts([styling]).then(()=>{if(disposed)return;fontsReady=true;poster();if(animate&&visible&&!raf)raf=requestAnimationFrame(tick);else if(!animate)paint(cue.end-.03);});
  return()=>{disposed=true;clearTimeout(posterTimer);cancelAnimationFrame(raf);resizeObserver.disconnect();observer.disconnect();v?.removeEventListener('loadeddata',refresh);v?.removeEventListener('seeked',refresh);if(videoFrame)v?.cancelVideoFrameCallback(videoFrame);};
 },[template,sample,sourceCue,look?.size,look?.position,look?.color,look?.motion,look?.entry,look?.entryMs,look?.font,look?.accent,animate,preview,mediaKey,ratio,frame]);
 const still=!!preview&&!animate&&!onFootage;
 return <div className={'template-preview-surface '+(onFootage?'footage-preview':'')} style={onFootage?{aspectRatio:ratio}:undefined}>
  {still&&<img src={preview} loading="lazy" decoding="async" alt={template+' web preset preview'}/>}
  <canvas ref={background} className="template-footage"/>
  <canvas style={{visibility:still?'hidden':'visible'}} className="live-template-preview" ref={ref} aria-label={template+' animated preview'}/>
 </div>;
}
