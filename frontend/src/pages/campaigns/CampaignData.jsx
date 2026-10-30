import React, { useEffect, useRef, useState } from 'react';
import { ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { api } from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import PoultryView from './PoultryView';
import { money, chartRows } from './numbers.mjs';

const base = '/api/v1/campaign-data';
const kinds = { PAYROLL_ALLOC: 'Salaires ventilés', VACCINATION: 'Vaccinations', MEDICATION: 'Soins', MORTALITY: 'Mortalité', SALE: 'Ventes', PURCHASE: 'Achats', EXPENSE: 'Dépenses', CASH: 'Mouvements de caisse', STOCK: 'Mouvements de stock', PRODUCTION: 'Production', FEED: 'Alimentation' };
const labels = { invoice_number: 'N° de facture', purchase_number: 'N° d’achat', expense_number: 'N° de dépense', customer_id: 'Client', supplier_id: 'Fournisseur', subtotal: 'Sous-total', discount: 'Remise', total_amount: 'Montant total', description: 'Description', category: 'Catégorie', amount: 'Montant', account_id: 'Compte de trésorerie', transaction_type: 'Nature du flux', direction: 'Sens', reference_number: 'Référence du paiement', product_id: 'Produit', movement_type: 'Type de mouvement', quantity: 'Quantité', reference_type: 'Document d’origine', reference_id: 'Identifiant du document', unit_cost_snapshot: 'Coût unitaire à la sortie', cost_total_fcfa: 'Coût total de sortie en FCFA', valuation_basis: 'Base de valorisation', flock_id: 'Bande', total_birds: 'Effectif', total_eggs: 'Œufs produits', damaged_eggs: 'Œufs endommagés', good_eggs: 'Bons œufs', quantity_used: 'Quantité consommée', cost_per_unit: 'Coût unitaire d’origine', total_cost: 'Coût total d’origine', date: 'Date métier' };
const issues = { SOURCE_CHANGED: 'Source modifiée après validation', SOURCE_MISSING: 'Source supprimée après validation', UNVALUED_CONSUMPTION: 'Coût de sortie de stock non vérifié', ECONOMIC_CLASSIFICATION_REQUIRED: 'Nature économique à qualifier', STOCK_LINK_MISSING: 'Mouvement de stock manquant', STOCK_ASSIGNMENT_REQUIRED: 'Sortie de stock à rattacher à la même campagne', DOCUMENT_ASSIGNMENT_REQUIRED: 'Document d’origine à rattacher à la même campagne' };
const tabs = { poultry: 'Élevage de poules', coexistence: 'Activités côte à côte', overview: '1. Lire les résultats', sources: '2. Vérifier les sources', valuation: '3. Vérifier les coûts', journal: 'Historique', settings: 'Activités et campagnes' };
issues.CASH_DOCUMENT_LINK_REQUIRED = 'Paiement à rapprocher de son document dans la même campagne';
issues.PAYROLL_RECONCILIATION_REQUIRED = 'Paie ou ventilation salariale à rapprocher';
issues.POULTRY_RECONCILIATION_REQUIRED = 'Quantités ou valeurs avicoles à rapprocher';
issues.SOURCE_PROVENANCE_MISMATCH = 'Origine réelle ou fictive incompatible avec la campagne';
const amount = value => money(value).replace(/ FCFA$/, '');
const today = () => new Date().toLocaleDateString('en-CA');
const errorText = e => typeof e?.response?.data?.detail === 'string' ? e.response.data.detail : 'Impossible de terminer cette opération. Vérifiez les champs et réessayez.';

function useData(path, revision) {
  const [state, setState] = useState({ data: null, loading: false, error: null });
  useEffect(() => {
    const controller = new AbortController();
    setState({ data: null, loading: Boolean(path), error: null });
    if (path) api.get(base + path, { signal: controller.signal }).then(r => {
      if (!controller.signal.aborted) setState({ data: r.data, loading: false, error: null });
    }).catch(e => { if (!controller.signal.aborted) setState({ data: null, loading: false, error: errorText(e) }); });
    return () => controller.abort();
  }, [path, revision]);
  return state;
}

function State({ state }) {
  return state.loading ? <p role="status">Chargement des données…</p> : state.error ? <p role="alert" className="alert alert-danger">{state.error}</p> : null;
}

function DataChart({ rows, series, line = false, quantity = false }) {
  const values = chartRows(rows, series.map(s => s.key));
  if (!rows.length) return <p>Aucune donnée rattachée sur cette période.</p>;
  if (!values) return <p>Montants trop élevés pour un graphique précis. Les valeurs exactes restent disponibles dans le tableau.</p>;
  const Chart = line ? LineChart : BarChart;
  return <div style={{ width: '100%', height: 285 }} role="img" aria-label={series.map(s => s.name).join(', ')}>
    <ResponsiveContainer><Chart data={values} margin={{ left: 15, right: 15 }}>
      <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="period" /><YAxis allowDecimals={false} domain={[min => Math.min(0, min), max => Math.max(0, max)]} tickFormatter={n => new Intl.NumberFormat('fr-FR', { notation: 'compact' }).format(n)} />
      <Tooltip formatter={(value, name) => [quantity ? new Intl.NumberFormat('fr-FR').format(value) + ' œufs' : money(String(value)), name]} /><Legend />
      {series.map(s => line ? <Line key={s.key} type="linear" dataKey={s.key} name={s.name} stroke={s.color} strokeWidth={2} isAnimationActive={false} /> : <Bar key={s.key} dataKey={s.key} name={s.name} fill={s.color} isAnimationActive={false} />)}
    </Chart></ResponsiveContainer>
  </div>;
}

export default function CampaignData() {
  const { user } = useAuth();
  const isAdmin = user?.role_name === 'admin';
  const [tab, setTab] = useState(() => window.location.hash.includes('view=poultry') ? 'poultry' : 'coexistence');
  const [activityFilter, setActivityFilter] = useState('all');
  const [dataScope, setDataScope] = useState('real');
  const [revision, setRevision] = useState(0);
  const [selected, setSelected] = useState([]);
  const [asOf, setAsOf] = useState(today);
  const [kind, setKind] = useState('SALE');
  const [sourceCursor, setSourceCursor] = useState(null);
  const [productCursor, setProductCursor] = useState(null);
  const [eventCursor, setEventCursor] = useState(null);
  const [dialog, setDialog] = useState(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const initialized = useRef(false);
  const validationRef = useRef(null);
  useEffect(() => {
    if (dialog && validationRef.current) {
      validationRef.current.scrollIntoView({ block: 'start' });
      validationRef.current.querySelector('select,input,textarea')?.focus({ preventScroll: true });
    }
  }, [dialog?.operationId]);
  const activities = useData('/activities', revision);
  const campaigns = useData('/campaigns', revision);
  const quality = useData('/quality', revision);
  const report = useData(selected.length && asOf ? '/report?' + new URLSearchParams([...selected.map(id => ['campaign_ids', id]), ['as_of', asOf]]) : null, revision);
  const sources = useData(tab === 'sources' ? `/sources/${kind}?limit=30${sourceCursor ? '&before_id=' + sourceCursor : ''}` : null, revision);
  const products = useData(tab === 'valuation' ? '/valuation/products?limit=30' + (productCursor ? '&before_id=' + productCursor : '') : null, revision);
  const events = useData(tab === 'journal' ? '/events?limit=30' + (eventCursor ? '&before_id=' + eventCursor : '') : null, revision);
  useEffect(() => {
    if (!initialized.current && campaigns.data?.length && activities.data) {
      const demo = activities.data.some(a => a.demo_dataset);
      const ids = activities.data.filter(a => Boolean(a.demo_dataset) === demo).map(a => a.id);
      setDataScope(demo ? 'demo' : 'real');
      setSelected(campaigns.data.filter(c => ids.includes(c.activity_id)).map(c => c.id));
      initialized.current = true;
    }
  }, [campaigns.data, activities.data]);
  const scopedActivities = (activities.data || []).filter(a => Boolean(a.demo_dataset) === (dataScope === 'demo'));
  const visibleActivities = scopedActivities.filter(a => activityFilter === 'all' || String(a.id) === activityFilter);
  function selectActivity(value, scope = dataScope) {
    setActivityFilter(value); setDataScope(scope);
    const ids = (activities.data || []).filter(a => Boolean(a.demo_dataset) === (scope === 'demo') && (value === 'all' || String(a.id) === value)).map(a => a.id);
    setSelected((campaigns.data || []).filter(c => ids.includes(c.activity_id)).map(c => c.id));
  }
  const campaignName = id => campaigns.data?.find(c => c.id === id)?.name || `Campagne #${id}`;
  const refresh = () => setRevision(v => v + 1);
  const open = (action, item) => { setNotice(null); setDialog({ action, item, operationId: crypto.randomUUID(), reason: '', confirmed: false, unitCost: '', campaignId: selected[0] || '' }); };
  const field = (name, value) => setDialog(d => ({ ...d, [name]: value }));

  async function mutate(path, payload, after) {
    if (busy) return;
    setBusy(true); setNotice(null);
    try {
      const { data } = await api.post(base + path, payload);
      after?.(data); setDialog(null); refresh(); setNotice({ ok: true, text: 'Enregistrement confirmé par le serveur.' });
    } catch (e) { setNotice({ ok: false, text: errorText(e) }); }
    finally { setBusy(false); }
  }
  async function submitDialog(e) {
    e.preventDefault();
    const { action, item, operationId, reason, confirmed, campaignId, unitCost } = dialog;
    if (action !== 'release' && !confirmed) return;
    const payload = { client_operation_id: operationId, reason };
    if (action === 'assign') return mutate(`/campaigns/${campaignId}/assignments`, { ...payload, source_type: item.source.type, source_id: item.source.id, source_hash: item.source_hash, confirm_currency: 'XOF' });
    if (action === 'release') return mutate(`/events/${item.assignment.event_id}/release`, payload);
    return mutate(`/valuation/products/${item.id}`, { ...payload, expected_quantity: item.quantity, unit_cost: unitCost, confirm_currency: 'XOF' });
  }
  const data = report.data;
  return <section className="py-4">
    <h1 className="h3">Campagnes et données</h1>
    <p>Une activité, une campagne, des pièces vérifiées. Les campagnes peuvent couvrir plusieurs années et être regroupées ici.</p>
    {notice && <div role={notice.ok ? 'status' : 'alert'} className={`alert alert-${notice.ok ? 'success' : 'danger'}`}>{notice.text}</div>}
    <div className="card p-3 mb-3">
      <div className="d-flex flex-wrap gap-3 align-items-start">
        <fieldset className="flex-grow-1" style={{ minWidth: 0 }}><legend className="h6">Campagnes à analyser</legend>
          <State state={campaigns} />
          <div className="d-flex flex-wrap gap-3 mb-3">
            <label>Périmètre<select className="form-select" value={dataScope} onChange={e => selectActivity('all', e.target.value)}><option value="demo">Démonstration</option><option value="real">Activités réelles</option></select></label>
            <label style={{ minWidth: 0, maxWidth: '100%' }}>Activité à comparer<select className="form-select" value={activityFilter} onChange={e => selectActivity(e.target.value)}><option value="all">Toutes les activités du périmètre</option>{scopedActivities.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}</select></label>
          </div>
          {visibleActivities.map(a => <details key={a.id} open={visibleActivities.length === 1} className="mb-2"><summary>{a.name} · {campaigns.data?.filter(c => c.activity_id === a.id && selected.includes(c.id)).length || 0} campagne(s) sélectionnée(s)</summary><div className="pt-2">{campaigns.data?.filter(c => c.activity_id === a.id).map(c => <label key={c.id} className="d-block mb-2"><input type="checkbox" checked={selected.includes(c.id)} onChange={e => setSelected(ids => e.target.checked ? [...ids, c.id] : ids.filter(id => id !== c.id))} /> {c.name} <small>({c.start_date} → {c.end_date || 'fin ouverte'})</small></label>)}</div></details>)}
          {campaigns.data?.length === 0 && <p>Aucune campagne. Commencez par créer une activité et sa campagne.</p>}
        </fieldset>
        <label>Situation au<input className="form-control" type="date" required value={asOf} onChange={e => setAsOf(e.target.value)} /></label>
        <button className="btn btn-outline-primary mt-4" onClick={refresh} disabled={busy}>Actualiser</button>
      </div>
      <State state={quality} />
      {quality.data && <p className="mb-0 mt-2"><strong>{quality.data.unassigned_total} source(s) non rattachée(s)</strong> dans l’application. L’historique reste à contrôler ; aucune devise ni affectation n’est présumée.</p>}
    </div>
    <nav aria-label="Étapes de validation" className="d-flex flex-wrap gap-2 mb-4">{Object.entries(tabs).map(([key, title]) => <button key={key} className={`btn btn-${tab === key ? 'primary' : 'outline-primary'}`} aria-current={tab === key ? 'page' : undefined} onClick={() => setTab(key)}>{title}</button>)}</nav>

    {(tab === 'overview' || tab === 'coexistence' || tab === 'poultry') && <>
      <State state={report} />
      {!selected.length && <div className="alert alert-info">Sélectionnez une campagne ou créez-en une dans « Activités et campagnes ».</div>}
      {data && <>
        <div className="alert alert-info"><strong>Périmètre partiel : sources rattachées uniquement.</strong> {data.scope} Le résultat est un indicateur de gestion provisoire. La trésorerie affichée correspond aux flux sélectionnés, sans solde d’ouverture.</div>
        {data.quality.issues.length > 0 && <div className="alert alert-warning"><strong>Résultat suspendu : {data.quality.issues.length} contrôle(s) à résoudre.</strong><p>Les totaux ci-dessous décrivent les instantanés enregistrés lors du rattachement ; les sources signalées doivent être rapprochées.</p><ul className="mb-0">{data.quality.issues.slice(0, 20).map((issue, i) => <li key={i}>{issues[issue.type] || issue.type} — {kinds[issue.source_type]} #{issue.source_id}</li>)}</ul>{data.quality.issues.length > 20 && <p>Les autres contrôles sont disponibles dans l’export JSON.</p>}</div>}
        {data.demo_dataset && <div className="alert alert-warning" role="note"><strong>DÉMONSTRATION · données fictives en FCFA.</strong> Jeu initial : 8 activités et 4 campagnes par activité. Les opérations vont jusqu’au 30 octobre 2026. Les scénarios comparent des flux financiers simplifiés ; l’élevage détaille les cycles de ponte et les salaires. La transformation des matières et le float Mobile Money restent simplifiés.</div>}
        {tab === 'poultry' && <PoultryView data={data.poultry} Chart={DataChart} ready={data.quality.result_available} />}
        {tab !== 'poultry' && data.sources.length > 0 && <div className="row g-3 mb-3">{[['Ventes documentées', data.totals.revenue], ['Dépenses documentées', data.totals.expense], ['Stock consommé valorisé', data.totals.consumption], ['Résultat provisoire', data.totals.result_fcfa], ['Flux net de trésorerie', data.totals.cash_net_fcfa]].map(([label, value]) => <div className="col-sm-6 col-xl" key={label}><div className="card h-100 p-3"><span>{label}</span><strong className="mt-2">{value === null ? 'À vérifier' : money(value)}</strong></div></div>)}</div>}
        {tab === 'coexistence' && data.sources.length > 0 && <>
          <h2 className="h4">Comment les activités coexistent</h2>
          <p>Comparez le résultat et la caisse séparément. Les apports ne sont pas des ventes. Une activité excédentaire ne finance pas automatiquement sa voisine.</p>
          <div className="table-responsive card p-3 mb-3"><p className="small">Tous les montants sont en FCFA.</p><table className="table align-middle"><thead><tr>{['Activité','Résultat provisoire','Apports','Flux net après apports','Besoin maximal avant apports','Lecture'].map(h => <th key={h} style={{ whiteSpace: 'normal' }}>{h}</th>)}</tr></thead><tbody>{data.by_activity.map(a => <tr key={a.activity_id}><th scope="row"><button className="btn btn-link p-0 text-start" onClick={() => selectActivity(String(a.activity_id))}>{a.name}</button><small className="d-block">{a.campaign_count} campagnes</small></th><td>{amount(a.result_fcfa)}</td><td>{amount(a.funding_in)}</td><td>{amount(a.cash_net_fcfa)}</td><td>{amount(a.funding_gap_fcfa)}</td><td><span className={`badge bg-${a.status === 'Excédentaire' ? 'success' : a.status === 'Déficitaire' ? 'danger' : 'warning'}`}>{a.status}</span></td></tr>)}</tbody></table><p className="small mb-0">Besoin calculé au creux du cumul journalier des flux rattachés, hors apports/retraits. Aucun solde d’ouverture n’est présumé. Une ligne négative indique un financement manquant dans le scénario.</p></div>
          <div className="card p-3 mb-3"><h2 className="h5">Trésorerie cumulée de chaque activité avant apports</h2>{data.quality.cash_available ? <DataChart line rows={data.activity_monthly} series={data.by_activity.map((a, i) => ({ key: `activity_${a.activity_id}`, name: a.name, color: ['#20866a','#326a9e','#be7043','#8655a3','#9b4343','#6f7d24','#0c8994','#596373'][i % 8] }))} /> : <p>Graphique suspendu : les sources de caisse demandent une vérification.</p>}</div>
          <details className="card p-3 mb-3"><summary>Calendrier des {data.campaigns.length} campagnes : voir les chevauchements</summary><div className="table-responsive mt-3"><table className="table"><thead><tr><th>Activité</th><th>Campagne</th><th>Début</th><th>Fin prévue</th><th>Chronologie des campagnes</th></tr></thead><tbody>{data.campaigns.map(c => { const origin = Date.UTC(Math.min(...data.campaigns.map(x => Number(x.start_date.slice(0,4)))),0,1), span = Date.UTC(Math.max(...data.campaigns.map(x => Number((x.end_date || data.as_of).slice(0,4))))+1,0,1)-origin, begin = Date.parse(c.start_date), end = Date.parse(c.end_date || data.as_of); return <tr key={c.id}><td>{activities.data?.find(a => a.id === c.activity_id)?.name}</td><td>{c.name}</td><td>{c.start_date}</td><td>{c.end_date || 'Ouverte'}</td><td style={{ minWidth: 260 }}><div style={{ height: 14, background: '#e4e7eb', position: 'relative' }}><span title={`${c.start_date} → ${c.end_date || 'fin ouverte'}`} style={{ position: 'absolute', height: 14, background: '#326a9e', left: `${Math.max(0, Math.min(100, (begin-origin)/span*100))}%`, width: `${Math.max(1, Math.min(100, (end-begin)/span*100))}%` }} /></div></td></tr>; })}</tbody></table></div></details>
        </>}
        {!data.sources.length ? <p>Aucune source rattachée à cette date. Vérifiez les sources avant de lire des résultats.</p> : tab === 'overview' ? <>
          <div className="row g-3 mb-3">
            <div className="col-lg-6"><div className="card p-3"><h2 className="h5">Entrées et sorties de caisse</h2><p>Flux rattachés par mois, en FCFA.</p>{data.quality.cash_available ? <DataChart rows={data.monthly} series={[{ key: 'cash_in', name: 'Entrées', color: '#20866a' }, { key: 'cash_out', name: 'Sorties', color: '#be7043' }]} /> : <p>Graphique suspendu : une source de trésorerie a été modifiée ou supprimée.</p>}</div></div>
            <div className="col-lg-6"><div className="card p-3"><h2 className="h5">Évolution du résultat cumulé</h2>{data.quality.result_available ? <DataChart line rows={data.monthly} series={[{ key: 'cumulative_result_fcfa', name: 'Résultat cumulé provisoire', color: '#326a9e' }]} /> : <p>Le graphique du résultat sera disponible lorsque les contrôles seront résolus.</p>}</div></div>
          </div>
          <div className="card p-3 mb-3"><h2 className="h5">Lecture par année</h2><p>Chaque pièce compte une fois, même dans une sélection de plusieurs campagnes. Les bilans annuels ne sont pas additionnés.</p>
            <div className="table-responsive"><table className="table"><thead><tr><th>Année</th><th>Ventes</th><th>Dépenses</th><th>Consommation</th><th>Résultat provisoire</th><th>Flux net de caisse</th></tr></thead><tbody>{data.yearly.map(r => <tr key={r.period}><td>{r.period}</td>{['revenue','expense','consumption','result_fcfa','cash_net_fcfa'].map(k => <td key={k}>{r[k] === null ? 'À vérifier' : money(r[k])}</td>)}</tr>)}</tbody></table></div>
          </div>
          <div className="card p-3 mb-3"><h2 className="h5">Comparer les campagnes</h2>{data.quality.result_available ? <DataChart rows={data.by_campaign.map(c => ({ ...c, period: c.name }))} series={[{ key: 'revenue', name: 'Ventes', color: '#20866a' }, { key: 'expense', name: 'Dépenses', color: '#be7043' }, { key: 'consumption', name: 'Stock consommé', color: '#326a9e' }]} /> : <p>Comparaison suspendue jusqu’à résolution des contrôles.</p>}</div>
        </> : null}
        <button className="btn btn-outline-primary" onClick={() => {
          const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
          const a = document.createElement('a'); a.href = url; a.download = `dakafarm-campagnes-${asOf}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
        }}>Exporter les sources et contrôles (JSON)</button>
      </>}
    </>}

    {tab === 'sources' && <div className="card p-3">
      <h2 className="h5">Rattacher des pièces contrôlées</h2>
      <p>Rattachez séparément le document, son paiement et ses mouvements de stock à la même campagne. Un achat augmente le stock ; seule sa consommation valorisée entre dans les charges. Une pièce entière appartient à une seule campagne.</p>
      <label className="mb-3">Type de source<select className="form-select" value={kind} onChange={e => { setKind(e.target.value); setSourceCursor(null); }}>{Object.entries(kinds).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
      <State state={sources} />
      <div className="table-responsive"><table className="table align-middle"><thead><tr><th>Pièce</th><th>Date</th><th>Valeurs d’origine</th><th>Affectation</th><th>Action</th></tr></thead><tbody>{sources.data?.items.map(item => <tr key={item.source.id}>
        <td>{item.source.label}<small className="d-block">#{item.source.id}</small></td><td>{item.source.date || 'Sans date'}</td>
        <td><details><summary>Consulter les données</summary><dl>{Object.entries(item.source.data).map(([k,v]) => <React.Fragment key={k}><dt>{labels[k] || k}</dt><dd>{v === null ? 'Non renseigné' : String(v)}</dd></React.Fragment>)}</dl></details>{item.issue && <span className="text-danger">{item.issue}</span>}{item.measures?.unvalued > 0 && <small className="d-block text-warning">Coût non vérifié : le résultat restera suspendu.</small>}</td>
        <td>{item.assignment ? <>{campaignName(item.assignment.campaign_id)}<small className="d-block">XOF confirmé{item.assignment.source_changed ? ' · source modifiée !' : ''}</small></> : 'À vérifier · devise non confirmée'}</td>
        <td><button disabled={busy || Boolean(item.issue) && !item.assignment} className="btn btn-sm btn-outline-primary" onClick={() => open(item.assignment ? 'release' : 'assign', item)}>{item.assignment ? 'Libérer pour corriger' : 'Vérifier et rattacher'}</button></td>
      </tr>)}</tbody></table></div>
      {sources.data?.items.length === 0 && <p>Aucune source de ce type sur cette page.</p>}
      <div className="d-flex gap-2"><button className="btn btn-sm btn-outline-secondary" disabled={!sourceCursor} onClick={() => setSourceCursor(null)}>Première page</button><button className="btn btn-sm btn-outline-primary" disabled={!sources.data?.next_cursor} onClick={() => setSourceCursor(sources.data.next_cursor)}>Page suivante</button></div>
    </div>}

    {tab === 'valuation' && <div className="card p-3"><h2 className="h5">Contrôler les coûts d’ouverture</h2>
      <p>Les anciens prix de stock restent non vérifiés. Un administrateur peut déclarer un coût justifié pour la quantité actuelle. Cette déclaration ne revalorise jamais les sorties historiques.</p><State state={products} />
      <div className="table-responsive"><table className="table"><thead><tr><th>Produit</th><th>Stock actuel</th><th>Coût unitaire d’origine</th><th>Qualité du coût</th><th>Action</th></tr></thead><tbody>{products.data?.items.map(p => <tr key={p.id}><td>{p.name}</td><td>{p.quantity} {p.unit}</td><td>{p.unit_cost} · devise à contrôler</td><td>{({ UNVERIFIED: 'Non vérifié', DECLARED: 'Déclaré en XOF', WEIGHTED_AVERAGE: 'Coût moyen calculé' })[p.cost_basis] || p.cost_basis}</td><td>{isAdmin && p.cost_basis === 'UNVERIFIED' && <button className="btn btn-sm btn-outline-primary" onClick={() => open('valuation', p)}>Déclarer le coût</button>}</td></tr>)}</tbody></table></div>
      {products.data?.items.length === 0 && <p>Aucun produit sur cette page.</p>}
      <div className="d-flex gap-2"><button className="btn btn-sm btn-outline-secondary" disabled={!productCursor} onClick={() => setProductCursor(null)}>Première page</button><button className="btn btn-sm btn-outline-primary" disabled={!products.data?.next_cursor} onClick={() => setProductCursor(products.data.next_cursor)}>Page suivante</button></div>
    </div>}

    {tab === 'journal' && <div className="card p-3"><h2 className="h5">Historique des affectations — toutes campagnes</h2><p>Une correction ajoute un événement. Elle ne remplace pas l’affectation précédente.</p><State state={events} />
      <div className="table-responsive"><table className="table"><thead><tr><th>Événement</th><th>Campagne</th><th>Source</th><th>Décision</th><th>Motif / auteur</th></tr></thead><tbody>{events.data?.items.map(e => <tr key={e.id}><td>#{e.id}<small className="d-block">{new Date(e.created_at).toLocaleString('fr-FR')}</small></td><td>{campaignName(e.campaign_id)}</td><td>{kinds[e.source_type]} #{e.source_id}</td><td>{e.action === 'ASSIGN' ? 'Rattachement' : 'Libération'}<small className="d-block">Précédent : {e.previous_event_id || 'aucun'}</small></td><td>{e.reason}<small className="d-block">Utilisateur #{e.actor_id}</small></td></tr>)}</tbody></table></div>
      {events.data?.items.length === 0 && <p>Aucun événement sur cette page.</p>}
      <div className="d-flex gap-2"><button className="btn btn-sm btn-outline-secondary" disabled={!eventCursor} onClick={() => setEventCursor(null)}>Première page</button><button className="btn btn-sm btn-outline-primary" disabled={!events.data?.next_cursor} onClick={() => setEventCursor(events.data.next_cursor)}>Page suivante</button></div>
    </div>}

    {tab === 'settings' && <div className="row g-3"><div className="col-lg-5"><div className="card p-3"><h2 className="h5">Activités</h2><State state={activities} /><ul>{activities.data?.map(a => <li key={a.id}>{a.name} ({a.code}) · {a.currency}</li>)}</ul>
      {isAdmin && <form onSubmit={e => { e.preventDefault(); const f = new FormData(e.currentTarget); mutate('/activities', { code: f.get('code'), name: f.get('name'), currency: 'XOF' }); }}>
        <label className="d-block mb-2">Code<input className="form-control" name="code" required pattern="[A-Z0-9_-]{2,40}" placeholder="AVICULTURE" /></label>
        <label className="d-block mb-2">Nom de l’activité<input className="form-control" name="name" required minLength={2} maxLength={120} placeholder="Aviculture" /></label><p>Devise de cette activité : XOF (FCFA).</p><button disabled={busy} className="btn btn-primary">Créer l’activité</button>
      </form>}
    </div></div><div className="col-lg-7"><div className="card p-3"><h2 className="h5">Nouvelle campagne</h2><p>Exemple : un élevage démarré en 2025 et terminé en 2027.</p>
      {isAdmin ? <form onSubmit={e => { e.preventDefault(); const f = new FormData(e.currentTarget); mutate('/campaigns', { activity_id: Number(f.get('activity_id')), code: f.get('code'), name: f.get('name'), start_date: f.get('start_date'), end_date: f.get('end_date') || null }, c => { initialized.current = true; setSelected([c.id]); setDataScope(activities.data?.find(a => a.id === c.activity_id)?.demo_dataset ? 'demo' : 'real'); setActivityFilter(String(c.activity_id)); }); }}>
        <label className="d-block mb-2">Activité<select name="activity_id" className="form-select" required defaultValue=""><option value="" disabled>Choisir une activité</option>{activities.data?.filter(a => a.is_active).map(a => <option key={a.id} value={a.id}>{a.name}</option>)}</select></label>
        <label className="d-block mb-2">Code<input name="code" className="form-control" required pattern="[A-Z0-9_-]{2,40}" placeholder="PONDEUSES-2025-2027" /></label>
        <label className="d-block mb-2">Nom<input name="name" className="form-control" required minLength={2} maxLength={120} /></label>
        <label className="d-block mb-2">Début<input name="start_date" className="form-control" type="date" required /></label>
        <label className="d-block mb-2">Fin prévue (facultative)<input name="end_date" className="form-control" type="date" /></label>
        <button disabled={busy || !activities.data?.length} className="btn btn-primary">Créer la campagne</button>
      </form> : <p>La création des activités et campagnes est réservée à un administrateur.</p>}
    </div></div></div>}

    {dialog && <div ref={validationRef} className="card border-primary p-4 mt-3" role="region" aria-labelledby="validation-title">
      <h2 className="h5" id="validation-title">{dialog.action === 'assign' ? `Vérifier ${dialog.item.source.label}` : dialog.action === 'release' ? 'Libérer une affectation' : `Valoriser ${dialog.item.name}`}</h2>
      <form onSubmit={submitDialog}>
        {dialog.action === 'assign' && <label className="d-block mb-2">Campagne destinataire<select required className="form-select" value={dialog.campaignId} onChange={e => field('campaignId', e.target.value)}><option value="">Choisir</option>{campaigns.data?.filter(c => c.status === 'OPEN').map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label>}
        {dialog.action === 'valuation' && <><p>Quantité contrôlée : {dialog.item.quantity} {dialog.item.unit}. Les sorties passées restent inchangées.</p><label className="d-block mb-2">Coût unitaire justifié en FCFA<input type="number" step="0.000001" min="0.000001" required className="form-control" value={dialog.unitCost} onChange={e => field('unitCost', e.target.value)} /></label></>}
        {dialog.action === 'release' && <p>La source sera retirée des calculs de {campaignName(dialog.item.assignment.campaign_id)}. L’événement initial restera dans l’historique.</p>}
        <label className="d-block mb-2">Motif et référence du justificatif<textarea className="form-control" required minLength={3} maxLength={1000} value={dialog.reason} onChange={e => field('reason', e.target.value)} /></label>
        {dialog.action !== 'release' && <label className="d-block mb-3"><input type="checkbox" required checked={dialog.confirmed} onChange={e => field('confirmed', e.target.checked)} /> Je confirme que les montants contrôlés sont en XOF (FCFA). Aucune conversion de devise n’est effectuée.</label>}
        <div className="d-flex gap-2"><button className="btn btn-primary" disabled={busy}>{busy ? 'Enregistrement…' : 'Confirmer'}</button><button type="button" className="btn btn-outline-secondary" disabled={busy} onClick={() => setDialog(null)}>Annuler</button></div>
      </form>
    </div>}
  </section>;
}
