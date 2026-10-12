import type {Cue,Look} from './captions';
import {presetFont} from './template-fonts';

// A timed keyword and a quiet, already-spoken context line. No guessed keywords.
export function renderKeyword(ctx:CanvasRenderingContext2D,width:number,height:number,cue:Cue,look:Look,time:number,anchors:{word:string;start:number;end:number}[]){
 let index=anchors.findIndex(w=>time>=w.start&&time<w.end);
 if(index<0&&cue.flow==='vad'&&time<cue.end)index=anchors.findLastIndex(w=>time>=w.start);
 if(index<0)return;
 const word=anchors[index],native=/[\u0900-\u0c7f]/.test(word.word),face=presetFont(look.template,false,look.font);
 const family=native?'"Noto Sans Telugu", "Noto Sans Devanagari", sans-serif':face?.family??'Arial, sans-serif';
 const size=look.size*Math.min(width,height)/1080*2.2;
 ctx.save();ctx.textAlign='center';ctx.textBaseline='middle';ctx.lineJoin='round';
 ctx.font=`${face?.weight??800} ${size}px ${family}`;
 const fit=Math.min(1,width*.88/Math.max(1,ctx.measureText(word.word).width));
 const y=Math.max(size*1.4,Math.min(height-size*1.4,height*look.position/100));
 ctx.translate(width/2,y);ctx.scale(fit,fit);
 const elapsed=time-word.start,progress=Math.min(1,elapsed/Math.min((look.entryMs??180)/1000,(word.end-word.start)*.5));
 if(look.motion!==false&&look.entry!=='None'){ctx.globalAlpha=progress;const travel=Math.pow(1-progress,3);if(look.entry==='Blur In')ctx.filter=`blur(${travel*size*.12}px)`;else if(look.entry==='Pop'){const scale=.7+.3*(1-travel);ctx.scale(scale,scale);}else if(look.entry==='Slide Right')ctx.translate(-travel*size*.5,0);else if(look.entry!=='By Letter')ctx.translate(0,travel*size*.22);}
 let drawn=word.word;if(look.entry==='By Letter'&&look.motion!==false){const letters=Array.from(new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(word.word),s=>s.segment);drawn=letters.slice(0,Math.ceil(progress*letters.length)).join('');}
 ctx.strokeStyle='rgba(0,0,0,.85)';ctx.lineWidth=size*.08;ctx.strokeText(drawn,0,0);
 ctx.fillStyle=look.accent??'#ffb83d';ctx.fillText(drawn,0,0);
 // Wrapping is measured with the same font used to draw; long Telugu phrases stay inside frame.
 ctx.globalAlpha=1;ctx.filter='none';ctx.font=`500 ${size*.29}px ${family}`;
 const spoken=anchors.slice(0,index).map(w=>w.word),lines:string[]=[];let line='';
 for(const text of spoken){const next=line?line+' '+text:text;if(line&&ctx.measureText(next).width>width*.82/fit){lines.push(line);line=text;}else line=next;}if(line)lines.push(line);
 ctx.fillStyle=look.color;ctx.lineWidth=size*.035;
 lines.slice(-2).forEach((text,i)=>{const yy=-size*(.75+(Math.min(2,lines.length)-1-i)*.39);ctx.strokeText(text,0,yy);ctx.fillText(text,0,yy);});ctx.restore();
}
