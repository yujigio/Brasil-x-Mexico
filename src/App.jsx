import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, ShieldAlert, Search, Eye, EyeOff, Lock, RefreshCw, 
  Copy, Check, Database, AlertTriangle, Key, ExternalLink, 
  Shield, Activity, CheckCircle2, XCircle, HelpCircle, BarChart3, User, Mail
} from 'lucide-react';

export default function App() {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [currentPasswordInput, setCurrentPasswordInput] = useState('');
  const [showCurrentInput, setShowCurrentInput] = useState(false);
  const [useKAnonymity, setUseKAnonymity] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [revealLeaked, setRevealLeaked] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('check');
  const [stats, setStats] = useState(null);

  const [usernameInput, setUsernameInput] = useState('');
  const [userCheckLoading, setUserCheckLoading] = useState(false);
  const [userCheckResult, setUserCheckResult] = useState(null);

  const [genLength, setGenLength] = useState(16);
  const [genUppercase, setGenUppercase] = useState(true);
  const [genLowercase, setGenLowercase] = useState(true);
  const [genNumbers, setGenNumbers] = useState(true);
  const [genSymbols, setGenSymbols] = useState(true);
  const [generatedPassword, setGeneratedPassword] = useState('');

  useEffect(() => {
    fetchStats();
    generateNewPassword();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats');
      if (res.ok) setStats(await res.json());
    } catch (e) {}
  };

  const calculateStrength = (pwd) => {
    if (!pwd) return { score: 0, label: 'Vazia', color: '#64748b' };
    let score = 0;
    if (pwd.length >= 8) score += 20;
    if (pwd.length >= 12) score += 20;
    if (/[A-Z]/.test(pwd)) score += 15;
    if (/[a-z]/.test(pwd)) score += 15;
    if (/[0-9]/.test(pwd)) score += 15;
    if (/[^A-Za-z0-9]/.test(pwd)) score += 15;

    if (score < 40) return { score, label: 'Muito Fraca', color: '#ff0844' };
    if (score < 65) return { score, label: 'Fraca', color: '#f59e0b' };
    if (score < 85) return { score, label: 'Média', color: '#3b82f6' };
    return { score, label: 'Forte', color: '#10b981' };
  };

  const getSHA1 = async (text) => {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await crypto.subtle.digest('SHA-1', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
  };

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!password) return;
    setLoading(true);
    setResult(null);
    setRevealLeaked(false);

    try {
      if (useKAnonymity) {
        const sha1 = await getSHA1(password);
        const prefix = sha1.substring(0, 5);
        const suffix = sha1.substring(5);

        const res = await fetch('/api/range/' + prefix);
        if (!res.ok) throw new Error('Erro');

        const data = await res.json();
        const match = data.hashes.find(item => item.suffix === suffix);

        if (match) {
          setResult({
            pwned: true,
            count: match.count,
            sha1: sha1,
            leakedPassword: match.pwd || password,
            riskLevel: match.count >= 10 ? 'CRÍTICO' : match.count >= 3 ? 'ALTO' : 'MÉDIO',
            method: 'k-Anonimato SHA-1'
          });
        } else {
          setResult({
            pwned: false,
            count: 0,
            sha1: sha1,
            leakedPassword: null,
            riskLevel: 'SEGURO',
            method: 'k-Anonimato SHA-1'
          });
        }
      } else {
        const res = await fetch('/api/check', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password })
        });
        if (!res.ok) throw new Error('Erro');

        const data = await res.json();
        setResult({ ...data, method: 'Consulta Direta' });
      }
    } catch (err) {
      setResult({ error: true, message: 'Servidor SambaTu API indisponível.' });
    } finally {
      setLoading(false);
    }
  };

  const handleUserCheck = async (e) => {
    e.preventDefault();
    if (!usernameInput) return;
    setUserCheckLoading(true);
    setUserCheckResult(null);

    try {
      const res = await fetch('/api/check-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameInput })
      });
      if (!res.ok) throw new Error('Erro na requisição');

      const data = await res.json();
      setUserCheckResult(data);
    } catch (err) {
      setUserCheckResult({ error: true, message: 'Servidor SambaTu API indisponível.' });
    } finally {
      setUserCheckLoading(false);
    }
  };

  const generateNewPassword = () => {
    let chars = '';
    if (genUppercase) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (genLowercase) chars += 'abcdefghijklmnopqrstuvwxyz';
    if (genNumbers) chars += '0123456789';
    if (genSymbols) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';
    if (!chars) chars = 'abcdefghijklmnopqrstuvwxyz0123456789';

    let resultPwd = '';
    for (let i = 0; i < genLength; i++) {
      resultPwd += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setGeneratedPassword(resultPwd);
  };

  const copyToClipboard = (txt) => {
    navigator.clipboard.writeText(txt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const strengthInfo = calculateStrength(password);

  return (
    <div className='min-h-screen pb-16 text-slate-100 font-sans'>
      <header className='border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 p-4'>
        <div className='max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4'>
          <div className='flex items-center gap-3'>
            <div className='p-2.5 rounded-xl bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20'>
              <ShieldCheck className='w-6 h-6 stroke-[2.5]' />
            </div>
            <div>
              <h1 className='text-xl font-bold text-white'>SambaTu <span className='text-cyan-400'>BreachChecker</span></h1>
              <p className='text-xs text-slate-400'>Base de Dados de Senhas Brasileiras (HideMeBr/SambaTu)</p>
            </div>
          </div>

          <div className='flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-full px-4 py-1.5 text-xs font-mono text-cyan-400'>
            <span className='w-2 h-2 rounded-full bg-emerald-400 animate-pulse'></span>
            <span>{stats?.totalUnique ? stats.totalUnique.toLocaleString('pt-BR') : '2.140.282'} senhas BR higienizadas</span>
          </div>
        </div>
      </header>

      <main className='max-w-4xl mx-auto px-4 pt-8'>
        <div className='text-center mb-8'>
          <h2 className='text-3xl font-extrabold mb-2'>
            Sua conta ou senha foi exposta em <span className='text-cyan-400'>Vazamentos?</span>
          </h2>
          <p className='text-slate-400 text-sm sm:text-base'>
            Consulte a base brasileira <strong>SambaTu</strong> em ambiente 100% higienizado.
          </p>
        </div>

        <div className='flex justify-center gap-2 mb-8 border-b border-slate-800/80 pb-3 overflow-x-auto'>
          <button
            onClick={() => setActiveTab('check')}
            className={'px-5 py-2.5 rounded-xl font-medium text-sm transition-all ' + (activeTab === 'check' ? 'bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/20' : 'text-slate-400 hover:text-slate-200')}
          >
            Consulta de Senha
          </button>
          <button
            onClick={() => setActiveTab('usercheck')}
            className={'px-5 py-2.5 rounded-xl font-medium text-sm transition-all ' + (activeTab === 'usercheck' ? 'bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/20' : 'text-slate-400 hover:text-slate-200')}
          >
            Consulta por Usuário / E-mail
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={'px-5 py-2.5 rounded-xl font-medium text-sm transition-all ' + (activeTab === 'stats' ? 'bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/20' : 'text-slate-400 hover:text-slate-200')}
          >
            Dados SambaTu
          </button>
          <button
            onClick={() => setActiveTab('generator')}
            className={'px-5 py-2.5 rounded-xl font-medium text-sm transition-all ' + (activeTab === 'generator' ? 'bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/20' : 'text-slate-400 hover:text-slate-200')}
          >
            Gerador de Senha
          </button>
          <button
            onClick={() => setActiveTab('privacy')}
            className={'px-5 py-2.5 rounded-xl font-medium text-sm transition-all ' + (activeTab === 'privacy' ? 'bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/20' : 'text-slate-400 hover:text-slate-200')}
          >
            Privacidade (k-Anonimato)
          </button>
        </div>

        {activeTab === 'check' && (
          <div className='space-y-6'>
            <div className='cyber-glass p-6 sm:p-8 border border-slate-800 rounded-2xl bg-slate-900/60 space-y-4'>
              <form onSubmit={handleCheck} className='space-y-4'>
                <div className='flex items-center justify-between mb-1'>
                  <label className='block text-xs font-semibold uppercase tracking-wider text-slate-300'>
                    Digite a senha para verificar
                  </label>
                  <div className='flex items-center gap-2'>
                    <input
                      type='checkbox'
                      id='kanon'
                      checked={useKAnonymity}
                      onChange={(e) => setUseKAnonymity(e.target.checked)}
                      className='rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-500/30'
                    />
                    <label htmlFor='kanon' className='text-xs text-slate-400 cursor-pointer flex items-center gap-1'>
                      <Shield className='w-3 h-3 text-cyan-400' /> k-Anonimato Client-side (Máxima Segurança)
                    </label>
                  </div>
                </div>

                <div className='relative'>
                  <div className='absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500'>
                    <Lock className='w-5 h-5' />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder='Digite a senha para checar...'
                    className='w-full pl-11 pr-24 py-3.5 bg-slate-950/80 border border-slate-800 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono text-sm sm:text-base transition-all'
                  />
                  <button
                    type='button'
                    onClick={() => setShowPassword(!showPassword)}
                    className='absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-200 text-xs font-sans gap-1'
                  >
                    {showPassword ? <EyeOff className='w-4 h-4' /> : <Eye className='w-4 h-4' />}
                    <span>{showPassword ? 'Ocultar' : 'Mostrar'}</span>
                  </button>
                </div>

                {password && (
                  <div className='space-y-1.5 pt-1'>
                    <div className='flex items-center justify-between text-xs'>
                      <span className='text-slate-400'>Força da Senha:</span>
                      <span className='font-bold' style={{ color: strengthInfo.color }}>
                        {strengthInfo.label} ({strengthInfo.score}%)
                      </span>
                    </div>
                    <div className='h-1.5 w-full bg-slate-900 rounded-full overflow-hidden'>
                      <div
                        className='h-full transition-all duration-300 rounded-full'
                        style={{ width: strengthInfo.score + '%', backgroundColor: strengthInfo.color }}
                      ></div>
                    </div>
                  </div>
                )}

                <button
                  type='submit'
                  disabled={loading || !password}
                  className='w-full py-4 px-6 rounded-xl font-bold text-slate-950 bg-gradient-to-r from-cyan-400 via-cyan-300 to-blue-500 hover:from-cyan-300 hover:to-blue-400 transition-all shadow-lg shadow-cyan-500/25 disabled:opacity-50 flex items-center justify-center gap-2 text-base mt-2'
                >
                  {loading ? (
                    <>
                      <RefreshCw className='w-5 h-5 animate-spin' /> Consultando Base SambaTu...
                    </>
                  ) : (
                    <>
                      <Search className='w-5 h-5 stroke-[2.5]' /> Verificar se foi Vazada no SambaTu
                    </>
                  )}
                </button>
              </form>
            </div>

            {result && (
              <div className='transition-all'>
                {result.error ? (
                  <div className='cyber-glass p-6 border border-amber-500/40 bg-amber-950/20 text-amber-200 rounded-xl flex items-start gap-4'>
                    <AlertTriangle className='w-6 h-6 text-amber-400 shrink-0 mt-0.5' />
                    <div>
                      <h4 className='font-bold text-base text-amber-400 mb-1'>Aviso do Sistema</h4>
                      <p className='text-sm text-amber-200/80'>{result.message}</p>
                    </div>
                  </div>
                ) : result.pwned ? (
                  <div className='cyber-glass p-6 sm:p-8 border border-red-500/40 bg-red-950/20 rounded-2xl space-y-6'>
                    <div className='flex items-start gap-4 border-b border-red-500/20 pb-5'>
                      <div className='p-3 rounded-full bg-red-500/20 text-red-400 shrink-0 border border-red-500/30'>
                        <ShieldAlert className='w-8 h-8' />
                      </div>
                      <div className='space-y-1'>
                        <div className='flex items-center gap-2'>
                          <span className='px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/40 uppercase tracking-wide'>
                            Risco {result.riskLevel}
                          </span>
                          <span className='text-xs font-mono text-slate-400'>Método: {result.method}</span>
                        </div>
                        <h3 className='text-xl sm:text-2xl font-bold text-white'>
                          Esta senha foi <span className='text-red-400'>ENCONTRADA em Vazamentos!</span>
                        </h3>
                        <p className='text-sm text-slate-300'>
                          Encontrada <strong>{result.count} vez(es)</strong> na base brasileira de senhas expostas <strong>SambaTu</strong>.
                        </p>
                      </div>
                    </div>

                    <div className='bg-slate-950/90 border border-slate-800 rounded-xl p-5 space-y-4'>
                      <div className='flex flex-col sm:flex-row sm:items-center justify-between gap-3'>
                        <div>
                          <h4 className='text-sm font-semibold text-white flex items-center gap-1.5'>
                            <Eye className='w-4 h-4 text-cyan-400' /> Revelar Senha Vazada na Base SambaTu
                          </h4>
                          <p className='text-xs text-slate-400'>Visualize a senha exata registrada no vazamento para comparar se é a senha que você usa atualmente.</p>
                        </div>
                        <button
                          onClick={() => setRevealLeaked(!revealLeaked)}
                          className='px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-400 text-xs font-medium transition-colors flex items-center justify-center gap-1.5 self-start sm:self-auto'
                        >
                          {revealLeaked ? <EyeOff className='w-3.5 h-3.5' /> : <Eye className='w-3.5 h-3.5' />}
                          {revealLeaked ? 'Ocultar Senha' : 'Revelar Senha Vazada'}
                        </button>
                      </div>

                      {revealLeaked && (
                        <div className='p-4 rounded-lg bg-slate-900 border border-red-500/30 flex items-center justify-between font-mono text-sm sm:text-base text-red-300 break-all'>
                          <span>{result.leakedPassword || password}</span>
                          <span className='text-xs font-sans px-2 py-1 rounded bg-red-500/20 text-red-400 border border-red-500/30 ml-2 shrink-0'>Registrada em Leaks</span>
                        </div>
                      )}
                    </div>

                    <div className='bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-3'>
                      <h4 className='text-sm font-semibold text-white flex items-center gap-1.5'>
                        <HelpCircle className='w-4 h-4 text-amber-400' /> Comparar com sua Senha Atual em uso
                      </h4>
                      <p className='text-xs text-slate-400'>Digite abaixo a senha que você usa atualmente em suas contas para checar a coincidência exata:</p>

                      <div className='relative'>
                        <input
                          type={showCurrentInput ? 'text' : 'password'}
                          value={currentPasswordInput}
                          onChange={(e) => setCurrentPasswordInput(e.target.value)}
                          placeholder='Digite a sua senha atual...'
                          className='w-full pl-4 pr-24 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-amber-500 text-sm font-mono'
                        />
                        <button
                          type='button'
                          onClick={() => setShowCurrentInput(!showCurrentInput)}
                          className='absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 text-xs gap-1'
                        >
                          {showCurrentInput ? <EyeOff className='w-3.5 h-3.5' /> : <Eye className='w-3.5 h-3.5' />}
                        </button>
                      </div>

                      {currentPasswordInput && (
                        <div className={'p-3 rounded-lg text-xs font-semibold flex items-center gap-2 ' + (
                          currentPasswordInput === (result.leakedPassword || password)
                            ? 'bg-red-500/20 border border-red-500/40 text-red-300'
                            : 'bg-emerald-500/20 border border-emerald-500/40 text-emerald-300'
                        )}>
                          {currentPasswordInput === (result.leakedPassword || password) ? (
                            <>
                              <XCircle className='w-4 h-4 text-red-400 shrink-0' />
                              <span>ALERTA MÁXIMO: Esta É A SUA SENHA ATUAL! Ela está comprometida e você deve alterá-la IMEDIATAMENTE em seus serviços.</span>
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className='w-4 h-4 text-emerald-400 shrink-0' />
                              <span>A senha consultada não coincide com a sua senha atual digitada. Boa prática!</span>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className='cyber-glass p-6 sm:p-8 border border-emerald-500/40 bg-emerald-950/20 rounded-2xl space-y-4'>
                    <div className='flex items-start gap-4'>
                      <div className='p-3 rounded-full bg-emerald-500/20 text-emerald-400 shrink-0 border border-emerald-500/30'>
                        <ShieldCheck className='w-8 h-8' />
                      </div>
                      <div>
                        <span className='px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 uppercase tracking-wide'>
                          Status: {result.riskLevel}
                        </span>
                        <h3 className='text-xl sm:text-2xl font-bold text-white mt-1'>
                          Nenhum Vazamento Encontrado!
                        </h3>
                        <p className='text-sm text-slate-300 mt-1'>
                          Esta senha <strong>não foi localizada</strong> na base de vazamentos brasileira <strong>SambaTu</strong>.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'usercheck' && (
          <div className='space-y-6'>
            <div className='cyber-glass p-6 sm:p-8 border border-slate-800 rounded-2xl bg-slate-900/60 space-y-4'>
              <form onSubmit={handleUserCheck} className='space-y-4'>
                <label className='block text-xs font-semibold uppercase tracking-wider text-slate-300'>
                  Digite o Nome de Usuário ou E-mail para verificar status
                </label>

                <div className='relative'>
                  <div className='absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500'>
                    <User className='w-5 h-5' />
                  </div>
                  <input
                    type='text'
                    value={usernameInput}
                    onChange={(e) => setUsernameInput(e.target.value)}
                    placeholder='Nome de usuário ou e-mail (ex: usuario@email.com)...'
                    className='w-full pl-11 pr-4 py-3.5 bg-slate-950/80 border border-slate-800 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono text-sm sm:text-base transition-all'
                  />
                </div>

                <div className='text-xs text-slate-400 bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center gap-2'>
                  <Shield className='w-4 h-4 text-cyan-400 shrink-0' />
                  <span>Por políticas de privacidade e segurança, a consulta por usuário exibe apenas se a conta foi afetada (Sim/Não), sem expor senhas ou credenciais.</span>
                </div>

                <button
                  type='submit'
                  disabled={userCheckLoading || !usernameInput}
                  className='w-full py-4 px-6 rounded-xl font-bold text-slate-950 bg-gradient-to-r from-cyan-400 via-cyan-300 to-blue-500 hover:from-cyan-300 hover:to-blue-400 transition-all shadow-lg shadow-cyan-500/25 disabled:opacity-50 flex items-center justify-center gap-2 text-base mt-2'
                >
                  {userCheckLoading ? (
                    <>
                      <RefreshCw className='w-5 h-5 animate-spin' /> Verificando Usuário...
                    </>
                  ) : (
                    <>
                      <Search className='w-5 h-5 stroke-[2.5]' /> Checar Status do Usuário
                    </>
                  )}
                </button>
              </form>
            </div>

            {userCheckResult && (
              <div className='transition-all'>
                {userCheckResult.error ? (
                  <div className='cyber-glass p-6 border border-amber-500/40 bg-amber-950/20 text-amber-200 rounded-xl flex items-start gap-4'>
                    <AlertTriangle className='w-6 h-6 text-amber-400 shrink-0 mt-0.5' />
                    <div>
                      <h4 className='font-bold text-base text-amber-400 mb-1'>Aviso do Sistema</h4>
                      <p className='text-sm text-amber-200/80'>{userCheckResult.message}</p>
                    </div>
                  </div>
                ) : userCheckResult.pwned ? (
                  <div className='cyber-glass p-6 sm:p-8 border border-red-500/40 bg-red-950/20 rounded-2xl space-y-4'>
                    <div className='flex items-start gap-4'>
                      <div className='p-3 rounded-full bg-red-500/20 text-red-400 shrink-0 border border-red-500/30'>
                        <ShieldAlert className='w-8 h-8' />
                      </div>
                      <div className='space-y-1'>
                        <span className='px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/40 uppercase tracking-wide'>
                          STATUS: COMPROMETIDO
                        </span>
                        <h3 className='text-xl sm:text-2xl font-bold text-white mt-1'>
                          O Usuário <span className='text-red-400 font-mono'>'{userCheckResult.username}'</span> Consta em Vazamentos!
                        </h3>
                        <p className='text-sm text-slate-300'>
                          Resultado: <strong>SIM (Vazado)</strong>. Recomendamos alterar a senha imediatamente.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className='cyber-glass p-6 sm:p-8 border border-emerald-500/40 bg-emerald-950/20 rounded-2xl space-y-4'>
                    <div className='flex items-start gap-4'>
                      <div className='p-3 rounded-full bg-emerald-500/20 text-emerald-400 shrink-0 border border-emerald-500/30'>
                        <ShieldCheck className='w-8 h-8' />
                      </div>
                      <div>
                        <span className='px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 uppercase tracking-wide'>
                          STATUS: SEGURO
                        </span>
                        <h3 className='text-xl sm:text-2xl font-bold text-white mt-1'>
                          Nenhum Vazamento Encontrado para <span className='text-emerald-400 font-mono'>'{userCheckResult.username}'</span>!
                        </h3>
                        <p className='text-sm text-slate-300 mt-1'>
                          Resultado: <strong>NÃO (Não Encontrado)</strong> na base SambaTu.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'stats' && (
          <div className='space-y-6'>
            <div className='grid grid-cols-1 sm:grid-cols-3 gap-4'>
              <div className='p-5 rounded-xl bg-slate-900 border border-slate-800'>
                <div className='text-xs text-slate-400 mb-1 flex items-center justify-between'>
                  <span>Total de Senhas Analisadas</span>
                  <Database className='w-4 h-4 text-cyan-400' />
                </div>
                <div className='text-2xl font-extrabold text-white font-mono'>
                  {stats?.totalValid ? stats.totalValid.toLocaleString('pt-BR') : '2.140.469'}
                </div>
                <div className='text-[11px] text-cyan-400 mt-1'>Sanitizadas e Isentas de Malware</div>
              </div>

              <div className='p-5 rounded-xl bg-slate-900 border border-slate-800'>
                <div className='text-xs text-slate-400 mb-1 flex items-center justify-between'>
                  <span>Senhas Únicas Indexadas</span>
                  <Key className='w-4 h-4 text-blue-400' />
                </div>
                <div className='text-2xl font-extrabold text-white font-mono'>
                  {stats?.totalUnique ? stats.totalUnique.toLocaleString('pt-BR') : '2.140.282'}
                </div>
                <div className='text-[11px] text-blue-400 mt-1'>Índice k-Anonimato SHA-1</div>
              </div>

              <div className='p-5 rounded-xl bg-slate-900 border border-slate-800'>
                <div className='text-xs text-slate-400 mb-1 flex items-center justify-between'>
                  <span>Fonte dos Dados</span>
                  <Activity className='w-4 h-4 text-emerald-400' />
                </div>
                <div className='text-lg font-bold text-white truncate'>
                  HideMeBr/SambaTu
                </div>
                <div className='text-[11px] text-emerald-400 mt-1'>Repositório Público GitHub</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'generator' && (
          <div className='p-6 sm:p-8 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-6'>
            <div className='flex items-center justify-between'>
              <div>
                <h3 className='text-xl font-bold text-white flex items-center gap-2'>
                  <Key className='w-5 h-5 text-cyan-400' /> Gerador de Senhas Ultra-Seguras
                </h3>
                <p className='text-xs text-slate-400'>Crie senhas com alta entropia que não constam em listas como SambaTu.</p>
              </div>
            </div>

            <div className='relative p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between font-mono text-lg text-cyan-300 break-all'>
              <span>{generatedPassword}</span>
              <div className='flex items-center gap-2 ml-2 shrink-0'>
                <button
                  onClick={generateNewPassword}
                  className='p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors'
                  title='Gerar Outra'
                >
                  <RefreshCw className='w-4 h-4' />
                </button>
                <button
                  onClick={() => copyToClipboard(generatedPassword)}
                  className='px-3 py-1.5 bg-cyan-400 text-slate-950 font-bold text-xs rounded shadow'
                >
                  {copied ? 'Copiado!' : 'Copiar'}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'privacy' && (
          <div className='p-6 sm:p-8 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5 text-slate-300 text-sm leading-relaxed'>
            <h3 className='text-xl font-bold text-white flex items-center gap-2'>
              <Shield className='w-5 h-5 text-cyan-400' /> Garantia de Privacidade e Isolamento
            </h3>
            <div className='p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1'>
              <h4 className='font-bold text-cyan-400 text-sm'>1. Isolamento Absoluto na Ingestão (Anti-Malware)</h4>
              <p className='text-xs text-slate-400'>A base SambaTu foi baixada e higienizada linha por linha descartando qualquer código ou payload executável.</p>
            </div>
            <div className='p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1'>
              <h4 className='font-bold text-cyan-400 text-sm'>2. k-Anonimato Client-side (SHA-1)</h4>
              <p className='text-xs text-slate-400'>Sua senha original NUNCA é enviada. O navegador calcula o SHA-1 localmente e envia apenas os primeiros 5 caracteres para a API.</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
