/**
 * AgentForge AI — API Service
 *
 * Centralized API client with auth headers, error handling, and typed responses.
 */

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// --- Types ---
interface ApiError {
  status: number;
  detail: string;
}

export interface User {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  title: string;
  business_idea: string;
  target_market: string | null;
  budget_range: string | null;
  status: string;
  created_at: string;
  updated_at: string | null;
}

export interface WorkflowStartResponse {
  message: string;
  workflow_id: string;
  websocket_url: string;
}

// --- Auth Token Management ---
function getToken(): string | null {
  return localStorage.getItem('agentforge_token');
}

function setToken(token: string): void {
  localStorage.setItem('agentforge_token', token);
}

function clearToken(): void {
  localStorage.removeItem('agentforge_token');
}

// --- Core Fetch Wrapper ---
async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // Handle specific error codes
    if (response.status === 401) {
      clearToken();
      // Don't redirect automatically — let the caller handle it
    }

    let detail = 'An error occurred';
    try {
      const errorBody = await response.json();
      detail = errorBody.detail || detail;
    } catch {
      // response body might not be JSON
    }

    const error: ApiError = { status: response.status, detail };
    throw error;
  }

  return response.json();
}

// --- Auth API ---
export async function register(email: string, password: string, name?: string) {
  const data = await apiFetch<{ access_token: string; token_type: string }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, name }),
  });
  setToken(data.access_token);
  return data;
}

