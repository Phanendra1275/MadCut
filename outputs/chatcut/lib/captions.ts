import {templateNames,type Template} from './templates';
import {preserveEvidence,type TranscriptEvidence} from './transcript-provenance';
export type {Template} from './templates';
export const languages=['Tenglish','Telugu','English','Hindi','Hinglish'] as const;
export type Language=typeof languages[number];
export type CaptionSettings={maxWords:number;maxCharsPerLine:number;maxLines:number;maxDuration:number;minDuration:number;maxGapMs:number;pauseMs:number};
export const defaultCaptionSettings:CaptionSettings={maxWords:6,maxCharsPerLine:36,maxLines:2,maxDuration:4,minDuration:.6,maxGapMs:250,pauseMs:600};

export type CaptionGroupingPreset='single'|'two-word'|'short-phrase'|'natural';
export interface GroupingPresetConfig{name:CaptionGroupingPreset;maxWords:number;label:string;description:string;settings:Partial<CaptionSettings>;}
export const captionGroupingPresets:Record<CaptionGroupingPreset,GroupingPresetConfig>={
 single:{name:'single',maxWords:1,label:'1 Word',description:'1 word per caption for high-energy reels',settings:{maxWords:1,maxLines:1,maxDuration:2.0,minDuration:0.2,maxCharsPerLine:20}},
 'two-word':{name:'two-word',maxWords:2,label:'2 Words',description:'2 words per caption for punchy dialogue rhythm',settings:{maxWords:2,maxLines:1,maxDuration:2.5,minDuration:0.2,maxCharsPerLine:24}},
 'short-phrase':{name:'short-phrase',maxWords:4,label:'Short (3-4)',description:'3–4 words per line for balanced mobile reading',settings:{maxWords:4,maxLines:2,maxDuration:3.5,minDuration:0.4,maxCharsPerLine:32}},
 natural:{name:'natural',maxWords:6,label:'Natural (5-7)',description:'Natural speech phrasing respecting pauses and punctuation',settings:{maxWords:6,maxLines:2,maxDuration:4.5,minDuration:0.6,maxCharsPerLine:38}}
};

