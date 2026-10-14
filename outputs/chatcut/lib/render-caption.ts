import type {Cue, Look} from './captions';
import {templateCatalog, getTemplateDefinition, resolveColor} from './templates';
import {presetFont} from './template-fonts';
import {renderKeyword} from './keyword-caption';

export function outputDimensions(width: number, height: number, aspect: string, resolution: number) {
  const ratio = aspect === 'original' ? width / height : aspect === '9:16' ? 9 / 16 : aspect === '1:1' ? 1 : aspect === '4:5' ? 4 / 5 : 16 / 9;
  return ratio >= 1 ? { width: Math.round(resolution * ratio / 2) * 2, height: resolution } : { width: resolution, height: Math.round(resolution / ratio / 2) * 2 };
}

export function wordTimeline(cue: Cue) {
  const words = cue.text.trim().split(/\s+/);
  let previous = cue.start;
  const valid = cue.words?.length === words.length && cue.words.every(w => {
    const okay = Number.isFinite(w.start) && Number.isFinite(w.end) && w.start >= previous - .001 && w.end > w.start && w.start >= cue.start - .001 && w.end <= cue.end + .001;
    previous = w.end;
    return okay;
  });
  return valid ? cue.words! : words.map((word, i) => ({
    word,
    start: cue.start + (cue.end - cue.start) * i / words.length,
    end: cue.start + (cue.end - cue.start) * (i + 1) / words.length
  }));
}

export const hasSpeechTiming = (cue: Cue) => !!cue.words && wordTimeline(cue) === cue.words;
export const motionEnabled = (look: Look) => look.motion !== false;
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const ease = (v: number) => 1 - Math.pow(1 - clamp(v), 3);
const native = (word: string) => /[\u0900-\u0c7f]/.test(word);

const scriptFamily = '"MadCut Script", Georgia, serif';
const bodyFamilyDefault = '"Noto Sans Telugu", "Noto Sans Devanagari", Arial, sans-serif';

type Glyph = { text: string; font: string; size: number; width: number; index: number; script: boolean };

