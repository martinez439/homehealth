import { apiGet, apiPost, setAuthToken } from './client';

const TOKEN_KEY = 'homehealth_access_token';
const USER_KEY = 'homehealth_user';

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function storeAuth({ access_token, user }) {
  localStorage.setItem(TOKEN_KEY, access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  setAuthToken(access_token);
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  setAuthToken(null);
}

export async function login(email, password) {
  const result = await apiPost('/api/auth/login', { email, password });
  storeAuth(result);
  return result;
}

export async function loadMe() {
  const user = await apiGet('/api/auth/me');
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  return user;
}

setAuthToken(getStoredToken());
