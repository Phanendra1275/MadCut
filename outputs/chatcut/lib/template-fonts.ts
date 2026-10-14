// Original template fonts where available; explicitly named free substitutes otherwise.
import type {Look} from './captions';
type Font={family:string;weight:number};
const face=(family:string,weight:number):Font=>({family:'"'+family+'"',weight});
const poppins=face('MadCut Poppins',800),inter=face('MadCut Inter Black',900),satisfy=face('MadCut Satisfy',400);
const overrides:Record<string,Font>={Poppins:poppins,'Poppins Bold':face('MadCut Poppins',700),'Inter Black':inter,Satisfy:satisfy,Vivaldi:face('MadCut Vivaldi',400),Edwardian:face('MadCut Edwardian',400)};
export const captionFontOptions=['Auto','Arial','Script','Condensed','Poppins','Poppins Bold','Inter Black','Satisfy','Vivaldi','Edwardian'];
export function presetFont(template:string,script=false,override?:string):Font|undefined{
 if(override&&override!=='Auto')return overrides[override];
 if(template==='Butter Up')return satisfy;
 if(template==='Slide Collide'&&script)return face('MadCut Vivaldi',400);
 if(template==='Rock Solidance'&&script)return face('MadCut Edwardian',400);
 if(template==='Amber Script')return script?satisfy:poppins;
 if(['Keyword Spotlight','Word Wipe','Focus Glow','Neon Emerald','Lime Drop','Scarlet Punch','Coovetica Waving of','Zoom In','Impact Pop','Karaoke Glow','Editorial Two-Line'].includes(template))return poppins;
 if(template==='Clean Minimal')return face('Noto Sans Telugu',600);
 if(['Ocean Waves','Santhosham','Spinning Butter','cracked','Slide Collide'].includes(template))return face('MadCut Poppins',700);
 if(['Jitter Shine','Static Shine','Premium Text','Premium Text Without Animation'].includes(template))return inter;
 return undefined;
}
export const presetFontLabel=(template:string)=>({
 'Impact Pop':'Poppins ExtraBold','Clean Minimal':'Noto Sans / Arial SemiBold',
 'Karaoke Glow':'Poppins Bold Glow','Editorial Two-Line':'Poppins ExtraBold Two-Line',
 'Keyword Spotlight':'Poppins ExtraBold','Word Wipe':'Poppins ExtraBold','Focus Glow':'Poppins ExtraBold',
 'Premium Text':'Inter Black – SF UI substitute','Premium Text Without Animation':'Inter Black – SF UI substitute',
 'Jitter Shine':'Inter Black','Static Shine':'Inter Black','Coovetica Waving of':'Poppins ExtraBold','Zoom In':'Poppins ExtraBold',
 'Ocean Waves':'Poppins Bold','Butter Up':'Satisfy','Slide Collide':'Poppins + Vivaldi – Coolvetica substitute',
 'Rock Solidance':'Anton + Edwardian – Coolvetica Cond substitute','Santhosham':'Poppins Bold – Coolvetica substitute',
 'Spinning Butter':'Poppins Bold – Coolvetica substitute','cracked':'Poppins Bold – Coolvetica substitute',
 'Neon Emerald':'Poppins ExtraBold','Lime Drop':'Poppins ExtraBold','Scarlet Punch':'Poppins ExtraBold','Amber Script':'Poppins + Satisfy'
} as Record<string,string>)[template]??'Preset font';
const loaded=new Map<string,Promise<unknown>>();
export async function loadCaptionFonts(looks:Pick<Look,'template'|'font'>[]){
 const fonts:Font[]=[face('Noto Sans Telugu',800),face('Noto Sans Devanagari',800),face('MadCut Script',400),face('MadCut Condensed',400)];
 for(const look of looks)for(const script of [false,true]){const font=presetFont(look.template,script,look.font);if(font)fonts.push(font);}
 await Promise.all(fonts.map(font=>{const key=font.weight+' 48px '+font.family;if(!loaded.has(key))loaded.set(key,document.fonts.load(key));return loaded.get(key);}));
}