export type WordAnchor={word:string;start:number;end:number;confidence?:number|null;timing?:'estimated'};
export type CaptionEditVersion={id:string;kind:'before-user-edit'|'user-edit';text:string;start:number;end:number;words?:WordAnchor[];timing?:Cue['timing']};
export type Cue={sourceSegmentIds?:string[];sourceWords?:WordAnchor[];sourceTiming?:{start:number;end:number};recoveryAttemptId?:string;editVersions?:CaptionEditVersion[];flow?:'vad';speechEnd?:number;gapRepair?:string;qualityScores?:{transcriptionConfidence?:number|null;languageConfidence?:number|null;correctionConfidence?:number|null;tenglishConfidence?:number|null};reviewReasons?:string[];recognitionQuality?:{averageLogProbability?:number;compressionRatio?:number;noSpeechProbability?:number};acousticRetry?:string;delayMs?:number;look?:Partial<Look>;confidence?:number|null;needsReview?:boolean;rawText?:string;correction?:string;segment?:{start:number;end:number};id:string;start:number;end:number;text:string;timing?:'mapped'|'edited'|'estimated';words?:WordAnchor[]};
export const entryAnimations=['Auto','Slide Up','Blur In','Slide Right','By Letter','Pop','None'] as const;
export type Look={entry?:typeof entryAnimations[number];entryMs?:number;font?:string;accent?:string;template:Template;size:number;color:string;position:number;bold:boolean;motion?:boolean};
export type Frame={scale:number;width:number;height:number;x:number;y:number;rotation:number;background:string};
export const defaultFrame:Frame={scale:100,width:100,height:100,x:0,y:0,rotation:0,background:'#0b0b0d'};
export type Project={provenance?:TranscriptEvidence;captionSettings?:CaptionSettings;timelineQuality?:{wordCount:number;captionCount:number;gapRepairs:number;uncoveredSpeech:{start:number;end:number;reason:string}[]};speechSpans?:{start:number;end:number}[];originalTracks?:Partial<Record<Language,Cue[]>>;tenglishMode?:'Natural'|'WhatsApp'|'Formal';emojis?:boolean;projectId?:string;frame?:Frame;captionDelay?:Partial<Record<Language,number>>;version:1;name:string;language:Language;tone:string;sourceLanguage:string;original:Cue[];tracks:Partial<Record<Language,Cue[]>>;look:Look;aspect:string;duration:number};
export const defaultLook:Look={template:'Minimal',size:48,color:'#ffffff',position:82,bold:true};
export function emptyProject():Project{return {projectId:crypto.randomUUID(),version:1,name:'Untitled video',language:'Tenglish',tone:'Accurate',sourceLanguage:'auto',tenglishMode:'Natural',emojis:false,original:[],tracks:{},look:{...defaultLook},aspect:'original',duration:0};}
export function validateCues(cues:Cue[],duration?:number){if(!Array.isArray(cues)||cues.length>500)throw new Error('Use up to 500 captions per project.');let last=0;for(const c of cues){if(!c||typeof c.text!=='string'||!c.text.trim()||c.text.length>1000||!Number.isFinite(c.start)||!Number.isFinite(c.end)||c.start<0||c.end<=c.start||c.start<last-.001||(duration&&c.end>duration+.1))throw new Error('Captions need text and increasing, non-overlapping times within the video.');if(c.words){let end=c.start;if(c.words.length!==c.text.trim().split(/\s+/).length||c.words.some(w=>{const invalid=!Number.isFinite(w.start)||!Number.isFinite(w.end)||w.end<=w.start||w.start<end-.001||w.start<c.start-.001||w.end>c.end+.001;end=w.end;return invalid;}))throw new Error('Word timestamps must be ordered inside their caption.');}last=c.end;}return cues;}
export function validateProject(raw:unknown):Project{const p=raw as Project;if(!p||p.version!==1||typeof p.name!=='string'||!languages.includes(p.language)||!p.tracks||!p.look||!Number.isFinite(p.duration)||p.duration<0||!['original','9:16','16:9','1:1','4:5'].includes(p.aspect)||!templateNames.includes(p.look.template)||!Number.isFinite(p.look.size)||p.look.size<20||p.look.size>100||!/^#[0-9a-f]{6}$/i.test(p.look.color)||!Number.isFinite(p.look.position)||p.look.position<10||p.look.position>90)throw new Error('This is not a valid MadCut project.');if(p.frame&&(!/^#[0-9a-f]{6}$/i.test(p.frame.background)||!Object.entries(p.frame).filter(([k])=>k!=='background').every(([,v])=>typeof v==='number'&&Number.isFinite(v))||p.frame.scale<10||p.frame.scale>300||p.frame.width<10||p.frame.width>200||p.frame.height<10||p.frame.height>200||Math.abs(p.frame.x)>100||Math.abs(p.frame.y)>100||Math.abs(p.frame.rotation)>180))throw new Error('Invalid video transform.');if(p.captionSettings){const bounds:Record<keyof CaptionSettings,[number,number]>={maxWords:[1,12],maxCharsPerLine:[20,48],maxLines:[1,2],maxDuration:[1,6],minDuration:[.2,1.5],maxGapMs:[0,250],pauseMs:[400,1500]};for(const [key,[a,b]] of Object.entries(bounds)){const value=p.captionSettings[key as keyof CaptionSettings];if(!Number.isFinite(value)||value<a||value>b)throw Error('Invalid caption settings.');}if(p.captionSettings.minDuration>=p.captionSettings.maxDuration)throw Error('Minimum caption duration must be shorter than maximum.');}if(p.provenance)p.provenance=preserveEvidence(p.provenance);validateCues(p.original,p.duration);Object.entries(p.tracks).forEach(([lang,cues])=>{if(!languages.includes(lang as Language))throw new Error('Unknown caption language.');validateCues(cues!,p.duration);});return p;}
export function timestamp(s:number,delimiter=','){const ms=Math.round(Math.max(0,s)*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')}${delimiter}${String(ms%1000).padStart(3,'0')}`;}
export function clock(s:number){return timestamp(s,'.').slice(3,8);}
export function exportSubtitle(cues:Cue[],format:string,look:Look=defaultLook){validateCues(cues);if(format==='vtt')return 'WEBVTT\n\n'+cues.map(c=>`${timestamp(c.start,'.')} --> ${timestamp(c.end,'.')}\n${c.text.replace(/-->/g,' ')}\n`).join('\n');if(format==='ass'){const t=(s:number)=>timestamp(s,'.').slice(1,-1);const color='&H00'+look.color.slice(5,7)+look.color.slice(3,5)+look.color.slice(1,3);const text=(s:string)=>s.replace(/\\/g,'\\').replace(/[{}]/g,'').replace(/\n/g,'\\N');return `[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Noto Sans,${look.size},${color},&H0000FFFF,&H00101010,&H80000000,${look.bold?-1:0},0,0,0,100,100,0,0,1,2,1,2,60,60,${Math.round(1080*(1-look.position/100))},1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n`+cues.map(c=>`Dialogue: 0,${t(c.start)},${t(c.end)},Default,,0,0,0,,${text(c.text)}`).join('\n');}return cues.map((c,i)=>`${i+1}\n${timestamp(c.start)} --> ${timestamp(c.end)}\n${c.text}\n`).join('\n');}
export function importSubtitle(text:string):Cue[]{const seconds=(v:string)=>{const a=v.trim().replace(',','.').split(':').map(Number);return a.length===3?a[0]*3600+a[1]*60+a[2]:a[0]*60+a[1];};const cues:Cue[]=[];for(const block of text.replace(/\r/g,'').split(/\n\s*\n/)){const lines=block.split('\n'),i=lines.findIndex(l=>l.includes('-->'));if(i<0)continue;const pair=lines[i].split('-->'),start=seconds(pair[0]),end=seconds(pair[1].trim().split(/\s/)[0]);const body=lines.slice(i+1).join('\n').replace(/<[^>]*>/g,'').trim();if(body)cues.push({id:crypto.randomUUID(),start,end,text:body});}if(!cues.length)throw new Error('No captions found. Import an SRT or VTT file.');return validateCues(cues);}
export function download(data:Blob|string,name:string,type='text/plain;charset=utf-8'){const blob=typeof data==='string'?new Blob([data],{type}):data,url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);}
export function groupCaptionWords(cues:Cue[],maxWords=6,onlyAligned=false,settings:Partial<CaptionSettings>={}):Cue[]{
 const cfg={...defaultCaptionSettings,...settings,maxWords},result:Cue[]=[];
 for(const c of cues){
  const parts=c.text.trim().split(/\s+/),aligned=c.words?.length===parts.length&&c.words.every((w,i)=>Number.isFinite(w.start)&&Number.isFinite(w.end)&&w.end>w.start&&w.start>=c.start-.001&&w.end<=c.end+.001&&(!i||w.start>=c.words![i-1].end-.001));
  // Segmentation cannot derive acoustic word timings from sentence bounds.
  if(!aligned){result.push(c);continue;}
  const words=c.words!;let first=0;
  while(first<parts.length){let end=first+1,lastBoundary=0;
   while(end<parts.length){const duration=words[end].end-words[first].start,gap=words[end].start-words[end-1].end;
    if(gap>=cfg.pauseMs/1000)break;
    if(end-first+1>cfg.maxWords||parts.slice(first,end+1).join(' ').length>cfg.maxCharsPerLine*cfg.maxLines||duration>cfg.maxDuration){if(lastBoundary&&words[lastBoundary-1].end-words[first].start>=cfg.minDuration)end=lastBoundary;break;}
    if(/[.!?,;:]$/.test(parts[end-1])){lastBoundary=end;if(words[end-1].end-words[first].start>=cfg.minDuration&&/[.!?]$/.test(parts[end-1]))break;}
    end++;
   }
   const group=words.slice(first,end),start=group[0].start,finish=end===parts.length?c.end:group.at(-1)!.end;
   result.push({...c,id:c.id+'-group-'+first,text:parts.slice(first,end).join(' '),start,end:finish,words:group});first=end;
  }
 }
 return validateCues(result);
}
export function bridgeCaptionGaps(cues:Cue[],spans:{start:number;end:number}[]=[],maxGapMs=250){
 const result=cues.map(c=>({...c}));for(let i=0;i<result.length-1;i++){const a=result[i],b=result[i+1],gap=b.start-a.end;if(gap>0&&gap<=maxGapMs/1000+.0001&&spans.some(s=>s.start<=a.end+.02&&s.end>=b.start-.02)){a.speechEnd=a.speechEnd??a.end;a.end=b.start;a.flow='vad';a.gapRepair='vad-short-hold';}}return validateCues(result);
}
export function regroupCues(cues:Cue[],baseCues?:Cue[],preset:CaptionGroupingPreset='natural',customSettings?:Partial<CaptionSettings>,speechSpans?:{start:number;end:number}[]):Cue[]{
 const source=baseCues&&baseCues.length?baseCues:cues;
 const config:CaptionSettings={...defaultCaptionSettings,...captionGroupingPresets[preset]?.settings,...customSettings};
 const grouped=groupCaptionWords(source,config.maxWords,false,config);
 return speechSpans&&speechSpans.length?bridgeCaptionGaps(grouped,speechSpans,config.maxGapMs??250):grouped;
}
export function editCaption(c:Cue,patch:Partial<Cue>):Cue{
 const next={...c,...patch};const changed=(patch.text!==undefined&&patch.text!==c.text)||(patch.start!==undefined&&patch.start!==c.start)||(patch.end!==undefined&&patch.end!==c.end);
 if(!changed)return next;
 next.sourceWords=structuredClone(c.sourceWords??c.words??[]);
 next.sourceTiming={...(c.sourceTiming??{start:c.start,end:c.end})};
 if(patch.text!==undefined){
  const words=patch.text.trim().split(/\s+/),old=c.text.trim().split(/\s+/),normalize=(s:string)=>s.normalize('NFC').replace(/\p{P}/gu,'');
  const same=old.length===words.length&&old.every((w,i)=>normalize(w)===normalize(words[i]));
  next.words=c.words?.length===words.length?c.words.map((w,i)=>{const {confidence,...anchor}=w;return {...anchor,word:words[i],...(same&&confidence!==undefined?{confidence}:{})};}):undefined;
  if(!same){next.timing='estimated';next.needsReview=true;next.reviewReasons=[...new Set([...(next.reviewReasons??[]),'edited-word-timing'])];}
 }
 if(patch.start!==undefined||patch.end!==undefined){
  if(!Number.isFinite(next.start)||!Number.isFinite(next.end)||next.start<0||next.end<=next.start)throw new Error('Caption end must be after its start.');
  const scale=(next.end-next.start)/(c.end-c.start);
  next.words=next.words?.map(({confidence,...w})=>({...w,start:next.start+(w.start-c.start)*scale,end:next.start+(w.end-c.start)*scale,timing:'estimated'}));next.timing='estimated';next.needsReview=true;
 }
 const version=(cue:Cue,kind:CaptionEditVersion['kind']):CaptionEditVersion=>({id:crypto.randomUUID(),kind,text:cue.text,start:cue.start,end:cue.end,words:structuredClone(cue.words),timing:cue.timing});
 const previous=c.editVersions??[version(c,'before-user-edit')];
 // Keep the initial editable version and 39 recent changes; raw ASR is separate.
 next.editVersions=[previous[0],...previous.slice(1).slice(-38),version(next,'user-edit')];
 return next;
}

export function retimeCaptions(cues:Cue[],keep:number[][]):Cue[]{const result:Cue[]=[];let offset=0;for(const [a,b] of keep){for(const c of cues){const start=Math.max(a,c.start),end=Math.min(b,c.end);if(end<=start)continue;const words=c.words?.filter(w=>(w.start+w.end)/2>=a&&(w.start+w.end)/2<b).map(w=>({...w,start:offset+Math.max(a,w.start)-a,end:offset+Math.min(b,w.end)-a})).filter(w=>w.end>w.start);if(c.words&&!words?.length)continue;if(!c.words&&!(c.start+(c.end-c.start)/2>=a&&c.start+(c.end-c.start)/2<b))continue;result.push({...c,id:c.id+'-cut-'+result.length,start:offset+start-a,end:offset+end-a,text:words?.map(w=>w.word).join(' ')??c.text,words,needsReview:c.needsReview||!words});}offset+=b-a;}return validateCues(result,offset);}
