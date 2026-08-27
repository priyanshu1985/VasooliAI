/**
 * API Client wrapper for AI Revenue Recovery FastAPI backend.
 * Data contract matches docs/design.md section 5.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });

    if (!res.ok) {
      const errorBody = await res.text();
      throw new Error(`HTTP ${res.status}: ${errorBody || res.statusText}`);
    }

    return await res.json();
  } catch (err) {
    console.error(`[API Error] ${endpoint}:`, err);
    throw err;
  }
}

/**
 * GET /api/overview
 * Contract: { total_payments, total_recovered, recovery_rate, diagnosis_accuracy, funnel: {...} }
 */
export async function getOverview() {
  return request('/api/overview');
}

/**
 * GET /api/stage1
 * Contract: { confusion_matrix: [[...]], labels: [...], feature_importance: [{feature, importance}] }
 */
export async function getStage1Metrics() {
  return request('/api/stage1');
}

/**
 * GET /api/stage2
 * Contract: { naive_recovery_rate, smart_recovery_rate, stopping_rule_violations: 0 }
 */
export async function getStage2Metrics() {
  return request('/api/stage2');
}

/**
 * GET /api/stage3
 * Contract: { promises_kept, promises_broken, escalation_funnel: {...} }
 */
export async function getStage3Metrics() {
  return request('/api/stage3');
}

/**
 * GET /api/audit
 * Contract: { rows: [{timestamp, stage, payment_id, decision, reasoning, outcome}], total_count }
 */
export async function getAuditTrail(params = {}) {
  const query = new URLSearchParams(params).toString();
  const endpoint = query ? `/api/audit?${query}` : '/api/audit';
  return request(endpoint);
}

/**
 * GET /health
 */
export async function checkHealth() {
  return request('/health');
}
