<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logic Turf App</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    animation: { 'fade-in': 'fadeIn 0.5s ease-out' },
                    keyframes: { fadeIn: { '0%': { opacity: '0', transform: 'translateY(10px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } } }
                }
            }
        }
    </script>
    <style>
        body { background-color: #020617; color: #e2e8f0; font-family: sans-serif; overflow-x: hidden; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // =================================================================
        // ▼▼▼ ここに Render の URL を貼り付けてください ▼▼▼
        // 例: const API_BASE_URL = "https://logic-turf-server-xxxx.onrender.com";
        // 末尾に "/" は不要です
        
        const API_BASE_URL = "ここにあなたのRenderのURLを貼り付けてください";
        
        // =================================================================

        // --- アイコン部品 ---
        const IconBase = ({ children, className }) => ( <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>{children}</svg> );
        const Brain = (props) => <IconBase {...props}><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></IconBase>;
        const Target = (props) => <IconBase {...props}><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></IconBase>;
        const TrendingUp = (props) => <IconBase {...props}><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></IconBase>;
        const DollarSign = (props) => <IconBase {...props}><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></IconBase>;
        const ChevronRight = (props) => <IconBase {...props}><polyline points="9 18 15 12 9 6"/></IconBase>;
        const AlertTriangle = (props) => <IconBase {...props}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></IconBase>;
        const Info = (props) => <IconBase {...props}><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></IconBase>;
        const CheckCircle = (props) => <IconBase {...props}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></IconBase>;
        const RefreshCw = (props) => <IconBase {...props}><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></IconBase>;
        const Database = (props) => <IconBase {...props}><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></IconBase>;

        // --- Logic & Data ---
        const BIAS_PATTERNS = {
            A: { id: 'A', name: 'A: 内有利 × 高速', desc: '内枠・先行有利。インベタで回れる馬を重視。', icon: '🚀' },
            B: { id: 'B', name: 'B: 外有利 × タフ', desc: '外枠・差し有利。体力を要する馬場。', icon: '💪' },
            C: { id: 'C', name: 'C: 内有利 × タフ', desc: 'パワーが必要だが内が伸びる。パワー先行馬。', icon: '🛡️' },
            D: { id: 'D', name: 'D: 外有利 × 高速', desc: '外差しが決まる高速馬場。スピード重視。', icon: '⚡' },
        };
        const LOCATIONS = ['東京', '中山', '京都', '阪神', '中京', '札幌', '函館', '福島', '新潟', '小倉'];

        // 分析ロジック (API対応版)
        const analyzeRace = (biasId, budget, realData = null) => {
            let reasoning = {};
            let horses = [];
            
            // バイアスごとのロジック定義
            switch (biasId) {
                case 'A':
                    reasoning = {
                        centerPin: "高速馬場への適応力と、ロスなく立ち回れる機動力を最優先で評価。近走で「外を回して負けた」隠れ実力馬をピックアップ。",
                        structure: "トラックバイアス「パターンA（内・前）」に合致します。逃げ馬不在のメンバー構成から、スローペースで内枠の先行勢が止まらない展開を想定。",
                        bloodline: "高速決着に強い「米国型ミスプロ系」や、平坦巧者の血を持つ馬を評価。"
                    };
                    break;
                case 'B':
                    reasoning = {
                        centerPin: "タフな馬場でのスタミナと、外からスムーズに加速できる持続力を評価。タイムランクよりも「上がりのかかるレース」での実績を重視。",
                        structure: "トラックバイアス「パターンB（外・差）」判定。内側の芝が荒れており、直線で外に持ち出せる馬が有利。ハイペース消耗戦を想定。",
                        bloodline: "欧州型ノーザンダンサー系やロベルト系など、底力とスタミナに富んだ血統を重視。"
                    };
                    break;
                case 'C':
                    reasoning = {
                        centerPin: "パワーを要する馬場ですが、物理的に距離ロスの少ない内を通れる馬を評価。馬格があり、揉まれ強い馬を中心に選定。",
                        structure: "トラックバイアス「パターンC（内・タフ）」判定。時計はかかるが、外を回すと届かない特殊な馬場。インで我慢できるパワータイプを狙う。",
                        bloodline: "ダート的なパワーを伝えるStorm Cat系や、重馬場得意なサドラーズウェルズ系を評価。"
                    };
                    break;
                default: // D
                    reasoning = {
                        centerPin: "絶対的なスピード能力と、長い直線を活かせる末脚の質を評価。前走で「詰まって脚を余した」馬の巻き返しに注目。",
                        structure: "トラックバイアス「パターンD（外・速）」判定。直線スピード勝負。外枠からノビノビと走れる差し馬がまとめて面倒を見ると予測。",
                        bloodline: "サンデーサイレンス系の主要種牡馬、特にディープインパクト系のキレを最大評価。"
                    };
            }

            // 馬の選定ロジック
            if (realData && realData.horses) {
                // APIからデータが来た場合
                const allHorses = [...realData.horses];
                
                // 簡易ロジック：バイアスに合わせて枠順で有利不利を判定する
                // A/Cなら内枠、B/Dなら外枠を優遇するソート
                if (biasId === 'A' || biasId === 'C') {
                    allHorses.sort((a, b) => a.waku - b.waku); // 内枠有利
                } else {
                    allHorses.sort((a, b) => b.waku - a.waku); // 外枠有利
                }
                
                // 上位5頭をピックアップ
                const selected = allHorses.slice(0, 5);
                horses = [
                    { ...selected[0], type: "◎", reason: "バイアス・展開絶好" },
                    { ...selected[1], type: "○", reason: "能力上位" },
                    { ...selected[2], type: "▲", reason: "一発の魅力" },
                    { ...selected[3], type: "△", reason: "押さえ" },
                    { ...selected[4], type: "△", reason: "展開向く" }
                ];
            } else {
                // データがない場合のフォールバック（デモ用）
                horses = [
                    { num: 1, name: "サンプルホースA", type: "◎", reason: "軸馬" },
                    { num: 2, name: "サンプルホースB", type: "○", reason: "対抗" },
                    { num: 3, name: "サンプルホースC", type: "▲", reason: "単穴" },
                    { num: 4, name: "サンプルホースD", type: "△", reason: "連下" },
                    { num: 5, name: "サンプルホースE", type: "△", reason: "連下" }
                ];
            }

            // 資金配分計算
            const allocations = calculateAllocation(horses, budget);
            return { reasoning, horses, allocations };
        };

        const calculateAllocation = (horses, budget) => {
            const axis = horses[0];
            const seconds = [horses[1], horses[2]];
            const thirds = [horses[1], horses[2], horses[3], horses[4]];
            
            const combinations = [];
            seconds.forEach(sec => {
                thirds.forEach(thd => {
                    if (sec.num !== thd.num && sec.num > thd.num) combinations.push([axis.num, thd.num, sec.num]);
                    else if (sec.num !== thd.num && sec.num < thd.num) combinations.push([axis.num, sec.num, thd.num]);
                });
            });

            const uniqueCombs = Array.from(new Set(combinations.map(JSON.stringify)), JSON.parse);
            const totalWeight = uniqueCombs.reduce((acc, _, idx) => acc + (uniqueCombs.length - idx), 0);
            
            let remainingBudget = budget;
            const allocations = uniqueCombs.map((comb, idx) => {
                const weight = uniqueCombs.length - idx;
                let amount = Math.floor((budget * (weight / totalWeight)) / 100) * 100;
                if (amount < 100) amount = 100;
                remainingBudget -= amount;
                return { comb, amount };
            });

            if (remainingBudget > 0 && allocations.length > 0) allocations[0].amount += remainingBudget;
            return allocations;
        };

        // --- Components ---

        const Header = () => (
            <header className="bg-slate-900 border-b border-amber-600/30 p-4 sticky top-0 z-50 backdrop-blur-md bg-opacity-90">
                <div className="max-w-md mx-auto flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <Brain className="text-amber-500 w-6 h-6" />
                        <h1 className="text-xl font-bold text-white tracking-wider">
                            Logic <span className="text-amber-500">Turf</span>
                        </h1>
                    </div>
                    <div className="text-xs text-emerald-400 font-mono border border-emerald-900 bg-emerald-900/30 px-2 py-1 rounded flex items-center">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full mr-1 animate-pulse"></div>
                        CLOUD
                    </div>
                </div>
            </header>
        );

        const ConfigScreen = ({ onSubmit }) => {
            const [formData, setFormData] = useState({ place: '東京', raceNum: '11', budget: 3000, bias: 'D' });
            const handleChange = (e) => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
            const handleBiasSelect = (key) => setFormData(prev => ({ ...prev, bias: key }));

            return (
                <div className="space-y-6 animate-fade-in">
                    <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                        <h2 className="text-amber-400 text-sm font-bold uppercase tracking-wider mb-4 flex items-center">
                            <Target className="w-4 h-4 mr-2" /> Target Race
                        </h2>
                        <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">開催場所</label>
                                <select name="place" value={formData.place} onChange={handleChange} className="w-full bg-slate-900 text-white border border-slate-700 rounded-lg p-3 text-sm focus:border-amber-500 outline-none">
                                    {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Race No.</label>
                                <select name="raceNum" value={formData.raceNum} onChange={handleChange} className="w-full bg-slate-900 text-white border border-slate-700 rounded-lg p-3 text-sm focus:border-amber-500 outline-none">
                                    {[...Array(12)].map((_, i) => <option key={i+1} value={i+1}>{i+1} R</option>)}
                                </select>
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">投資予算 (円)</label>
                            <div className="relative">
                                <DollarSign className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                                <input type="number" name="budget" value={formData.budget} onChange={handleChange} step="100" className="w-full bg-slate-900 text-white border border-slate-700 rounded-lg p-3 pl-10 text-sm focus:border-amber-500 outline-none font-mono" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-amber-400 text-sm font-bold uppercase tracking-wider flex items-center">
                                <TrendingUp className="w-4 h-4 mr-2" /> Track Bias
                            </h2>
                            <span className="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded">重要</span>
                        </div>
                        <div className="space-y-3">
                            {Object.entries(BIAS_PATTERNS).map(([key, data]) => (
                                <button key={key} onClick={() => handleBiasSelect(key)} className={`w-full text-left p-3 rounded-lg border transition-all duration-200 flex items-start group ${formData.bias === key ? 'bg-amber-900/20 border-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.2)]' : 'bg-slate-900 border-slate-800 hover:border-slate-600'}`}>
                                    <span className="text-2xl mr-3">{data.icon}</span>
                                    <div>
                                        <div className={`font-bold text-sm ${formData.bias === key ? 'text-amber-400' : 'text-slate-300'}`}>{data.name}</div>
                                        <div className="text-xs text-slate-500 mt-1">{data.desc}</div>
                                    </div>
                                    {formData.bias === key && <CheckCircle className="ml-auto w-5 h-5 text-amber-500" />}
                                </button>
                            ))}
                        </div>
                    </div>

                    <button onClick={() => onSubmit(formData)} className="w-full bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-slate-900 font-bold py-4 rounded-lg shadow-lg flex items-center justify-center space-x-2 transition-transform active:scale-95">
                        <span>START ANALYSIS</span> <ChevronRight className="w-5 h-5" />
                    </button>
                    
                    {API_BASE_URL.includes("render") ? (
                        <p className="text-xs text-center text-emerald-500/70 mt-2 font-mono flex items-center justify-center">
                            <Database className="w-3 h-3 mr-1" /> Server Connected
                        </p>
                    ) : (
                        <p className="text-xs text-center text-red-500/70 mt-2 font-mono">
                            ⚠️ URL未設定: コード内のAPI_BASE_URLを設定してください
                        </p>
                    )}
                </div>
            );
        };

        const ProcessingScreen = ({ config, onComplete }) => {
            const [progress, setProgress] = useState(0);
            const [status, setStatus] = useState("Initializing...");
            const [error, setError] = useState(null);

            useEffect(() => {
                const fetchData = async () => {
                    try {
                        setProgress(10);
                        setStatus(`Connecting to Server...`);
                        
                        // URLの末尾スラッシュ対策
                        const baseUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
                        const url = `${baseUrl}/api/race?place=${config.place}&race_num=${config.raceNum}`;
                        
                        console.log("Fetching:", url);
                        const res = await fetch(url);
                        setProgress(50);
                        
                        if (!res.ok) throw new Error("Server not responding");
                        const data = await res.json();
                        setProgress(80);
                        setStatus("Analyzing Fetched Data...");
                        
                        setTimeout(() => {
                            setProgress(100);
                            onComplete(data);
                        }, 1000);

                    } catch (err) {
                        console.error(err);
                        setError("サーバー接続エラー: " + err.message);
                    }
                };
                fetchData();
            }, [config, onComplete]);

            if (error) {
                return (
                    <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-4 animate-fade-in px-8">
                        <AlertTriangle className="w-12 h-12 text-red-500" />
                        <h3 className="text-red-400 font-bold">Connection Error</h3>
                        <p className="text-slate-400 text-sm mb-4">{error}</p>
                        <p className="text-xs text-slate-500">Renderサーバーが起動中か確認してください。<br/>最初のアクセスは起動に1分ほどかかります。</p>
                        <button onClick={() => window.location.reload()} className="mt-4 bg-slate-700 px-4 py-2 rounded text-sm hover:bg-slate-600">再試行</button>
                    </div>
                );
            }

            return (
                <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-8 animate-fade-in">
                    <div className="relative w-24 h-24">
                        <div className="absolute inset-0 border-4 border-slate-700 rounded-full"></div>
                        <div className="absolute inset-0 border-4 border-amber-500 rounded-full border-t-transparent animate-spin"></div>
                        <Brain className="absolute inset-0 m-auto text-amber-500 w-8 h-8 animate-pulse" />
                    </div>
                    <div className="w-full max-w-xs space-y-2">
                        <div className="flex justify-between text-xs text-amber-400 font-mono">
                            <span>PROCESSING</span>
                            <span>{progress}%</span>
                        </div>
                        <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-amber-500 transition-all duration-300 ease-out" style={{ width: `${progress}%` }} />
                        </div>
                        <p className="text-sm text-slate-400 mt-4 animate-pulse">{status}</p>
                    </div>
                </div>
            );
        };

        const ResultScreen = ({ data, config, onReset }) => {
            const { reasoning, horses, allocations } = data;
            const biasInfo = BIAS_PATTERNS[config.bias];

            return (
                <div className="space-y-6 pb-20 animate-fade-in">
                    <div className="bg-gradient-to-br from-amber-500 to-amber-700 p-0.5 rounded-xl shadow-[0_0_20px_rgba(245,158,11,0.3)]">
                        <div className="bg-slate-900 rounded-[10px] p-5">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h2 className="text-amber-500 text-xs font-bold tracking-widest uppercase mb-1">Logic Turf Decision</h2>
                                    <div className="text-2xl font-bold text-white">勝負の買い目</div>
                                </div>
                                <div className="bg-amber-500 text-slate-900 text-xs font-bold px-2 py-1 rounded">3連複</div>
                            </div>
                            <div className="flex items-center space-x-4 mb-6 bg-slate-800/50 p-3 rounded-lg border border-amber-500/30">
                                <div className="w-10 h-10 bg-amber-500 rounded-full flex items-center justify-center text-slate-900 font-bold text-xl shadow-lg">◎</div>
                                <div>
                                    <div className="text-xs text-amber-400 font-mono">AXIS HORSE</div>
                                    <div className="text-lg font-bold text-white">{horses[0].num}. {horses[0].name}</div>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm text-slate-300">
                                {horses.slice(1).map((h, i) => (
                                    <div key={i} className="flex items-center space-x-2 border-b border-slate-800 py-2">
                                        <span className={`font-bold ${h.type === '○' ? 'text-amber-200' : h.type === '▲' ? 'text-slate-200' : 'text-slate-500'}`}>{h.type}</span>
                                        <span className="font-mono text-slate-500 w-6 text-center">{h.num}</span>
                                        <span className="truncate">{h.name}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <h3 className="text-white font-bold flex items-center"><Info className="w-4 h-4 mr-2 text-emerald-500" /> プロフェッショナル解説</h3>
                        <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 space-y-4 text-sm">
                            <section>
                                <h4 className="text-emerald-400 font-bold text-xs uppercase mb-1">1. センターピン (能力評価)</h4>
                                <p className="text-slate-300 leading-relaxed">{reasoning.centerPin}</p>
                            </section>
                            <div className="h-px bg-slate-700" />
                            <section>
                                <h4 className="text-emerald-400 font-bold text-xs uppercase mb-1">2. 環境・構造 (バイアス/展開)</h4>
                                <p className="text-slate-300 leading-relaxed"><span className="text-amber-400 font-bold mr-1">[{biasInfo.name}]</span>{reasoning.structure}</p>
                            </section>
                            <div className="h-px bg-slate-700" />
                            <section>
                                <h4 className="text-emerald-400 font-bold text-xs uppercase mb-1">3. 血統・適性の裏付け</h4>
                                <p className="text-slate-300 leading-relaxed">{reasoning.bloodline}</p>
                            </section>
                        </div>
                    </div>

                    <div>
                        <h3 className="text-white font-bold flex items-center mb-3"><DollarSign className="w-4 h-4 mr-2 text-emerald-500" /> 資金配分プラン (予算: {config.budget.toLocaleString()}円)</h3>
                        <div className="bg-white rounded-lg overflow-hidden shadow-lg">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-100 text-slate-600 font-bold text-xs uppercase">
                                    <tr>
                                        <th className="px-4 py-3">組合せ</th>
                                        <th className="px-4 py-3">種類</th>
                                        <th className="px-4 py-3 text-right">投資額</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {allocations.map((alloc, i) => (
                                        <tr key={i} className="hover:bg-slate-50">
                                            <td className="px-4 py-3 font-mono font-bold text-slate-800">{alloc.comb.join('-')}</td>
                                            <td className="px-4 py-3 text-slate-500 text-xs">3連複</td>
                                            <td className="px-4 py-3 text-right font-mono font-bold text-emerald-600">¥{alloc.amount.toLocaleString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot className="bg-slate-50 font-bold text-slate-800">
                                    <tr><td className="px-4 py-3" colSpan="2">TOTAL</td><td className="px-4 py-3 text-right">¥{allocations.reduce((acc, cur) => acc + cur.amount, 0).toLocaleString()}</td></tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>

                    <button onClick={onReset} className="w-full bg-slate-800 hover:bg-slate-700 text-slate-400 py-3 rounded-lg flex items-center justify-center space-x-2 transition-colors">
                        <RefreshCw className="w-4 h-4" /> <span>条件を変更して再分析</span>
                    </button>
                </div>
            );
        };

        const App = () => {
            const [step, setStep] = useState(1);
            const [config, setConfig] = useState(null);
            const [result, setResult] = useState(null);

            const handleConfigSubmit = (data) => { setConfig(data); setStep(2); };
            const handleAnalysisComplete = (fetchedData) => {
                const analysisResult = analyzeRace(config.bias, parseInt(config.budget), fetchedData);
                setResult(analysisResult);
                setStep(3);
            };
            const handleReset = () => { setStep(1); setConfig(null); setResult(null); };

            return (
                <div className="min-h-screen text-slate-200 font-sans selection:bg-amber-500/30">
                    <Header />
                    <main className="max-w-md mx-auto p-4 relative">
                        {step === 1 && <ConfigScreen onSubmit={handleConfigSubmit} />}
                        {step === 2 && <ProcessingScreen config={config} onComplete={handleAnalysisComplete} />}
                        {step === 3 && result && <ResultScreen data={result} config={config} onReset={handleReset} />}
                    </main>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
