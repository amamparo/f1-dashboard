import { fetchUtils } from "react-admin";

import { API_BASE_URL } from "./common";

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
  const { json } = await fetchUtils.fetchJson(`${API_BASE_URL}${path}${qs}`);
  return json;
};
