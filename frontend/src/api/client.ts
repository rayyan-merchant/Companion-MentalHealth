const API_BASE = '/api';

export interface PublicConfig {
    support_email: string;
    provider_processing_enabled: boolean;
    deleted_conversation_retention_days: number;
    security_log_retention_days: number;
    region: string;
}

let configPromise: Promise<PublicConfig> | null = null;

function readCookie(name: string): string | null {
    const prefix = `${encodeURIComponent(name)}=`;
    const part = document.cookie
        .split('; ')
        .find((item) => item.startsWith(prefix));
    return part ? decodeURIComponent(part.slice(prefix.length)) : null;
}

export function getPublicConfig(forceRefresh = false): Promise<PublicConfig> {
    if (forceRefresh) configPromise = null;
    if (!configPromise) {
        configPromise = fetch(`${API_BASE}/config/public`, {
            credentials: 'include'
        }).then(async (response) => {
            if (!response.ok) throw new Error('Could not load app configuration');
            return response.json();
        });
    }
    return configPromise;
}

async function ensureCsrfToken(): Promise<string> {
    await getPublicConfig();
    let csrf = readCookie('companion_csrf');
    if (!csrf) {
        await getPublicConfig(true);
        csrf = readCookie('companion_csrf');
    }
    if (!csrf) {
        throw new ApiError(
            'Unable to initialize request security. Please refresh and try again.',
            0
        );
    }
    return csrf;
}

export class ApiError extends Error {
    constructor(
        message: string,
        public status: number,
        public detail?: unknown
    ) {
        super(message);
    }
}

async function parseError(response: Response): Promise<ApiError> {
    const body = await response.json().catch(() => ({}));
    let message = `Request failed (${response.status})`;
    if (typeof body.detail === 'string') message = body.detail;
    else if (body.detail?.message) message = body.detail.message;
    else if (Array.isArray(body.detail) && body.detail[0]?.msg) {
        message = body.detail[0].msg;
    } else if (body.error) message = body.error;
    return new ApiError(message, response.status, body);
}

export async function apiFetch<T>(
    path: string,
    options: RequestInit = {}
): Promise<T> {
    const method = (options.method || 'GET').toUpperCase();
    const mutating = !['GET', 'HEAD', 'OPTIONS'].includes(method);
    const headers = new Headers(options.headers);
    if (options.body && !headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }
    if (mutating) {
        headers.set('X-CSRF-Token', await ensureCsrfToken());
    }
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        credentials: 'include',
        headers
    });
    if (response.status === 401) {
        window.dispatchEvent(new CustomEvent('companion:unauthorized'));
    }
    if (!response.ok) throw await parseError(response);
    if (response.status === 204) return undefined as T;
    return response.json();
}
