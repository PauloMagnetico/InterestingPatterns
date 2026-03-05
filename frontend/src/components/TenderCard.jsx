export default function TenderCard({ tender }) {
  const fmt = (d) => (d ? new Date(d).toLocaleDateString("nl-BE") : "—");
  const fmtEur = (v) =>
    v ? new Intl.NumberFormat("nl-BE", { style: "currency", currency: "EUR" }).format(v) : "—";

  return (
    <div className="tender-card">
      <div className="tender-source">{tender.source}</div>
      <h3>
        <a href={tender.url} target="_blank" rel="noreferrer">
          {tender.title}
        </a>
      </h3>
      <p className="tender-authority">{tender.contracting_authority}</p>
      <div className="tender-meta">
        <span>Publicatie: {fmt(tender.publication_date)}</span>
        <span>Deadline: {fmt(tender.deadline)}</span>
        <span>Waarde: {fmtEur(tender.estimated_value)}</span>
        {tender.cpv_code && <span>CPV: {tender.cpv_code}</span>}
        {tender.nuts_code && <span>Regio: {tender.nuts_code}</span>}
      </div>
    </div>
  );
}
