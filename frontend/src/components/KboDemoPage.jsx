import { useState } from "react";
import { fetchKbo } from "../api/tenders";

export default function KboDemoPage({ onClose }) {
  const [kboInput, setKboInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLookup = async (e) => {
    e.preventDefault();
    const clean = kboInput.trim().replace(/\D/g, "");
    if (!clean) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await fetchKbo(clean);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="kbo-demo-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="kbo-demo-panel">
        <div className="kbo-demo-header">
          <div>
            <p className="kbo-demo-eyebrow">KBO — Kruispuntbank van Ondernemingen</p>
            <h2>Organisatierollen opzoeken</h2>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleLookup} className="kbo-demo-form">
          <input
            type="text"
            placeholder="KBO-nummer (bijv. 0887229108 of BE 0887.229.108)"
            value={kboInput}
            onChange={(e) => setKboInput(e.target.value)}
            className="kbo-demo-input"
          />
          <button type="submit" className="kbo-demo-btn" disabled={loading}>
            {loading ? "Ophalen..." : "Opzoeken"}
          </button>
        </form>

        {error && (
          <div className="kbo-demo-error">
            Fout: {error}
          </div>
        )}

        {result && (
          <div className="kbo-demo-result">
            <div className="kbo-result-header">
              <div>
                <h3>{result.name || "Onbekend"}</h3>
                <div className="kbo-result-meta">
                  <span className="kbo-badge">{result.kbo_number}</span>
                  {result.legal_form && <span className="kbo-badge kbo-badge-gray">{result.legal_form}</span>}
                  {result.status && (
                    <span className={`kbo-badge ${result.status.toLowerCase().includes("actief") ? "kbo-badge-green" : "kbo-badge-red"}`}>
                      {result.status}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {result.mandataries.length === 0 ? (
              <p className="kbo-empty">Geen mandatarissen gevonden in KBO.</p>
            ) : (
              <table className="kbo-table">
                <thead>
                  <tr>
                    <th>Naam</th>
                    <th>Functie</th>
                    <th>Sinds</th>
                  </tr>
                </thead>
                <tbody>
                  {result.mandataries.map((m, i) => (
                    <tr key={i}>
                      <td className="kbo-name">{m.name}</td>
                      <td>{m.role}</td>
                      <td className="kbo-since">{m.since || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
