import type { CurrentUser, Token} from '../types'

const API_BASE_URL = 'http://127.0.0.1:8000/'

async function request<T>(
    path: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    headers?: HeadersInit,
    body?: unknown,
): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        method,
        headers: {
            ...(body !== undefined
                ? { 'Content-Type': 'application/json' }
                : {}),
            ...headers,
        },
        body: body !== undefined
            ? JSON.stringify(body)
            : undefined,
    })

    if (!response.ok) {
        const error = await response.json().catch(() => null)
        const message = error?.detail ?? `Request failed with status ${response.status}`

        throw new Error(message)
    }

    return response.json() as Promise<T>
}

export async function login(email: string, password: string): Promise<Token> {
    const response = await request<Token>('users/login', 'POST', {}, {
            "email": email,
            "password": password,
            "remember_me": false
        }
    )
    localStorage.setItem('token', response.access_token)
    return response
}

export async function logout(): Promise<void> {
    localStorage.removeItem('token')
}

export async function getCurrentUser(): Promise<CurrentUser> {
    const token = localStorage.getItem('token')
    if (!token) {
        throw new Error('No token found')
    }

    const response = await request<CurrentUser>('users/me', 'GET', {
        'Authorization': `Bearer ${token}`
    })
    return response
}
