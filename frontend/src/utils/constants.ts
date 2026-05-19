/* Agent data, colors, and copy constants */

export const AGENTS = [
  { id: 'ceo',        name: 'CEO',        icon: '🧠', color: '#7c3aed', label: 'STRATEGIC VISION',      stat: 'Competitive landscape mapped in 4.2s' },
  { id: 'research',   name: 'Research',   icon: '🔬', color: '#06b6d4', label: 'MARKET INTELLIGENCE',   stat: '10,000 data points. 47 competitors. 8.3 seconds.' },
  { id: 'marketing',  name: 'Marketing',  icon: '📡', color: '#10b981', label: 'GROWTH WARFARE',        stat: '12 channels. 3 viral hooks. 1 go-to-market strategy.' },
  { id: 'developer',  name: 'Developer',  icon: '⚡', color: '#3b82f6', label: 'CODE ARCHITECTURE',     stat: 'Full-stack blueprint. API-first. Cloud-native.' },
  { id: 'finance',    name: 'Finance',    icon: '💎', color: '#f59e0b', label: 'FINANCIAL MODELING',    stat: '5-year runway. Break-even month 14. Series A ready.' },
  { id: 'analytics',  name: 'Analytics',  icon: '📊', color: '#f97316', label: 'DATA OMNISCIENCE',     stat: 'KPIs tracked. Risks flagged. Pivot points identified.' },
  { id: 'operations', name: 'Operations', icon: '⚙️', color: '#e2e8f0', label: 'OPERATIONAL PRECISION', stat: 'Supply chain. Hiring plan. Launch timeline. Done.' },
] as const;

export const STATS = [
  { value: 1247, suffix: '+', label: 'Startups Launched' },
  { value: 7,    suffix: '',  label: 'AI Agents' },
  { value: 42,   suffix: '',  label: 'Page Reports' },
  { value: 2,    suffix: 'min', label: 'Processing Time', prefix: '<' },
] as const;

export const TESTIMONIALS = [
  { quote: "I went from a napkin idea to a 42-page investor-ready blueprint in 90 seconds. My VC literally asked if I hired McKinsey.", author: "Sarah Chen", role: "Founder, NeuralLeaf" },
  { quote: "Seven AI agents analyzed my market, built my financial model, AND designed my tech architecture. While I was making coffee.", author: "Marcus Rivera", role: "CEO, QuantumFlow" },
  { quote: "StartupOS didn't just save me weeks of work — it found a market opportunity I completely missed. That pivot 3x'd our seed round.", author: "Priya Sharma", role: "CTO, DataHive AI" },
] as const;

export const TERMINAL_LINES = [
  { text: '[SYSTEM] Initializing neural core...', type: 'system' as const, delay: 0 },
  { text: '[CEO] Analyzing business model canvas...', type: 'agent' as const, delay: 200 },
  { text: '[CEO] Identified 3 competitive advantages', type: 'agent' as const, delay: 500 },
  { text: '[CEO] Strategic vision complete ✓', type: 'success' as const, delay: 800 },
  { text: '[RESEARCH] Scanning 10,247 market data points...', type: 'agent' as const, delay: 1100 },
  { text: '[RESEARCH] Market size: $4.2B TAM, 23% CAGR', type: 'highlight' as const, delay: 1400 },
  { text: '[RESEARCH] 47 competitors profiled, 4 direct threats', type: 'highlight' as const, delay: 1700 },
  { text: '[MARKETING] Generating go-to-market strategy...', type: 'agent' as const, delay: 2000 },
  { text: '[MARKETING] 12 acquisition channels evaluated', type: 'agent' as const, delay: 2300 },
  { text: '[DEVELOPER] Architecting full-stack blueprint...', type: 'agent' as const, delay: 2600 },
  { text: '[DEVELOPER] Tech stack: React + FastAPI + PostgreSQL', type: 'highlight' as const, delay: 2900 },
  { text: '[FINANCE] Building 5-year financial model...', type: 'agent' as const, delay: 3200 },
  { text: '[FINANCE] Break-even: Month 14. Seed: $750K', type: 'highlight' as const, delay: 3500 },
  { text: '[ANALYTICS] Running risk assessment...', type: 'agent' as const, delay: 3800 },
  { text: '[OPERATIONS] Generating launch timeline...', type: 'agent' as const, delay: 4100 },
  { text: '[SYSTEM] Blueprint generation complete.', type: 'success' as const, delay: 4400 },
  { text: '[SYSTEM] 42 pages generated in 1m 47s ✓', type: 'success' as const, delay: 4600 },
];

export const NAV_LINKS = [
  { label: 'Platform', href: '#platform' },
  { label: 'Agents', href: '#agents' },
  { label: 'Results', href: '#results' },
  { label: 'Proof', href: '#proof' },
] as const;
