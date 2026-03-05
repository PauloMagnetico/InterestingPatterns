import { useState, useEffect } from "react";
import { fetchTenders } from "./api/tenders";
import TenderCard from "./components/TenderCard";
import SearchBar from "./components/SearchBar";
import "./App.css";

const PAGE_SIZE = 25;

export default function App() {
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchTenders({ ...filters, page, pageSize: PAGE_SIZE })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filters, page]);

  const handleSearch = (newFilters) => {
    setFilters(newFilters);
    setPage(1);
  };

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  return (
    <div className="app">
      <header className="app-header">
        <p className="header-eyebrow">Belgisch Aanbestedingsregister</p>
        <h1>InterestingPatterns</h1>
        <p className="header-tagline">
          — wij tonen enkel interessante patronen
        </p>
        <div className="header-meta">
          <div>src: TED / e-Notification</div>
          <div>scope: BE — alle gewesten</div>
          <div>{new Date().toLocaleDateString("nl-BE", { dateStyle: "long" })}</div>
        </div>
      </header>

      <div className="app-body">
        <aside className="sidebar">
          <SearchBar
            onSearch={handleSearch}
            total={data?.total ?? null}
            loading={loading}
          />
        </aside>

        <main className="main-content">
          {loading && (
            <div className="state-msg loading">dossiers ophalen</div>
          )}
          {error && !loading && (
            <div className="state-msg error">[ fout ] {error}</div>
          )}
          {!loading && data && data.items.length === 0 && (
            <div className="state-msg">geen dossiers gevonden</div>
          )}
          {!loading && data && data.items.length > 0 && (
            <>
              <div className="tender-list">
                {data.items.map((t) => (
                  <TenderCard key={t.id} tender={t} />
                ))}
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    onClick={() => setPage((p) => p - 1)}
                    disabled={page === 1}
                  >
                    ← vorige
                  </button>
                  <span className="pagination-info">
                    {page} / {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page === totalPages}
                  >
                    volgende →
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
