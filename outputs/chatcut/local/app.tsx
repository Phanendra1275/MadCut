import {useEffect,useState} from 'react';
import Landing from '../app/landing';
import Projects from '../app/projects';
import Studio from '../app/page';
import type {Language,Template} from '../lib/captions';
export default function MadCut(){
 const [route,setRoute]=useState(location.hash.startsWith('#studio')?'studio':location.hash.startsWith('#projects')?'projects':'home');
 const [selection,setSelection]=useState<{language?:Language;template?:Template}>({});
 useEffect(()=>{const changed=()=>setRoute(location.hash.startsWith('#studio')?'studio':location.hash.startsWith('#projects')?'projects':'home');addEventListener('hashchange',changed);return()=>removeEventListener('hashchange',changed);},[]);
 function open(language?:Language,template?:Template){setSelection({language,template});location.hash='projects';setRoute('projects');scrollTo(0,0);}
 return route==='projects'?<Projects {...selection}/>:route==='studio'?<div className="mad-studio"><Studio initialLanguage={selection.language} initialTemplate={selection.template}/></div>:<Landing open={open}/>;
}
