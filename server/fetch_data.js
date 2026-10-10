import fs from 'fs';
import path from 'path';
import https from 'https';
import readline from 'readline';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DATA_DIR = path.join(__dirname, '../data');
const RAW_FILE = path.join(DATA_DIR, 'SambaTu_raw.txt');
const CLEAN_JSON = path.join(DATA_DIR, 'sambatu_clean.json');
const SAMBATU_URL = 'https://raw.githubusercontent.com/HideMeBr/SambaTu/main/SambaTu.txt';

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

console.log('=================================================');
console.log('🔒 SAMBATU ISOLATED INGESTION & SANITIZATION PIPE');
console.log('=================================================');
console.log('Iniciando download seguro de: ' + SAMBATU_URL);

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error('Falha no download. HTTP Status: ' + response.statusCode));
        return;
      }
      const totalBytes = parseInt(response.headers['content-length'] || '0', 10);
      let downloaded = 0;
      response.on('data', (chunk) => {
        downloaded += chunk.length;
        if (totalBytes > 0) {
          const pct = ((downloaded / totalBytes) * 100).toFixed(1);
          process.stdout.write('\rBaixando: ' + (downloaded / (1024 * 1024)).toFixed(2) + ' MB (' + pct + '%)');
        } else {
          process.stdout.write('\rBaixando: ' + (downloaded / (1024 * 1024)).toFixed(2) + ' MB');
        }
      });
      response.pipe(file);
      file.on('finish', () => {
        file.close(() => {
          console.log('\nDownload concluído com sucesso!');
          resolve();
        });
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

function sanitizePassword(rawLine) {
  if (!rawLine) return null;
  let cleaned = rawLine.replace(/[\x00-\x1F\x7F]/g, '').trim();
  if (/<script|javascript:|system\(|exec\(|drop table|union select/i.test(cleaned)) {
    return null;
  }
  if (cleaned.length === 0 || cleaned.length > 256) {
    return null;
  }
  return cleaned;
}

async function processData() {
  try {
    if (!fs.existsSync(RAW_FILE)) {
      await downloadFile(SAMBATU_URL, RAW_FILE);
    } else {
      console.log('Arquivo raw existente localizado em: ' + RAW_FILE);
    }

    console.log('Iniciando sanitização e indexação linha a linha em ambiente isolado...');
    
    const fileStream = fs.createReadStream(RAW_FILE, { encoding: 'utf8' });
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    const frequencyMap = new Map();
    let totalLines = 0;
    let validCount = 0;
    let rejectedCount = 0;

    for await (const line of rl) {
      totalLines++;
      const clean = sanitizePassword(line);
      if (!clean) {
        rejectedCount++;
        continue;
      }
      validCount++;
      const current = frequencyMap.get(clean) || 0;
      frequencyMap.set(clean, current + 1);

      if (totalLines % 200000 === 0) {
        console.log('Processadas ' + totalLines.toLocaleString('pt-BR') + ' linhas...');
      }
    }

    console.log('Sanitização concluída!');
    console.log('Total de linhas analisadas: ' + totalLines.toLocaleString('pt-BR'));
    console.log('Senhas válidas higienizadas: ' + validCount.toLocaleString('pt-BR'));
    console.log('Senhas únicas encontradas: ' + frequencyMap.size.toLocaleString('pt-BR'));
    console.log('Linhas maliciosas/inválidas descartadas: ' + rejectedCount.toLocaleString('pt-BR'));

    const kAnonMap = {};

    for (const [pwd, count] of frequencyMap.entries()) {
      const sha1 = crypto.createHash('sha1').update(pwd, 'utf8').digest('hex').toUpperCase();
      const prefix = sha1.substring(0, 5);
      const suffix = sha1.substring(5);

      if (!kAnonMap[prefix]) {
        kAnonMap[prefix] = [];
      }
      kAnonMap[prefix].push({
        suffix,
        pwd,
        count
      });
    }

    const outputData = {
      metadata: {
        dataset: 'HideMeBr/SambaTu',
        source: 'GitHub - Brazilian Password Database',
        totalLines,
        totalValid: validCount,
        totalUnique: frequencyMap.size,
        updatedAt: new Date().toISOString()
      },
      kAnonMap
    };

    console.log('Salvando base de dados higienizada e indexada em ' + CLEAN_JSON + '...');
    fs.writeFileSync(CLEAN_JSON, JSON.stringify(outputData), 'utf8');
    console.log('✨ Processo de coleta e isolamento SambaTu finalizado com SUCESSO!');

  } catch (err) {
    console.error('Erro no processamento da base SambaTu:', err);
    process.exit(1);
  }
}

processData();
