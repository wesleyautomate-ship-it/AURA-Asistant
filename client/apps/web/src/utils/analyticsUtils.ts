import type { Property } from '../store/propertyStore';

export type DateRange = { start: Date; end: Date };

export function filterByDateRange<T extends { createdAt?: string; updatedAt?: string }>(items: T[], range?: DateRange): T[] {
  if (!range) return items;
  const start = range.start.getTime();
  const end = range.end.getTime();
  return items.filter(i => {
    const ts = i.updatedAt || i.createdAt;
    if (!ts) return true;
    const t = new Date(ts).getTime();
    return t >= start && t <= end;
  });
}

export function computeComps(subject: Property, candidates: Property[], opts?: { maxDistanceKm?: number; bedTolerance?: number; bathTolerance?: number; sqftTolerancePct?: number }) {
  const { bedTolerance = 1, bathTolerance = 1, sqftTolerancePct = 0.2 } = opts || {};
  const sqft = subject.sqft || 0;
  const lowSqft = sqft ? sqft * (1 - sqftTolerancePct) : 0;
  const highSqft = sqft ? sqft * (1 + sqftTolerancePct) : Number.MAX_SAFE_INTEGER;
  return candidates.filter(c => {
    const bedOk = subject.beds == null || c.beds == null ? true : Math.abs((c.beds || 0) - (subject.beds || 0)) <= bedTolerance;
    const bathOk = subject.baths == null || c.baths == null ? true : Math.abs((c.baths || 0) - (subject.baths || 0)) <= bathTolerance;
    const sqftOk = c.sqft == null || sqft === 0 ? true : (c.sqft >= lowSqft && c.sqft <= highSqft);
    return bedOk && bathOk && sqftOk;
  });
}

export function pricePerSqft(p?: Property): number | null {
  if (!p || !p.price || !p.sqft || p.sqft === 0) return null;
  return p.price / p.sqft;
}

export function summarizeComps(comps: Property[]) {
  const prices = comps.map(c => c.price).filter((v): v is number => typeof v === 'number');
  const pps = comps.map(c => pricePerSqft(c) ?? undefined).filter((v): v is number => typeof v === 'number');
  const avg = (arr: number[]) => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
  const median = (arr: number[]) => {
    if (!arr.length) return 0;
    const s = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(s.length / 2);
    return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
  };
  return {
    count: comps.length,
    averagePrice: avg(prices),
    medianPrice: median(prices),
    averagePricePerSqft: avg(pps),
    medianPricePerSqft: median(pps),
  };
}

export function recommendStrategy(subject: Property, comps: Property[]) {
  const summary = summarizeComps(comps);
  const subjectPps = pricePerSqft(subject);
  if (subjectPps == null || summary.medianPricePerSqft === 0) {
    return { strategy: 'standard', rationale: 'Insufficient data for PPS comparison.' };
  }
  const diffPct = (subjectPps - summary.medianPricePerSqft) / summary.medianPricePerSqft;
  if (diffPct <= -0.05) return { strategy: 'aggressive', rationale: 'Subject PPS below market median; room to price higher.' };
  if (diffPct >= 0.05) return { strategy: 'standard', rationale: 'Subject PPS above market median; consider standard pricing.' };
  return { strategy: 'standard', rationale: 'Subject PPS near market; standard strategy advised.' };
}

export function exportCSV(rows: Array<Record<string, any>>): string {
  if (!rows.length) return '';
  const headers = Object.keys(rows[0]);
  const escape = (v: any) => {
    const s = String(v ?? '');
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
      return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  };
  const lines = [headers.join(',')].concat(rows.map(r => headers.map(h => escape(r[h])).join(',')));
  return lines.join('\n');
}


