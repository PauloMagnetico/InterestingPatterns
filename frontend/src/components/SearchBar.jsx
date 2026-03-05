import { useState } from "react";

export default function SearchBar({ onSearch }) {
  const [q, setQ] = useState("");
  const [cpv, setCpv] = useState("");
  const [nuts, setNuts] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({ q: q.trim() || undefined, cpv: cpv.trim() || undefined, nuts: nuts.trim() || undefined });
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Zoeken..."
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      <input
        type="text"
        placeholder="CPV-code (bijv. 72000000)"
        value={cpv}
        onChange={(e) => setCpv(e.target.value)}
      />
      <select value={nuts} onChange={(e) => setNuts(e.target.value)}>
        <option value="">Alle regio's</option>
        <option value="BE1">Brussel</option>
        <option value="BE2">Vlaanderen</option>
        <option value="BE3">Wallonië</option>
      </select>
      <button type="submit">Zoeken</button>
    </form>
  );
}
