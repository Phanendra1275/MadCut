import packMetadata from '../public/templates/catalog.json';
export const templateNames=['Minimal','Viral Reels','Karaoke','WhatsApp','Meme','Cinematic','Glow Script','Ink Flow','Script Duo','Typo Stairs','Kinetic Stack','Hyper Clean','Editorial','Trio Lockup','Pop Tag','Left Slide','Right Slide','Up Slide','Down Slide','Left Blur Slide','Right Blur Slide','Up Blur Slide','Down Blur Slide','Left Bounce Slide','Right Bounce Slide','Up Bounce Slide','Down Bounce Slide','Up Bounce Shrink','Down Bounce Shrink','Left Bounce Expand','Right Bounce Expand','Flex Bounce','Gradient Blue','Gradient Red','Gradient Red Orange','Jitter Shine','Static Shine','Zoom In','Premium Text','Premium Text Without Animation','Santhosham','Coovetica Waving of','Slide Collide','Spinning Butter','Butter Up','cracked','Ocean Waves','Rock Solidance','Neon Emerald','Lime Drop','Amber Script','Scarlet Punch','Keyword Spotlight','Word Wipe','Focus Glow'] as const;

export type Template=typeof templateNames[number];

const existingCatalog:{name:Template;label:string;sample:string;accent:string;defaults?:{entry:string;motion:boolean;color:string;size?:number;position?:number;font?:string}}[]=[

 {name:'Glow Script',label:'Glow & handwritten',sample:'glowing vibes',accent:'#77ff20'},

 {name:'Ink Flow',label:'Script in motion',sample:'felt Forever in a moment',accent:'#f5f0e9'},

 {name:'Script Duo',label:'Bold meets script',sample:'I’M BACK With',accent:'#f2ff8a'},

 {name:'Typo Stairs',label:'Stepped typography',sample:'i’m back with',accent:'#ffffff'},

 {name:'Kinetic Stack',label:'Condensed word stack',sample:'PURE KINETIC ENERGY',accent:'#dfff38'},

 {name:'Hyper Clean',label:'Electric emphasis',sample:'KEEP IT HYPER CLEAN',accent:'#38ff60'},

 {name:'Editorial',label:'Quiet word reveal',sample:'All the content CREATORS OUT THERE',accent:'#ffffff'},

 {name:'Trio Lockup',label:'Three-word lockup',sample:'i’m BACK with',accent:'#beff00',defaults:{entry:'Auto',motion:true,color:'#ffffff',font:'Auto'}},

 {name:'Pop Tag',label:'Active word tag',sample:'i’m back with',accent:'#ffb000'},

 {name:'Neon Emerald',label:'Video reference · neon two-line reveal',sample:'NUVVU EM CHESTHUNNAV',accent:'#69ff35',defaults:{entry:'Auto',motion:true,color:'#ffffff'}},
 {name:'Lime Drop',label:'Video reference · spring word drop',sample:'NUVVU EM CHESTHUNNAV',accent:'#c4ff39',defaults:{entry:'Auto',motion:true,color:'#ffffff'}},
 {name:'Amber Script',label:'Video reference · warm bold & script',sample:'Nuvvu em chesthunnav',accent:'#ffb43c',defaults:{entry:'Auto',motion:true,color:'#ffffff'}},
 {name:'Scarlet Punch',label:'Video reference · red & white punch',sample:'NUVVU EM CHESTHUNNAV',accent:'#ff3038',defaults:{entry:'Auto',motion:true,color:'#ffffff'}},

 {name:'Keyword Spotlight',label:'Timed keyword + spoken context',sample:'Nuvvu em chesthunnav?',accent:'#ffb83d',defaults:{entry:'Auto',motion:true,color:'#ffffff',size:72,position:72,font:'Auto'}},
 {name:'Word Wipe',label:'Active-word color wipe',sample:'Nuvvu em chesthunnav?',accent:'#c4ff39',defaults:{entry:'Auto',motion:true,color:'#ffffff',size:72,position:76,font:'Auto'}},
 {name:'Focus Glow',label:'Bright active word · quiet context',sample:'Nuvvu em chesthunnav?',accent:'#3bddff',defaults:{entry:'Auto',motion:true,color:'#ffffff',size:72,position:76,font:'Auto'}},
 {name:'Minimal',label:'Simple word reveal',sample:'Your words clearly',accent:'#ffffff'},

 {name:'Viral Reels',label:'Word pop',sample:'MAKE IT POP',accent:'#eaff6a'},

 {name:'Karaoke',label:'Speech highlights',sample:'Say it your way',accent:'#eaff6a'},

 {name:'WhatsApp',label:'Chat typing',sample:'Em bro ela unnav?',accent:'#a6efc1'},

 {name:'Meme',label:'Punchy emphasis',sample:'WAIT WHAT?!',accent:'#ffffff'},

 {name:'Cinematic',label:'Soft word fade',sample:'A moment to remember',accent:'#ffffff'},

 {name:'Left Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Right Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Up Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Down Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Left Blur Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Right Blur Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Up Blur Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Down Blur Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Left Bounce Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Right Bounce Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Up Bounce Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Down Bounce Slide',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Up Bounce Shrink',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Down Bounce Shrink',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Left Bounce Expand',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Right Bounce Expand',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Flex Bounce',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Gradient Blue',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#72c8ff'},

 {name:'Gradient Red',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ff645c'},

 {name:'Gradient Red Orange',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ff645c'},

 {name:'Jitter Shine',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Static Shine',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

 {name:'Zoom In',label:'From your pack · web recreation',sample:'Nuvvu eeroju vasthunnava?',accent:'#ffffff'},

];


export const packTemplates=packMetadata;
export type TemplateItem={name:Template;displayName?:string;id?:string;label:string;sample:string;accent:string;category?:string;preview?:string;file?:string;defaults?:{entry:string;motion:boolean;color:string;size?:number;position?:number;font?:string}};
export const templateCatalog:TemplateItem[]=[...existingCatalog.filter(t=>!t.label.includes('web recreation')), ...packMetadata.map(t=>({...t,name:t.webPreset as Template,displayName:t.name}))];
export const templateCategories=['All','Minimal','Bold','Dynamic','Viral','Karaoke','Cinematic','Social','Meme','Highlight','Clean','Original'];
export function categoryOf(t:TemplateItem){return t.category??({Minimal:'Minimal','Viral Reels':'Viral',Karaoke:'Karaoke',WhatsApp:'Social',Meme:'Meme',Cinematic:'Cinematic','Glow Script':'Highlight','Ink Flow':'Cinematic','Script Duo':'Bold','Typo Stairs':'Dynamic','Kinetic Stack':'Dynamic','Hyper Clean':'Clean',Editorial:'Clean','Trio Lockup':'Bold','Pop Tag':'Highlight','Neon Emerald':'Highlight','Lime Drop':'Dynamic','Amber Script':'Cinematic','Scarlet Punch':'Bold','Keyword Spotlight':'Bold','Word Wipe':'Highlight','Focus Glow':'Highlight'} as Record<string,string>)[t.name]??'Original';}