export async function login(email: string, password: string) {
  const data = await apiFetch<{ access_token: string; token_type: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
}

export function logout() {
  clearToken();
}

export async function getMe(): Promise<User> {
  return apiFetch<User>('/auth/me');
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// --- Projects API ---
export async function createProject(data: {
  title: string;
  business_idea: string;
  target_market?: string;
  budget_range?: string;
}): Promise<Project> {
  return apiFetch<Project>('/projects/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function listProjects(): Promise<{ projects: Project[]; total: number }> {
  return apiFetch('/projects/');
}

export async function getProject(projectId: string): Promise<Project> {
  return apiFetch<Project>(`/projects/${projectId}`);
}

// --- Workflow API ---
export async function startWorkflow(projectId: string): Promise<WorkflowStartResponse> {
  return apiFetch<WorkflowStartResponse>(`/projects/${projectId}/start`, {
    method: 'POST',
  });
}

// --- Share API ---
export interface ShareResponse {
  share_token: string;
  share_url: string;
}

export interface SharedProject {
  title: string;
  business_idea: string;
  target_market: string;
  budget_range: string;
  status: string;
  has_report: boolean;
  report_id: string | null;
}

export async function shareProject(projectId: string): Promise<ShareResponse> {
  return apiFetch<ShareResponse>(`/projects/${projectId}/share`, { method: 'POST' });
}

export async function getSharedProject(shareToken: string): Promise<SharedProject> {
  return apiFetch<SharedProject>(`/shared/${shareToken}`);
}

export function getSharedReportDownloadUrl(shareToken: string): string {
  return `${API_BASE}/shared/${shareToken}/report/download`;
}

// --- Report API ---
export function getReportDownloadUrl(projectId: string): string {
  const token = getToken();
  return `${API_BASE}/projects/${projectId}/report${token ? `?token=${token}` : ''}`;
}

// --- Results API ---
export interface AgentResult {
  name: string;
  status: string;
  output: Record<string, any> | null;
  tokens_used: number;
  execution_time: number;
}

export interface ProjectResults {
  status: string;
  workflow_id?: string;
  started_at?: string;
  completed_at?: string;
  total_tokens?: number;
  total_cost?: number;
  agents: Record<string, AgentResult>;
  message?: string;
}

export interface WorkflowStatus {
  status: string;
  progress: number;
  total_agents: number;
  current_agent: string | null;
  percent: number;
}

export async function getProjectResults(projectId: string): Promise<ProjectResults> {
  return apiFetch<ProjectResults>(`/projects/${projectId}/results`);
}

export async function getWorkflowStatus(projectId: string): Promise<WorkflowStatus> {
  return apiFetch<WorkflowStatus>(`/projects/${projectId}/status`);
}

// --- WebSocket URL Builder ---
export function getWebSocketUrl(workflowId: string): string {
  const wsBase = API_BASE.replace('http://', 'ws://').replace('https://', 'wss://').replace('/api/v1', '');
  return `${wsBase}/api/v1/ws/${workflowId}`;
}

// ─────────── Observability API ───────────

export interface ObservabilityLog {
  id: string;
  workflow_id: string;
  agent_name: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  latency_ms: number;
  model_provider: string;
  model_name: string;
  cost_usd: number;
  status: string;
  error_message: string | null;
  input_preview: string | null;
  output_preview: string | null;
  feedback_score: number | null;
  created_at: string | null;
}

export async function getObservabilityLogs(params?: {
  agent_name?: string; status?: string; limit?: number; offset?: number;
}) {
  const q = new URLSearchParams();
  if (params?.agent_name) q.set('agent_name', params.agent_name);
  if (params?.status) q.set('status', params.status);
  if (params?.limit) q.set('limit', String(params.limit));
  if (params?.offset) q.set('offset', String(params.offset));
  return apiFetch<{ total: number; logs: ObservabilityLog[] }>(
    `/observability/logs?${q.toString()}`
  );
}

export async function getMetrics(days = 30) {
  return apiFetch<Record<string, any>>(`/observability/metrics?days=${days}`);
}

export async function getMetricsByAgent() {
  return apiFetch<Array<Record<string, any>>>('/observability/metrics/by-agent');
}

export async function getMetricsByProvider() {
  return apiFetch<Array<Record<string, any>>>('/observability/metrics/by-provider');
}

export async function submitFeedback(logId: string, score: number) {
  return apiFetch(`/observability/feedback/${logId}?score=${score}`, { method: 'POST' });
}

// ─────────── Knowledge API ───────────

export async function uploadDocument(file: File, projectId?: string) {
  const token = getToken();
  const form = new FormData();
  form.append('file', file);
  if (projectId) form.append('project_id', projectId);
  const res = await fetch(`${API_BASE}/knowledge/upload`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!res.ok) throw { status: res.status, detail: 'Upload failed' };
  return res.json();
}

export async function listDocuments(projectId?: string) {
  const q = projectId ? `?project_id=${projectId}` : '';
  return apiFetch<{ total: number; documents: any[] }>(`/knowledge/documents${q}`);
}

export async function deleteDocument(docId: string) {
  return apiFetch(`/knowledge/documents/${docId}`, { method: 'DELETE' });
}

export async function searchKnowledge(query: string, nResults = 5) {
  return apiFetch<{ query: string; results_count: number; results: any[] }>(
    `/knowledge/search?query=${encodeURIComponent(query)}&n_results=${nResults}`,
    { method: 'POST' }
  );
}

export async function getKnowledgeStats() {
  return apiFetch<Record<string, any>>('/knowledge/stats');
}

// ─────────── Prompt IDE API ───────────

export async function listPromptAgents() {
  return apiFetch<Array<Record<string, any>>>('/prompts/agents');
}

export async function getPromptVersions(agentName: string) {
  return apiFetch<Array<Record<string, any>>>(`/prompts/${agentName}/versions`);
}

export async function createPromptVersion(agentName: string, systemPrompt: string, notes?: string) {
  return apiFetch(`/prompts/${agentName}/versions`, {
    method: 'POST',
    body: JSON.stringify(systemPrompt),
    headers: { 'Content-Type': 'application/json' },
  });
}

export async function activatePromptVersion(agentName: string, versionId: string) {
  return apiFetch(`/prompts/${agentName}/versions/${versionId}/activate`, { method: 'PUT' });
}

// ─────────── Admin API ───────────

export async function getAuditLogs(params?: { action?: string; limit?: number; offset?: number }) {
  const q = new URLSearchParams();
  if (params?.action) q.set('action', params.action);
  if (params?.limit) q.set('limit', String(params.limit));
  if (params?.offset) q.set('offset', String(params.offset));
  return apiFetch<{ total: number; logs: any[] }>(`/admin/audit-logs?${q.toString()}`);
}

export async function getSystemStats() {
  return apiFetch<Record<string, any>>('/admin/system-stats');
}

export async function listUsers() {
  return apiFetch<Array<Record<string, any>>>('/admin/users');
}

export async function updateUserRole(userId: string, role: string) {
  return apiFetch(`/admin/users/${userId}/role?role=${role}`, { method: 'PUT' });
}

// ─────────── Health API ───────────
export async function getHealth() {
  return apiFetch<Record<string, any>>('/../health');
}
