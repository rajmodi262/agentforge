/**
 * AgentForge AI — Knowledge Base Page
 * 
 * Document upload, RAG search, and knowledge management.
 */

import { useState, useEffect, useRef } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import * as api from '../services/api';
import { colors, spacing, typography, radii, gradients } from '../styles/tokens';

const CARD = { background: colors.bgCard, border: `1px solid ${colors.border}`, borderRadius: radii.lg, padding: spacing.lg } as const;
const EXT_ICONS: Record<string, string> = { '.pdf': '📕', '.md': '📝', '.txt': '📄', '.docx': '📘', '.csv': '📊' };

export default function KnowledgePage() {
  const [docs, setDocs] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    const [d, s] = await Promise.all([
      api.listDocuments().catch(() => ({ documents: [] })),
      api.getKnowledgeStats().catch(() => null),
    ]);
    setDocs(d.documents);
    setStats(s);
  };

  const handleUpload = async (files: FileList | null) => {
    if (!files?.length) return;
    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        await api.uploadDocument(file);
      }
      await loadData();
    } catch { }
    setUploading(false);
  };

  const handleDelete = async (docId: string) => {
    await api.deleteDocument(docId).catch(() => {});
    setDocs(prev => prev.filter(d => d.id !== docId));
  };

  const handleSearch = async () => {
    if (searchQuery.length < 3) return;
    setSearching(true);
    try {
      const data = await api.searchKnowledge(searchQuery);
      setSearchResults(data.results);
    } catch { setSearchResults([]); }
    setSearching(false);
  };

  return (
    <DashboardLayout>
      <div style={{ padding: '2rem 2.5rem', maxWidth: '1000px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: typography.bold, margin: '0 0 0.3rem' }}>🧠 Knowledge Base</h1>
        <p style={{ color: colors.textMuted, fontSize: typography.sm, margin: `0 0 ${spacing.xl}` }}>Upload documents for RAG-powered agent context</p>

        {/* ── Stats ── */}
        {stats && (
          <div style={{ display: 'flex', gap: spacing.md, marginBottom: spacing.xl }}>
            <div style={{ ...CARD, flex: 1, textAlign: 'center' }}>
              <div style={{ fontSize: '1.8rem', fontWeight: typography.bold, color: colors.primary }}>{stats.total_documents}</div>
              <div style={{ fontSize: typography.xs, color: colors.textMuted }}>Documents</div>
            </div>
            <div style={{ ...CARD, flex: 1, textAlign: 'center' }}>
              <div style={{ fontSize: '1.8rem', fontWeight: typography.bold, color: colors.cyan }}>{stats.total_chunks}</div>
              <div style={{ fontSize: typography.xs, color: colors.textMuted }}>Chunks</div>
            </div>
            <div style={{ ...CARD, flex: 1, textAlign: 'center' }}>
              <div style={{ fontSize: '1.8rem', fontWeight: typography.bold, color: colors.emerald }}>{stats.rag_status?.total_documents ?? 0}</div>
              <div style={{ fontSize: typography.xs, color: colors.textMuted }}>In Vector DB</div>
            </div>
          </div>
        )}

        {/* ── Upload Zone ── */}
        <div
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={e => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files); }}
          onClick={() => fileRef.current?.click()}
          style={{
            ...CARD,
            textAlign: 'center',
            padding: '2.5rem',
            marginBottom: spacing.xl,
            cursor: 'pointer',
            borderStyle: 'dashed',
            borderColor: dragOver ? colors.primary : 'rgba(255,255,255,0.1)',
            background: dragOver ? 'rgba(124,58,237,0.08)' : 'rgba(255,255,255,0.02)',
            transition: 'all 0.2s',
          }}
        >
          <input ref={fileRef} type="file" multiple accept=".pdf,.md,.txt,.docx,.csv" style={{ display: 'none' }} onChange={e => handleUpload(e.target.files)} />
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>{uploading ? '⏳' : '📂'}</div>
          <div style={{ color: colors.white, fontWeight: typography.semibold, marginBottom: '0.3rem' }}>
            {uploading ? 'Uploading & Chunking...' : 'Drop files here or click to upload'}
          </div>
          <div style={{ color: colors.textMuted, fontSize: typography.sm }}>
            Supports PDF, Markdown, TXT, DOCX, CSV
          </div>
        </div>

        {/* ── Search ── */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <input
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Search knowledge base..."
            style={{
              flex: 1, padding: '0.6rem 1rem', background: 'rgba(255,255,255,0.05)',
              border: `1px solid ${colors.border}`, borderRadius: radii.md,
              color: colors.white, fontSize: typography.sm, outline: 'none',
            }}
          />
          <button onClick={handleSearch} disabled={searching} style={{
            padding: '0.6rem 1.2rem', background: gradients.hero,
            border: 'none', borderRadius: radii.md, color: colors.white, fontWeight: typography.semibold, fontSize: typography.sm, cursor: 'pointer',
          }}>
            {searching ? '...' : '🔍 Search'}
          </button>
        </div>

        {/* ── Search Results ── */}
        {searchResults.length > 0 && (
          <div style={{ ...CARD, marginBottom: spacing.xl }}>
            <h3 style={{ fontSize: typography.sm, fontWeight: typography.semibold, margin: '0 0 1rem', color: colors.cyan }}>
              Search Results ({searchResults.length})
            </h3>
            {searchResults.map((r, i) => (
              <div key={i} style={{ padding: '0.75rem', borderBottom: `1px solid ${colors.borderHover}`, fontSize: typography.sm, color: colors.textMuted }}>
                {typeof r === 'string' ? r : JSON.stringify(r).slice(0, 200)}
              </div>
            ))}
          </div>
        )}

        {/* ── Document List ── */}
        <h3 style={{ fontSize: '0.95rem', fontWeight: typography.semibold, marginBottom: '0.75rem' }}>
          Documents ({docs.length})
        </h3>
        {docs.length === 0 ? (
          <div style={{ ...CARD, textAlign: 'center', padding: '3rem', color: colors.textDark }}>
            No documents uploaded yet. Upload files to power your agents with knowledge.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {docs.map(doc => (
              <div key={doc.id} style={{ ...CARD, display: 'flex', alignItems: 'center', gap: spacing.md, padding: '1rem 1.25rem' }}>
                <span style={{ fontSize: '1.5rem' }}>{EXT_ICONS[doc.extension] || '📄'}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: typography.semibold, fontSize: typography.sm, color: colors.white }}>{doc.filename}</div>
                  <div style={{ fontSize: typography.xs, color: colors.textMuted }}>
                    {doc.chunks} chunks · {(doc.file_size / 1024).toFixed(1)}KB · {new Date(doc.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
                <span style={{ fontSize: '0.7rem', color: colors.emerald, padding: '0.2rem 0.5rem', background: 'rgba(16,185,129,0.1)', borderRadius: '1rem' }}>
                  {doc.stored_in_rag} embedded
                </span>
                <button onClick={() => handleDelete(doc.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: colors.error, fontSize: typography.sm }}>✕</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
