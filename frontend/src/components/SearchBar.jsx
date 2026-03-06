import { useState } from "react";
import BelgiumMap from "./BelgiumMap";

export default function SearchBar({ onSearch, total, loading }) {
  const [q, setQ] = useState("");
  const [cpv, setCpv] = useState("");
  const [nuts, setNuts] = useState("");
  const [awardedOnly, setAwardedOnly] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({
      q: q.trim() || undefined,
      cpv: cpv.trim() || undefined,
      nuts: nuts || undefined,
      awardedOnly: awardedOnly || undefined,
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
        <label>Regio</label>
        <BelgiumMap value={nuts} onChange={setNuts} />
        {nuts && (
          <p className="nuts-selected">
            {nuts === "BE1" ? "Brussels Hoofdstedelijk Gewest" : nuts === "BE2" ? "Vlaanderen" : "Wallonië"}
          </p>
        )}
      </div>

      <div className="filter-group filter-toggle">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={awardedOnly}
            onChange={(e) => setAwardedOnly(e.target.checked)}
            className="toggle-checkbox"
          />
          <span className="toggle-text">Enkel gegunde opdrachten</span>
        </label>
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