export function renderCaption(ctx: CanvasRenderingContext2D, width: number, height: number, cue: Cue | undefined, look: Look, time: number) {
  look = { ...look, ...cue?.look };
  ctx.clearRect(0, 0, width, height);
  if (!cue || time < cue.start || time >= cue.end) return;

  if (cue.flow !== 'vad' && hasSpeechTiming(cue)) {
    const anchors = wordTimeline(cue), last = anchors.at(-1)!;
    if (time >= last.end + .15 || anchors.some((w, i) => i > 0 && w.start - anchors[i - 1].end > .45 && time >= anchors[i - 1].end + .15 && time < w.start)) return;
  }

  if (look.template === 'Keyword Spotlight' && look.motion !== false) {
    renderKeyword(ctx, width, height, cue, look, time, wordTimeline(cue));
    return;
  }

  ctx.save();
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'left';
  ctx.lineJoin = 'round';

  const bodyFamily = look.font === 'Script' ? scriptFamily : look.font === 'Condensed' ? '"MadCut Condensed", ' + bodyFamilyDefault : look.font === 'Arial' ? 'Arial, ' + bodyFamilyDefault : bodyFamilyDefault;
  const fromPack = templateCatalog.find(t => t.name === look.template)?.label.includes('web recreation');
  const style = look.template;
  const animated = motionEnabled(look);
  const anchors = wordTimeline(cue);
  const accent = look.accent ?? templateCatalog.find(t => t.name === style)?.accent ?? '#eaff6a';
  const def = getTemplateDefinition(style);

  const reference = ['Neon Emerald', 'Lime Drop', 'Amber Script', 'Scarlet Punch'].includes(style);

  // Container-relative responsive typography
  // Container scale based on 1080 reference dimension
  const containerScale = Math.min(width, height) / 1080;
  const base = look.size * containerScale;
  const factor = def?.typography?.sizeMultiplier ?? (
    ['Kinetic Stack', 'Script Duo', 'Glow Script', 'Trio Lockup'].includes(style) ? 1.85 :
    ['Meme', 'Rock Solidance'].includes(style) ? 1.5 :
    style === 'Cinematic' ? .85 : 1.2
  );
  const size = Math.max(1, base * factor);
  const raw = cue.text.trim().split(/\s+/);

  const glyphs: Glyph[] = raw.map((word, index) => {
    const isSecondHalf = index >= Math.ceil(raw.length / 2);
    const script = !native(word) && (
      (def?.typography?.scriptAlternate?.target === 'second_half' && isSecondHalf) ||
      (style === 'Glow Script' && index === raw.length - 1) ||
      (style === 'Ink Flow' && index === Math.min(1, raw.length - 1)) ||
      (style === 'Script Duo' && index === raw.length - 1) ||
      (style === 'Typo Stairs' && index % 3 === 2) ||
      (style === 'Butter Up') ||
      (style === 'Amber Script' && isSecondHalf) ||
      (['Slide Collide', 'Rock Solidance'].includes(style) && index === raw.length - 1)
    );

    const big = (def?.typography?.casing === 'uppercase') ||
      ['Kinetic Stack', 'Meme', 'Viral Reels', 'Script Duo', 'Rock Solidance', 'Neon Emerald', 'Lime Drop', 'Scarlet Punch'].includes(style) ||
      (style === 'Trio Lockup' && index % 3 === 1);

    const text = big && !script ? word.toLocaleUpperCase() : word;
    const scale = style === 'Ink Flow' ? (script ? 1.5 : .7) :
      style === 'Trio Lockup' ? (index % 3 === 1 ? 1.4 : .7) :
      style === 'Typo Stairs' ? (index % 3 === 1 ? 1.4 : 1) : 1;

    const specific = presetFont(style, script, look.font);
    const family = native(word) ? bodyFamilyDefault :
      specific?.family ?? (
        look.font && look.font !== 'Auto' ? bodyFamily :
        script ? (def?.typography?.scriptAlternate?.fontFamily ?? scriptFamily) :
        big && !native(word) && !reference ? '"MadCut Condensed", ' + bodyFamily :
        reference || fromPack ? 'Arial, ' + bodyFamily : bodyFamily
      );

    const weight = native(word) ? (look.bold ? '800' : '500') :
      specific?.weight ?? (
        script ? '400' :
        def?.typography?.fontWeight ?? (look.bold ? '800' : '500')
      );

    const font = `${weight} ${size * scale}px ${family}`;
    ctx.font = font;
    return { text, font, size: size * scale, width: ctx.measureText(text).width, index, script };
  });

  const stack = def?.layout?.mode === 'stacked' || ['Kinetic Stack', 'Trio Lockup', 'Typo Stairs', 'Ocean Waves'].includes(style);
  const splitHalf = def?.layout?.splitHalf || ['Slide Collide', 'Rock Solidance', 'Spinning Butter', 'Coovetica Waving of', 'Neon Emerald', 'Lime Drop', 'Amber Script', 'Scarlet Punch'].includes(style);

  const lines: Glyph[][] = [];
  let line: Glyph[] = [];
  for (const g of glyphs) {
    const lineWidth = line.reduce((n, w) => n + w.width + size * .22, 0) + g.width;
    const newLine = stack ||
      (style === 'Glow Script' && g.script) ||
      (style === 'Script Duo' && g.script) ||
      (style === 'Ink Flow' && (g.script || line.some(w => w.script))) ||
      (splitHalf && g.index === Math.ceil(raw.length / 2));

    if (line.length && (newLine || lineWidth > width * .86)) {
      lines.push(line);
      line = [];
    }
    line.push(g);
  }
  if (line.length) lines.push(line);

  const heights = lines.map(l => Math.max(...l.map(g => g.size)) * (l.some(g => g.script) ? 1.13 : 1.42));
  const total = heights.reduce((a, b) => a + b, 0);
  const widest = Math.max(...lines.map(l => l.reduce((a, g) => a + g.width, 0) + size * .22 * (l.length - 1)));

  // Bounding box fit to container
  const fit = Math.min(1, width * .88 / Math.max(1, widest), height * .75 / Math.max(1, total));
  const vPos = def?.layout?.verticalPositionPercent !== undefined && look.position === 82 ? def.layout.verticalPositionPercent : look.position;
  ctx.translate(width / 2, Math.max(total * fit / 2 + height * .02, Math.min(height - total * fit / 2 - height * .02, height * vPos / 100)));
  ctx.scale(fit, fit);
  let y = -total / 2;

  lines.forEach((l, row) => {
    const lineWidth = l.reduce((a, g) => a + g.width, 0) + size * .22 * (l.length - 1);
    let x = -lineWidth / 2;
    const centerY = y + heights[row] / 2;
    const visible = l.filter(g => !animated || time >= anchors[g.index].start);

    // Background box support (declarative + legacy WhatsApp/Minimal)
    const bgBox = def?.layout?.backgroundBox;
    if (visible.length && (bgBox || ['Minimal', 'WhatsApp'].includes(style))) {
      const boxColor = bgBox ? bgBox.color : (style === 'WhatsApp' ? 'rgba(13,80,53,.96)' : 'rgba(0,0,0,.65)');
      const padX = bgBox ? bgBox.paddingX : .35;
      const padY = bgBox ? bgBox.paddingY : .43;
      const rad = bgBox ? bgBox.borderRadius : .2;
      ctx.fillStyle = boxColor;
      ctx.beginPath();
      ctx.roundRect(-lineWidth / 2 - size * padX, centerY - heights[row] * padY, lineWidth + size * padX * 2, heights[row] * (padY * 2), size * rad);
      ctx.fill();
    }

    for (const g of l) {
      const a = anchors[g.index];
      const elapsed = time - a.start;
      const entry = look.entryMs ? look.entryMs / 1000 : Math.min(.18, Math.max(.045, (a.end - a.start) * .55));
      const progress = ease(elapsed / entry);
      const isActive = animated && time >= a.start && time < a.end;

      if (!animated || elapsed >= 0) {
        ctx.save();
        ctx.font = g.font;
        ctx.translate(x + g.width / 2, centerY);

        // Entry animations
        if (animated && look.entry && look.entry !== 'Auto') {
          ctx.globalAlpha = look.entry === 'None' ? 1 : progress;
          if (look.entry === 'Slide Up') ctx.translate(0, (1 - progress) * g.size * .65);
          if (look.entry === 'Slide Right') ctx.translate(-(1 - progress) * g.size * .65, 0);
          if (look.entry === 'Blur In') ctx.filter = `blur(${(1 - progress) * g.size * .15}px)`;
          if (look.entry === 'Pop') {
            const scale = .65 + .35 * progress;
            ctx.scale(scale, scale);
          }
        } else if (animated) {
          const direction = style.startsWith('Left') ? [-1, 0] : style.startsWith('Right') ? [1, 0] : style.startsWith('Up') ? [0, -1] : style.startsWith('Down') ? [0, 1] : [0, 0];
          const slide = style.includes('Slide') || style.includes('Shrink') || style.includes('Expand');
          if (slide) {
            const travel = style.includes('Bounce') ? Math.exp(-elapsed * 22) * Math.cos(elapsed * 35) : (1 - progress);
            ctx.translate(direction[0] * g.size * travel * .8, direction[1] * g.size * travel * .8);
          }
          if (style.includes('Shrink') || style === 'Zoom In') {
            const scale = 1 + (1 - progress) * .65;
            ctx.scale(scale, scale);
          }
          if (style.includes('Expand') || style === 'Flex Bounce') {
            const scale = style === 'Flex Bounce' ? 1 + .2 * Math.exp(-elapsed * 16) * Math.sin(elapsed * 32) : .6 + .4 * progress;
            ctx.scale(scale, scale);
          }
          if (style.includes('Blur')) ctx.filter = `blur(${(1 - progress) * g.size * .12}px)`;
          if (style === 'Jitter Shine') ctx.translate(Math.sin(elapsed * 72) * g.size * .05 * (1 - progress), Math.cos(elapsed * 51) * g.size * .04 * (1 - progress));
          ctx.globalAlpha = style === 'Karaoke' ? 1 : progress;

          // Word active pop
          if (['Viral Reels', 'Meme', 'Pop Tag', 'Kinetic Stack'].includes(style)) {
            const pop = 1 + .12 * Math.sin(clamp(elapsed / entry) * Math.PI);
            ctx.scale(pop, pop);
          }
          if (['Ink Flow', 'Typo Stairs', 'Editorial', 'Trio Lockup'].includes(style)) ctx.translate(0, (1 - progress) * g.size * .35);
          if (style === 'Script Duo' && g.script) ctx.rotate((1 - progress) * -.12);
          if (style === 'Slide Collide') ctx.translate((g.script ? 1 : -1) * (1 - progress) * g.size, 0);
          if (style === 'Spinning Butter') ctx.rotate((1 - progress) * (g.index % 2 ? -1 : 1) * Math.PI * .65);
          if (style === 'Lime Drop') {
            const spring = 1 - Math.exp(-elapsed * 18) * Math.cos(elapsed * 25);
            ctx.translate(0, (1 - spring) * g.size * .55);
            const scale = .85 + .15 * spring;
            ctx.scale(scale, scale);
          }
          if (['Neon Emerald', 'Amber Script', 'Scarlet Punch'].includes(style)) {
            ctx.translate(0, (1 - progress) * g.size * .25);
            const scale = .94 + .06 * progress;
            ctx.scale(scale, scale);
          }
          if (style === 'Butter Up') ctx.translate(0, Math.sin(elapsed * 22) * Math.exp(-elapsed * 12) * g.size * .35);
          if (['Ocean Waves', 'Coovetica Waving of'].includes(style)) ctx.translate(0, Math.sin(elapsed * 5 + g.index) * g.size * .09);
        }

        // Color computation
        let color = resolveColor(def?.colors?.base, look.color, accent, look.color);
        if (style === 'Glow Script' && !g.script) color = accent;
        if (style === 'Hyper Clean' && g.index > Math.floor(raw.length / 3) - 1) color = accent;
        if (style === 'Kinetic Stack' && g.index % 3 === 1) color = accent;
        if (style === 'Trio Lockup' && g.index % 3 === 1) color = accent;
        if (style === 'Script Duo') color = g.script ? '#ff3034' : accent;
        if (style === 'Karaoke' && isActive) color = accent;
        if (style === 'Coovetica Waving of' && g.index >= Math.ceil(raw.length / 2)) color = '#ff2424';
        if (style === 'Spinning Butter' && g.index >= Math.ceil(raw.length / 2)) color = '#ce25ee';
        if (style === 'Ocean Waves' || style === 'Zoom In') color = '#00e2ff';
        if (style === 'Slide Collide' && !g.script) color = '#ff8c00';
        if (style === 'Rock Solidance' && g.script) color = '#63ce08';
        if (reference) {
          color = g.index < Math.ceil(raw.length / 2) ? accent : look.color;
          if (style === 'Lime Drop') color = g.index < Math.ceil(raw.length / 2) ? look.color : accent;
        }

        // Active word styling
        if (def?.activeWord && isActive) {
          if (def.activeWord.color) {
            color = resolveColor(def.activeWord.color, look.color, accent, accent);
          }
          if (def.activeWord.glowBlur) {
            ctx.shadowColor = resolveColor(def.activeWord.glowColor, look.color, accent, accent);
            ctx.shadowBlur = g.size * def.activeWord.glowBlur;
          }
          if (def.activeWord.scale && !['Viral Reels', 'Meme', 'Pop Tag', 'Kinetic Stack'].includes(style)) {
            ctx.scale(def.activeWord.scale, def.activeWord.scale);
          }
        }

        if (style === 'Focus Glow') {
          color = isActive ? accent : look.color;
          ctx.globalAlpha *= isActive ? 1 : .65;
          ctx.shadowColor = isActive ? accent : 'transparent';
          ctx.shadowBlur = isActive ? g.size * .32 : 0;
        }

        if (style === 'Word Wipe' && isActive) {
          ctx.save();
          ctx.beginPath();
          ctx.rect(-g.width / 2 - g.size * .16, -g.size * .62, (g.width + g.size * .32) * progress, g.size * 1.24);
          ctx.clip();
          ctx.fillStyle = accent;
          ctx.fillRect(-g.width / 2 - g.size * .16, -g.size * .62, (g.width + g.size * .32), g.size * 1.24);
          ctx.restore();
        }

        if ((style === 'Pop Tag' || def?.activeWord?.backgroundColor) && isActive) {
          const pillBg = resolveColor(def?.activeWord?.backgroundColor, look.color, accent, accent);
          ctx.fillStyle = pillBg;
          ctx.beginPath();
          ctx.roundRect(-g.width / 2 - g.size * .2, -g.size * .68, g.width + g.size * .4, g.size * 1.4, g.size * .23);
          ctx.fill();
          color = def?.activeWord?.color ? resolveColor(def.activeWord.color, look.color, accent, '#0a0a0a') : '#0a0a0a';
        }

        // Declarative shadow & offset
        if (def?.effects?.shadowOffset) {
          ctx.shadowOffsetX = def.effects.shadowOffset.x * containerScale;
          ctx.shadowOffsetY = def.effects.shadowOffset.y * containerScale;
        }
        if (def?.effects?.shadowBlur && (!isActive || !def?.activeWord?.glowBlur)) {
          ctx.shadowColor = resolveColor(def.effects.shadowColor, look.color, accent, 'rgba(0,0,0,.6)');
          ctx.shadowBlur = g.size * def.effects.shadowBlur;
        }
        if (isActive && def?.activeWord?.glowBlur) {
          ctx.shadowOffsetX = 0;
          ctx.shadowOffsetY = 0;
        }

        if (reference) {
          ctx.shadowColor = color;
          ctx.shadowBlur = g.size * (isActive ? .18 : .07);
        }
        if (['Glow Script', 'Hyper Clean', 'Santhosham', 'Spinning Butter', 'Ocean Waves', 'Rock Solidance', 'Zoom In'].includes(style)) {
          ctx.shadowColor = color;
          ctx.shadowBlur = g.size * (isActive ? .24 : .12);
        }

        let drawn = g.text;
        if (animated && look.entry === 'By Letter') {
          const Segmenter = (Intl as any).Segmenter;
          const letters = Segmenter ? Array.from(new Segmenter(undefined, { granularity: 'grapheme' }).segment(g.text), (s: any) => s.segment) : Array.from(g.text);
          drawn = letters.slice(0, Math.ceil(progress * letters.length)).join('');
        }

        // Outline drawing (declarative + legacy)
        const outlineRatio = def?.effects?.outlineWidth ?? (reference || ['Karaoke', 'Meme', 'Viral Reels'].includes(style) ? .1 : 0);
        if (outlineRatio > 0) {
          ctx.strokeStyle = def?.effects?.outlineColor ?? 'rgba(0,0,0,.9)';
          ctx.lineWidth = g.size * outlineRatio;
          ctx.strokeText(drawn, -g.width / 2, 0);
        }

        ctx.fillStyle = color;

        if (style.startsWith('Gradient')) {
          const gradient = ctx.createLinearGradient(0, -g.size / 2, 0, g.size / 2);
          gradient.addColorStop(0, style === 'Gradient Blue' ? '#e7fbff' : '#fff3bf');
          gradient.addColorStop(.45, style === 'Gradient Blue' ? '#5bbdff' : '#ff883d');
          gradient.addColorStop(1, style === 'Gradient Blue' ? '#2057e8' : style === 'Gradient Red Orange' ? '#e03004' : '#ee1c49');
          ctx.fillStyle = gradient;
          ctx.shadowColor = accent;
          ctx.shadowBlur = g.size * .12;
        }

        if (['Jitter Shine', 'Static Shine'].includes(style)) {
          const phase = animated ? (elapsed % 1.8) / 1.8 : .5;
          const gradient = ctx.createLinearGradient(-g.width / 2, 0, g.width / 2, 0);
          gradient.addColorStop(0, '#df6700');
          gradient.addColorStop(Math.max(.001, phase - .12), '#ff9000');
          gradient.addColorStop(Math.max(.002, phase), '#fff0b0');
          gradient.addColorStop(Math.min(.999, phase + .12), '#ff9000');
          gradient.addColorStop(1, '#df6700');
          ctx.fillStyle = gradient;
        }

        ctx.fillText(drawn, -g.width / 2, 0);

        if (style === 'Word Wipe' && isActive) {
          ctx.save();
          ctx.beginPath();
          ctx.rect(-g.width / 2 - g.size * .16, -g.size * .62, (g.width + g.size * .32) * progress, g.size * 1.24);
          ctx.clip();
          ctx.fillStyle = '#111111';
          ctx.fillText(drawn, -g.width / 2, 0);
          ctx.restore();
        }

        if (style === 'cracked') {
          ctx.strokeStyle = '#ff3838';
          ctx.shadowColor = '#ff3838';
          ctx.shadowBlur = g.size * .15;
          ctx.lineWidth = g.size * .07;
          ctx.beginPath();
          ctx.moveTo(-g.width / 2, -g.size * .05);
          ctx.lineTo(0, g.size * .05);
          ctx.lineTo(g.width / 2, -g.size * .18);
          ctx.stroke();
        }

        ctx.restore();
      }
      x += g.width + size * .22;
    }
    y += heights[row];
  });
  ctx.restore();
}
