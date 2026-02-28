import { fetchUtils } from "react-admin";

import { API_BASE_URL } from "./common";

export function authHeaders(base?: HeadersInit): Headers {
  const headers = new Headers(base);
  const token = localStorage.getItem("token");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return headers;
}

export const httpClient = (url: string, options: fetchUtils.Options = {}) => {
  return fetchUtils.fetchJson(url, {
    ...options,
    headers: authHeaders(options.headers),
  });
};

export const get = async (
  path: string,
  query?: Record<string, string | number>,
) => {
  const params = new URLSearchParams();
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      params.set(k, String(v));
    }
  }
  const qs = query ? `?${params}` : "";
  const { json } = await fetchUtils.fetchJson(`${API_BASE_URL}${path}${qs}`, {
    headers: authHeaders(),
  });
  return json;
};
