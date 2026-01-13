import { useState } from 'react';
import axios from 'axios';
import { Map, Zap, Database, ArrowRight, Code2, AlertCircle, Loader2 } from 'lucide-react';

// URL do Backend (ajustar se mudar porta ou ambiente)
const API_URL = "http://localhost:8000";

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'IDLE' | 'FETCHING' | 'INFERRING' | 'DONE'>('IDLE');
  const [rawData, setRawData] = useState<any>(null);
  const [schema, setSchema] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleProcess = async () => {
    if (!url) return;
    setLoading(true);
    setError(null);
    setRawData(null);
    setSchema(null);
    
    try {
      // Passo 1: Buscar Dados (Proxy)
      setStep('FETCHING');
      const fetchResponse = await axios.get(`${API_URL}/fetch`, { params: { url } });
      
      // Lógica de Amostragem: Pega o primeiro item ou feature
      let sample = fetchResponse.data;
      if (Array.isArray(sample) && sample.length > 0) sample = sample[0];
      if (sample.features && Array.isArray(sample.features)) sample = sample.features[0];

      setRawData(sample);

      // Passo 2: Inferir Schema (IA)
      setStep('INFERRING');
      const inferResponse = await axios.post(`${API_URL}/infer`, { sample });
      setSchema(inferResponse.data);

      setStep('DONE');
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || "Erro desconhecido");
      setStep('IDLE');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-8 font-sans max-w-7xl mx-auto selection:bg-blue-500/30">
      {/* Header */}
      <header className="mb-12 text-center animate-fade-in-down">
        <div className="inline-flex items-center justify-center p-3 bg-blue-600/10 rounded-full mb-4 ring-1 ring-blue-500/30 shadow-lg shadow-blue-500/10">
          <Map className="w-8 h-8 text-blue-400" />
        </div>
        <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 mb-2 tracking-tight">
          EasyAPIGIS
        </h1>
        <p className="text-slate-400 text-lg font-light">
          Middleware de Interoperabilidade Espacial Inteligente
        </p>
      </header>

      {/* Input Section */}
      <div className="max-w-2xl mx-auto mb-12">
        <div className="bg-slate-800/50 p-2 rounded-xl border border-slate-700 flex shadow-2xl backdrop-blur-sm transition-all focus-within:border-blue-500/50 focus-within:ring-2 focus-within:ring-blue-500/20">
          <input 
            type="text" 
            placeholder="Cole a URL da API Geoespacial aqui (JSON/GeoJSON)..."
            className="flex-1 bg-transparent border-none outline-none text-white px-4 placeholder:text-slate-500 w-full"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleProcess()}
          />
          <button 
            onClick={handleProcess}
            disabled={loading || !url}
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-600/20"
          >
            {loading ? <Loader2 className="animate-spin w-5 h-5" /> : <Zap className="w-5 h-5 fill-current" />}
            <span className="hidden sm:inline">
              {step === 'FETCHING' ? 'Baixando...' : step === 'INFERRING' ? 'Analisando...' : 'Processar'}
            </span>
          </button>
        </div>
        
        {/* Sugestão de URL para teste */}
        <div className="mt-4 text-center">
            <span className="text-xs text-slate-500 mr-2 uppercase tracking-wider font-semibold">Tente com:</span>
            <button 
                onClick={() => setUrl("https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-35-mun.json")}
                className="text-xs text-blue-400 hover:text-blue-300 hover:underline transition-colors"
            >
                Municípios SP (GeoJSON)
            </button>
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-950/30 border border-red-500/30 rounded-lg text-red-200 flex items-start gap-3 shadow-lg animate-shake">
            <AlertCircle className="w-5 h-5 mt-0.5 text-red-400 shrink-0" />
            <div>
              <h3 className="font-semibold text-red-400 text-sm">Falha no processamento</h3>
              <p className="text-sm opacity-90">{error}</p>
            </div>
          </div>
        )}
      </div>

      {/* Results Grid */}
      {(rawData || schema) && (
        <div className="grid lg:grid-cols-2 gap-8 animate-fade-in">
          {/* Coluna 1: Raw Data */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden flex flex-col h-[600px] shadow-xl">
            <div className="bg-slate-900/50 p-4 border-b border-slate-700 flex justify-between items-center backdrop-blur-md">
              <div className="flex items-center gap-2 text-slate-300">
                <Database className="w-4 h-4 text-emerald-400" />
                <span className="font-mono text-sm font-semibold">Dados Originais (Amostra)</span>
              </div>
              <span className="text-[10px] font-mono bg-slate-700 text-slate-300 px-2 py-1 rounded border border-slate-600">
                RAW JSON
              </span>
            </div>
            <div className="flex-1 overflow-auto p-4 custom-scrollbar bg-[#0b1120]">
              <pre className="text-xs font-mono text-emerald-300/90 whitespace-pre-wrap break-all leading-relaxed">
                {JSON.stringify(rawData, null, 2)}
              </pre>
            </div>
          </div>

          {/* Coluna 2: Inferred Schema */}
          <div className="bg-slate-800 rounded-xl border border-blue-500/30 overflow-hidden flex flex-col h-[600px] shadow-[0_0_40px_rgba(59,130,246,0.15)] relative">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500"></div>
            <div className="bg-blue-950/20 p-4 border-b border-blue-500/20 flex justify-between items-center backdrop-blur-md">
              <div className="flex items-center gap-2 text-blue-100">
                <Code2 className="w-4 h-4 text-blue-400" />
                <span className="font-mono text-sm font-bold">Schema Inferido pela IA</span>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-blue-300 bg-blue-900/30 px-2 py-1 rounded border border-blue-500/20">
                <Zap className="w-3 h-3 text-yellow-400 fill-current" />
                <span className="font-semibold tracking-wide">GROQ LLAMA 3</span>
              </div>
            </div>
            
            <div className="flex-1 overflow-auto p-6 custom-scrollbar bg-slate-900/50">
               {schema ? (
                 <div className="space-y-6">
                    {/* Geometry Info Cards */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-slate-800/80 p-4 rounded-lg border border-slate-700/50 hover:border-blue-500/30 transition-colors">
                            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1 block">Geometria</span>
                            <span className="text-blue-400 font-mono font-bold text-lg flex items-center gap-2">
                              {schema.geometry_type}
                            </span>
                        </div>
                        <div className="bg-slate-800/80 p-4 rounded-lg border border-slate-700/50 hover:border-green-500/30 transition-colors">
                            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1 block">SRID (Projeção)</span>
                            <span className="text-green-400 font-mono font-bold text-lg">
                              EPSG:{schema.srid}
                            </span>
                        </div>
                    </div>
                    
                    {/* Fields Table */}
                    <div className="border border-slate-700/50 rounded-lg overflow-hidden bg-slate-800/30">
                      <table className="w-full text-left text-sm">
                          <thead className="bg-slate-900/80 text-xs text-slate-500 uppercase tracking-wider font-semibold">
                              <tr>
                                  <th className="px-4 py-3 border-b border-slate-700">Campo Original</th>
                                  <th className="px-4 py-3 border-b border-slate-700">Destino (SQL)</th>
                                  <th className="px-4 py-3 border-b border-slate-700">Tipo</th>
                              </tr>
                          </thead>
                          <tbody className="font-mono text-xs divide-y divide-slate-700/50">
                              {schema.fields.map((field: any, i: number) => (
                                  <tr key={i} className="hover:bg-white/5 transition-colors group">
                                      <td className="px-4 py-3 text-slate-400 group-hover:text-white transition-colors">
                                        {field.original_name}
                                      </td>
                                      <td className="px-4 py-3 text-blue-300">
                                        <div className="flex items-center gap-2">
                                          <ArrowRight className="w-3 h-3 opacity-30 group-hover:opacity-100 transition-opacity text-blue-500" />
                                          {field.target_name}
                                        </div>
                                      </td>
                                      <td className="px-4 py-3">
                                        <span className="text-yellow-500/90 bg-yellow-500/10 px-1.5 py-0.5 rounded border border-yellow-500/20">
                                          {field.type}
                                        </span>
                                      </td>
                                  </tr>
                              ))}
                          </tbody>
                      </table>
                    </div>
                 </div>
               ) : (
                 <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4 opacity-50">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    <span className="text-sm">Aguardando resposta da Inteligência...</span>
                 </div>
               )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;