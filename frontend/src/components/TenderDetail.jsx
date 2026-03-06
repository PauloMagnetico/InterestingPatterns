import { useState, useEffect } from "react";
import { analyzeTender } from "../api/tenders";

function OrgCard({ org, overlapNames, role }) {
  return (
    <div className="org-card">
      <div className="org-card-header">
        <span className="org-role-label">{role}</span>
        <h3 className="org-name">{org.name}</h3>
        {org.company_number && (
          <span className="org-number">{org.company_number}</span>
        )}
      </div>
      {org.board.length > 0 ? (
        <ul className="board-list">
          {org.board.map((member, i) => {
            const isOverlap = overlapNames.has(member.name);
            return (
              <li key={i} className={`board-member ${isOverlap ? "board-member--overlap" : ""}`}>
                <span className="member-name">{member.name}</span>
                {member.role && (
                  <span className="member-role">{member.role}</span>
                )}
                {isOverlap && (
                  <span className="overlap-tag" title="Bestuurder ook actief bij andere betrokken organisatie">
                    overlap
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="board-empty">Geen bestuurders gevonden</p>
      )}
    </div>
  );
}

export default function TenderDetail({ tender, onClose }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setAnalysis(null);
    analyzeTender(tender.id)
      .then(setAnalysis)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [tender.id]);

  const overlapNames = new Set(
    (analysis?.board_overlaps ?? []).map((o) => o.person_name)
  );

  return (
    <div className="detail-overlay" onClick={onClose}>
      <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
        <div className="detail-header">
          <div className="detail-title-block">
            <h2 className="detail-title">{tender.title}</h2>
            <span className="detail-id">{tender.id}</span>
          </div>
          <button className="detail-close" onClick={onClose} aria-label="Sluiten">
            &times;
          </button>
        </div>

        <div className="detail-body">
          {loading && (
            <div className="state-msg loading">bestuur ophalen via registers...</div>
          )}
          {error && !loading && (
            <div className="state-msg error">[ fout ] {error}</div>
          )}
          {!loading && analysis && (
            <>
              {analysis.note && (
                <p className="detail-note">{analysis.note}</p>
              )}

              <div className="orgs-grid">
                <OrgCard
                  org={analysis.contracting_authority}
                  overlapNames={overlapNames}
                  role="Aanbestedende overheid"
                />
                {analysis.awarded_parties.map((org, i) => (
                  <OrgCard
                    key={i}
                    org={org}
                    overlapNames={overlapNames}
                    role="Gegunde partij"
                  />
                ))}
              </div>

              {analysis.board_overlaps.length > 0 && (
                <div className="overlaps-section">
                  <h4 className="overlaps-title">Overlappende bestuurders</h4>
                  <ul className="overlaps-list">
                    {analysis.board_overlaps.map((o, i) => (
                      <li key={i} className="overlap-item">
                        <span className="overlap-person">{o.person_name}</span>
                        <span className="overlap-orgs">
                          {o.organizations.join(" — ")}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
