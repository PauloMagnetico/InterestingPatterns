import { useState, useEffect } from "react";
import { fetchTenders } from "./api/tenders";
import TenderCard from "./components/TenderCard";
import SearchBar from "./components/SearchBar";
import "./App.css";

export default function App() {
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchTenders({ ...filters, page })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filters, page]);

  const handleSearch = (newFilters) => {
    setFilters(newFilters);
    setPage(1);
  };

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;

  return (
    <div className="app">
      <header className="app-header">
        <h1>InterestingPatterns</h1>
        <p>Openbare aanbestedingen in België — we tonen enkel interessante patronen</p>
      </header>

      <main>
        <SearchBar onSearch={handleSearch} />

        {loading && <div className="state-msg">Laden...</div>}
        {error && <div className="state-msg error">Fout: {error}</div>}

        {data && !loading && (
          <>
            <div className="results-info">
              {data.total} aanbestedingen gevonden
            </div>
            <div className="tender-list">
              {data.items.map((t) => (
                <TenderCard key={t.id} tender={t} />
              ))}
            </div>
            {totalPages > 1 && (
              <div className="pagination">
                <button onClick={() => setPage((p) => p - 1)} disabled={page === 1}>
                  Vorige
                </button>
                <span>
                  {page} / {totalPages}
                </span>
                <button onClick={() => setPage((p) => p + 1)} disabled={page === totalPages}>
                  Volgende
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
