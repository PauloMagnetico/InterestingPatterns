function fmt(d) {
  if (!d) return "—";
  return new Date(d).toLocaleDateString("nl-BE", { day: "2-digit", month: "short", year: "numeric" });
}

function fmtEur(v) {
  if (!v) return null;
  if (v >= 1_000_000)
    return `€ ${(v / 1_000_000).toFixed(2).replace(".", ",")} M`;
  if (v >= 1_000)
    return `€ ${(v / 1_000).toFixed(0)} K`;
  return `€ ${v}`;
}

function isNear(d) {
  if (!d) return false;
  const days = (new Date(d) - Date.now()) / 86_400_000;
  return days >= 0 && days <= 14;
}

export default function TenderCard({ tender }) {
  const value = fmtEur(tender.estimated_value);
  const deadlineNear = isNear(tender.deadline);

  return (
    <article className="tender-card">
      <div className="card-top">
        <a
          className="card-title"
          href={tender.url}
          target="_blank"
          rel="noreferrer"
        >
          {tender.title}
        </a>
        <div className="card-badges">
          <span className="badge badge-source">{tender.source}</span>
          {tender.nuts_code && (
            <span className="badge badge-nuts">{tender.nuts_code}</span>
          )}
          {tender.cpv_code && (
            <span className="badge badge-cpv">{tender.cpv_code}</span>
          )}
        </div>
      </div>

      <p className="card-authority">{tender.contracting_authority}</p>

      <div className="card-footer">
        <div className="card-stat">
          <span className="card-stat-label">Publicatie</span>
          <span className="card-stat-value">{fmt(tender.publication_date)}</span>
        </div>
        <div className="card-stat">
          <span className="card-stat-label">Deadline</span>
          <span className={`card-stat-value ${deadlineNear ? "deadline-near" : ""}`}>
            {fmt(tender.deadline)}
            {deadlineNear && " ⚠"}
          </span>
        </div>
        {value && (
          <div className="card-stat">
            <span className="card-stat-label">Geraamde waarde</span>
            <span className="card-stat-value highlight">{value}</span>
          </div>
        )}
      </div>
    </article>
  );
}
