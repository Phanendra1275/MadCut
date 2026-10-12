import type {Cue, Project} from './captions';

export type Frozen<T> = T extends object ? {readonly [K in keyof T]:Frozen<T[K]>} : T;
export type RecoveryAttempt={id:string;sourceId:string;status:string;reason:string;applied:false;requiresReview:true;gap:{start:number;end:number;reason:string};interval:{start:number;end:number};originalSegments:Cue[];candidates?:Cue[];gapWords?:Cue['words'];possibleNewWords?:Cue['words'];wordCountChanged?:boolean;timingBasis?:string;error?:string};
export type TranscriptEvidence=Frozen<{
 schemaVersion:1;
 raw:{schemaVersion:1;kind:'raw-asr';id:string;pipelineVersion:string;language:string;duration:number;text:string;speechEngine?:string|null;languageProbability?:number|null;segments:Cue[]};
 corrected:{id:string;kind:string;parentId:string;segments:Cue[]};
 recoveries:RecoveryAttempt[];
}>;

function freeze<T>(value:T):Frozen<T>{
 if(value&&typeof value==='object'&&!Object.isFrozen(value)){
  Object.values(value).forEach(freeze);Object.freeze(value);
 }
 return value as Frozen<T>;
}

export function preserveEvidence(evidence:TranscriptEvidence):TranscriptEvidence{
 // Clone first: editable tracks must never share references with frozen evidence.
 const copy=structuredClone(evidence);
 if(copy.schemaVersion!==1||copy.raw?.kind!=='raw-asr'||!/^[a-f0-9]{64}$/.test(copy.raw.id)||copy.corrected?.parentId!==copy.raw.id||!Array.isArray(copy.raw.segments)||!Array.isArray(copy.corrected.segments)||!Array.isArray(copy.recoveries))throw Error('Invalid transcript provenance.');
 const ids=new Set<string>();
 for(const c of copy.raw.segments){
  if(ids.has(c.id)||typeof c.text!=='string'||!Number.isFinite(c.start)||!Number.isFinite(c.end)||c.start<0||c.end<=c.start||c.end>copy.raw.duration+.1)throw Error('Invalid original ASR segment.');
  ids.add(c.id);
 }
 return freeze(copy);
}

export function withTranscriptEvidence(project:Project,evidence?:TranscriptEvidence):Project{
 return evidence?{...project,provenance:preserveEvidence(evidence)}:project;
}

export function compareCaption(project:Project,cue:Cue){
 const evidence=project.provenance;if(!evidence)return undefined;
 const ids=cue.sourceSegmentIds??[cue.id];
 return {raw:evidence.raw.segments.filter(c=>ids.includes(c.id)),
  corrected:evidence.corrected.segments.filter(c=>(c.sourceSegmentIds??[c.id]).some(id=>ids.includes(id))),
  current:cue};
}
