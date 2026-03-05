import { useState } from "react";

export default function SearchBar({ onSearch, total, loading }) {
  const [q, setQ] = useState("");
  const [cpv, setCpv] = useState("");
  const [nuts, setNuts] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({
      q: q.trim() || undefined,
      cpv: cpv.trim() || undefined,
      nuts: nuts.trim() || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <p className="sidebar-label">// filter dossiers</p>

      <div className="filter-group">
        <label htmlFor="q">Zoekterm</label>
        <input
          id="q"
          type="text"
          placeholder="bijv. wegenbouw, ICT..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="cpv">CPV-code</label>
        <input
          id="cpv"
          type="text"
          placeholder="bijv. 72000000"
          value={cpv}
          onChange={(e) => setCpv(e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="nuts">Regio</label>
        <select id="nuts" value={nuts} onChange={(e) => setNuts(e.target.value)}>
          <option value="">Heel België</option>
          <option value="BE1">BE1 — Brussels</option>
          <option value="BE2">BE2 — Vlaanderen</option>
          <option value="BE3">BE3 — Wallonië</option>
        </select>
      </div>

      <button type="submit" className="search-btn" disabled={loading}>
        {loading ? "Zoeken..." : "Zoek dossiers"}
      </button>

      <hr className="sidebar-divider" />

      <div className="results-count">
        {total !== null && (
          <>dossiers gevonden: <span>{total.toLocaleString("nl-BE")}</span></>
        )}
      </div>
    </form>
  );
}
