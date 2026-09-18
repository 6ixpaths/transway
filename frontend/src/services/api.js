const API_BASE_URL = process.env.API_BASE_URL.replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'unknown', address = null, fieldErrors = null } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.address = address;
    this.fieldErrors = fieldErrors;
  }

  get isRetryable() {
    return this.status === 0 || this.status >= 500;
  }
}

export async function optimizeRoute(stops, { signal } = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/routes/optimize/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ stops }),
      signal,
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new ApiError('Could not reach the Transway API. Is the backend running?', { code: 'network' });
  }

  const body = await response.json().catch(() => null);
  if (response.ok) return body;
  throw toApiError(response.status, body);
}

function toApiError(status, body) {
  const isObject = body && typeof body === 'object';

  if (status === 400 && isObject && !body.detail) {
    const messages = Object.values(body).flat().map(String);
    return new ApiError(messages[0] || 'The request was rejected.', {
      status,
      code: 'validation',
      fieldErrors: body,
    });
  }

  const fallback = status >= 500 ? 'The route service is unavailable right now.' : 'The request could not be completed.';
  return new ApiError((isObject && body.detail) || fallback, {
    status,
    code: (isObject && body.code) || 'unknown',
    address: (isObject && body.address) || null,
  });
}
