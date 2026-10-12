import {spawn} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const config=JSON.parse(readFileSync(new URL('../.local/config.json',import.meta.url),'utf8'));
const child=spawn(config.python_executable,[fileURLToPath(new URL('../local/service.py',import.meta.url))],{cwd:root,stdio:'inherit'});
process.on('SIGINT',()=>child.kill('SIGINT'));process.on('SIGTERM',()=>child.kill('SIGTERM'));
child.on('exit',code=>process.exit(code??0));child.on('error',error=>{console.error(error.message);process.exit(1);});
