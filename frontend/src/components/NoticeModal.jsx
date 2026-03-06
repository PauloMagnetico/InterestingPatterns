import { useState, useEffect } from "react";
import { fetchNotice } from "../api/tenders";

const ROLE_LABEL = {
  buyer: "Opdrachtgever",
  winner: "Winnaar",
  tenderer: "Inschrijver",
};

const ROLE_CLASS = {
  buyer: "role-buyer",
  winner: "role-winner",
  tenderer: "role-tenderer",
};

function RoleBadge({ role }) {
  return (
    <span className={`notice-role-badge ${ROLE_CLASS[role] ?? ""}`}>
      {ROLE_LABEL[role] ?? role}
    </span>
  );
}

export default function NoticeModal({ tender, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNotice(tender.id)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [tender.id]);

  // Close on backdrop click
  function handleBackdrop(e) {
    if (e.target === e.currentTarget) onClose();
  }

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onClick={handleBackdrop}>
      <div className="modal">
        <div className="modal-header">
          <div>
            <p className="modal-eyebrow">Analyse — {tender.id}</p>
            <h2 className="modal-title">{tender.title}</h2>
            <p className="modal-authority">{tender.contracting_authority}</p>
          </div>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {loading && (
            <p className="modal-state loading">organisaties ophalen via KBO</p>
          )}
          {error && !loading && (
            <p className="modal-state error">[ fout ] {error}</p>
          )}

          {!loading && data && (
            <>
              {/* Overlap alert */}
              {data.overlaps.length > 0 && (
                <section className="modal-section overlap-alert">
                  <h3 className="modal-section-title alert-title">
                    Overlappende personen — {data.overlaps.length} gevonden
                  </h3>
                  <div className="overlap-list">
                    {data.overlaps.map((o, i) => (
                      <div key={i} className="overlap-row">
                        <span className="overlap-name">{o.name}</span>
                        <div className="overlap-detail">
                          <span className="overlap-side buyer-side">
                            {o.buyer_role} bij {o.buyer_org}
                            {o.buyer_org_kbo && <span className="kbo-num"> ({o.buyer_org_kbo})</span>}
                          </span>
                          <span className="overlap-arrow">↔</span>
                          <span className="overlap-side winner-side">
                            {o.winner_role} bij {o.winner_org}
                            {o.winner_org_kbo && <span className="kbo-num"> ({o.winner_org_kbo})</span>}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {data.overlaps.length === 0 && (
                <section className="modal-section">
                  <p className="modal-state no-overlap">Geen overlappende personen gevonden</p>
                </section>
              )}

              {/* Organisations */}
              <section className="modal-section">
                <h3 className="modal-section-title">Betrokken organisaties</h3>
                <div className="org-list">
                  {data.organisations.map((org) => (
                    <div key={org.internal_id} className="org-card">
                      <div className="org-header">
                        <span className="org-name">{org.name}</span>
                        <div className="org-roles">
                          {org.roles.map((r) => <RoleBadge key={r} role={r} />)}
                        </div>
                      </div>
                      <div className="org-meta">
                        {org.kbo_number && (
                          <span className="org-meta-item">KBO {org.kbo_number}</span>
                        )}
                        {org.city && (
                          <span className="org-meta-item">{org.city}{org.country && org.country !== "BEL" ? `, ${org.country}` : ""}</span>
                        )}
                        {org.kbo_status && (
                          <span className={`org-meta-item status-${org.kbo_status.toLowerCase()}`}>
                            {org.kbo_status}
                          </span>
                        )}
                        {org.awarded_amounts.length > 0 && (
                          <span className="org-meta-item org-amount">
                            {org.awarded_amounts.map((a) =>
                              a >= 1_000_000
                                ? `€ ${(a / 1_000_000).toFixed(2).replace(".", ",")} M`
                                : `€ ${(a / 1_000).toFixed(0)} K`
                            ).join(", ")}
                          </span>
                        )}
                      </div>
                      {org.mandataries && org.mandataries.length > 0 && (
                        <div className="mandatary-list">
                          {org.mandataries.map((m, i) => (
                            <div key={i} className="mandatary-row">
                              <span className="mandatary-name">{m.name}</span>
                              <span className="mandatary-role">{m.role}</span>
                              {m.since && <span className="mandatary-since">sinds {m.since}</span>}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
