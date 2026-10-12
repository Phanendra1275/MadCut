import type {Project} from '../lib/captions';
import {compareCaption} from '../lib/transcript-provenance';

export function TranscriptComparison({project,selected,seek}:{project:Project;selected:string;seek:(seconds:number)=>void}){
 const evidence=project.provenance;if(!evidence)return null;
 const current=(project.tracks[project.language]??[]).find(c=>c.id===selected);
 const comparison=current?compareCaption(project,current):undefined;
 return <details className="flow-settings transcript-comparison">
  <summary>Original ASR and corrections</summary>
  <p className="hint">Original recognition is kept separately. Retry suggestions require listening; confidence is not a correctness guarantee.</p>
  <strong>Original ASR</strong>
  <p data-testid="raw-asr-text">{comparison?.raw.length?comparison.raw.map(c=>c.text).join(' '):evidence.raw.text}</p>
  <strong>Corrected native transcript</strong>
  <p data-testid="corrected-native-text">{(comparison?.corrected.length?comparison.corrected:evidence.corrected.segments).map(c=>c.text).join(' ')}</p>
  {current&&<><strong>Current {project.language} caption</strong><p data-testid="current-caption-text">{current.text}</p><p className="hint">ASR confidence: {typeof current.qualityScores?.transcriptionConfidence==='number'?current.qualityScores.transcriptionConfidence.toFixed(2):typeof current.confidence==='number'?current.confidence.toFixed(2):'Unknown'}. {current.timing==='estimated'?'Word timing is estimated; original anchors are retained.':''}</p></>}
  {evidence.recoveries.map(attempt=><div key={attempt.id}>
   <button className="text-button" onClick={()=>seek(attempt.gap.start)}>Review {attempt.gap.start.toFixed(2)}–{attempt.gap.end.toFixed(2)} s</button>
   <p className="hint">{attempt.status}: {attempt.reason}. Original captions retained.</p>
   {!!attempt.possibleNewWords?.length&&<p>Possible words, not applied: {attempt.possibleNewWords.map(w=>w.word).join(' ')}</p>}
  </div>)}
 </details>;
}
