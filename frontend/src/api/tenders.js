const BASE_URL = import.meta.env.VITE_API_URL || "/api";

export async function fetchTenders({ page = 1, pageSize = 20, q, cpv, nuts } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  if (q) params.set("q", q);
  if (cpv) params.set("cpv", cpv);
  if (nuts) params.set("nuts", nuts);

  const res = await fetch(`${BASE_URL}/tenders?${params}`);
  if (!res.ok) throw new Error(`API fout: ${res.status}`);
  return res.json();
}

export async function fetchTender(id) {
  const res = await fetch(`${BASE_URL}/tenders/${id}`);
  if (!res.ok) throw new Error(`API fout: ${res.status}`);
  return res.json();
}

export async function analyzeTender(id) {
  const res = await fetch(`${BASE_URL}/tenders/${id}/analyze`);
  if (!res.ok) throw new Error(`Analyse mislukt: ${res.status}`);
  return res.json();
}
