import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const dataPath = path.join(__dirname, '../data/sambatu_clean.json');
let pwnedDatabase = {};
let totalValidCount = 2140469;
let totalUniqueCount = 2140282;

console.log('[SERVER] Carregando base SambaTu higienizada de:', dataPath);
try {
  if (fs.existsSync(dataPath)) {
    const rawData = fs.readFileSync(dataPath, 'utf-8');
    const parsed = JSON.parse(rawData);
    pwnedDatabase = parsed.kAnonMap || parsed;
    
    if (parsed.metadata) {
      if (parsed.metadata.totalValid) totalValidCount = parsed.metadata.totalValid;
      if (parsed.metadata.totalUnique) totalUniqueCount = parsed.metadata.totalUnique;
    }

    let calculatedUnique = 0;
    for (const prefix in pwnedDatabase) {
      calculatedUnique += pwnedDatabase[prefix].length;
    }
    if (calculatedUnique > 0) totalUniqueCount = calculatedUnique;

    console.log('[SERVER] Base SambaTu carregada com sucesso! Hashes únicos indexados:', totalUniqueCount);
  } else {
    console.warn('[SERVER] Arquivo data/sambatu_clean.json não encontrado.');
  }
} catch (err) {
  console.error('[SERVER] Erro ao carregar a base de dados:', err);
}

app.get('/api/stats', (req, res) => {
  res.json({
    totalValid: totalValidCount,
    totalUnique: totalUniqueCount,
    indexedPrefixes: Object.keys(pwnedDatabase).length,
    status: 'ONLINE'
  });
});

app.get('/api/range/:prefix', (req, res) => {
  const prefix = (req.params.prefix || '').toUpperCase();
  if (!prefix || prefix.length !== 5) {
    return res.status(400).json({ error: 'O prefixo SHA-1 deve ter exatamente 5 caracteres hexadecimais.' });
  }

  const hashes = pwnedDatabase[prefix] || [];
  res.json({
    prefix,
    hashes
  });
});

app.post('/api/check', (req, res) => {
  const { password } = req.body;
  if (!password) {
    return res.status(400).json({ error: 'Senha não fornecida.' });
  }

  const sha1 = crypto.createHash('sha1').update(password).digest('hex').toUpperCase();
  const prefix = sha1.substring(0, 5);
  const suffix = sha1.substring(5);

  const bucket = pwnedDatabase[prefix] || [];
  const match = bucket.find(item => item.suffix === suffix);

  if (match) {
    return res.json({
      pwned: true,
      count: match.count,
      sha1: sha1,
      leakedPassword: match.pwd || password,
      riskLevel: match.count >= 10 ? 'CRÍTICO' : match.count >= 3 ? 'ALTO' : 'MÉDIO'
    });
  } else {
    return res.json({
      pwned: false,
      count: 0,
      sha1: sha1,
      leakedPassword: null,
      riskLevel: 'SEGURO'
    });
  }
});

app.post('/api/check-user', (req, res) => {
  const { username } = req.body;
  if (!username || !username.trim()) {
    return res.status(400).json({ error: 'Usuário/E-mail não fornecido.' });
  }

  const target = username.trim().toLowerCase();
  const sha1 = crypto.createHash('sha1').update(target).digest('hex').toUpperCase();
  const prefix = sha1.substring(0, 5);
  const suffix = sha1.substring(5);

  const bucket = pwnedDatabase[prefix] || [];
  const match = bucket.find(item => item.suffix === suffix);

  if (match) {
    return res.json({
      pwned: true,
      username: username,
      count: match.count,
      riskLevel: match.count >= 10 ? 'CRÍTICO' : match.count >= 3 ? 'ALTO' : 'MÉDIO'
    });
  } else {
    return res.json({
      pwned: false,
      username: username,
      count: 0,
      riskLevel: 'SEGURO'
    });
  }
});

app.listen(PORT, () => {
  console.log('[SERVER] Servidor SambaTu API rodando na porta', PORT);
});
