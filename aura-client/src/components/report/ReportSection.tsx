/**
 * Report Section Component
 * ========================
 * 
 * Renders typed section variants for all content types
 * Supports CMA, Pitch Deck, Market Report, Newsletter sections
 * 
 * Version: 3.2
 * Phase: Track 2.4 - Rendering Components
 */

import React, { memo } from 'react';
import { Section } from '../../types/contentSchemas';

interface ReportSectionProps {
  section: Section;
  index: number;
}

export const ReportSection: React.FC<ReportSectionProps> = memo(({ section, index }) => {
  const renderContent = () => {
    // Handle different section types
    switch (section.type) {
      case 'header':
        return renderHeader();
      case 'property-overview':
        return renderPropertyOverview();
      case 'market-analysis':
        return renderMarketAnalysis();
      case 'comparables':
        return renderComparables();
      case 'valuation':
        return renderValuation();
      case 'insights':
        return renderInsights();
      case 'chart':
        return renderChart();
      case 'table':
        return renderTable();
      case 'text':
        return renderText();
      case 'bullets':
        return renderBullets();
      case 'metrics':
        return renderMetrics();
      case 'disclaimer':
        return renderDisclaimer();
      default:
        return renderGeneric();
    }
  };

  const renderHeader = () => (
    <div className="section-header">
      <h2>{section.title}</h2>
      {section.content?.subtitle && <p className="subtitle">{section.content.subtitle}</p>}
    </div>
  );

  const renderPropertyOverview = () => (
    <div className="property-overview">
      <h3>{section.title}</h3>
      {section.content?.address && <p className="address">{section.content.address}</p>}
      {section.content?.details && (
        <div className="property-details">
          {Object.entries(section.content.details).map(([key, value]) => (
            <div key={key} className="detail-item">
              <span className="detail-label">{formatLabel(key)}:</span>
              <span className="detail-value">{value}</span>
            </div>
          ))}
        </div>
      )}
      {section.content?.description && (
        <p className="description">{section.content.description}</p>
      )}
    </div>
  );

  const renderMarketAnalysis = () => (
    <div className="market-analysis">
      <h3>{section.title}</h3>
      {section.content?.metrics && (
        <div className="metrics-grid">
          {section.content.metrics.map((metric: any, idx: number) => (
            <div key={idx} className="metric-card">
              <div className="metric-label">{metric.label || metric.name}</div>
              <div className="metric-value">
                {formatMetricValue(metric.value, metric.unit)}
                {metric.trend && <span className={`trend trend-${metric.trend}`}>
                  {getTrendIcon(metric.trend)}
                </span>}
              </div>
              {metric.change && <div className="metric-change">{metric.change}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderComparables = () => (
    <div className="comparables">
      <h3>{section.title}</h3>
      {section.content?.comparables && (
        <div className="comparables-list">
          {section.content.comparables.map((comp: any, idx: number) => (
            <div key={idx} className="comparable-item">
              <div className="comp-header">
                <h4>{comp.address}</h4>
                <span className="comp-price">{formatCurrency(comp.price)}</span>
              </div>
              <div className="comp-details">
                <span>{comp.sqft} sq ft</span>
                <span>•</span>
                <span>{comp.bedrooms} bed</span>
                <span>•</span>
                <span>{comp.bathrooms} bath</span>
                {comp.distance && (
                  <>
                    <span>•</span>
                    <span>{comp.distance.toFixed(2)} mi</span>
                  </>
                )}
              </div>
              {comp.soldDate && (
                <div className="comp-sold-date">Sold: {formatDate(comp.soldDate)}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderValuation = () => (
    <div className="valuation">
      <h3>{section.title}</h3>
      {section.content?.estimatedValue && (
        <div className="valuation-primary">
          <div className="valuation-label">Estimated Value</div>
          <div className="valuation-value">{formatCurrency(section.content.estimatedValue)}</div>
          {section.content.confidenceRange && (
            <div className="valuation-range">
              Range: {formatCurrency(section.content.confidenceRange.min)} - {formatCurrency(section.content.confidenceRange.max)}
            </div>
          )}
        </div>
      )}
      {section.content?.methodology && (
        <div className="methodology">
          <h4>Methodology</h4>
          <ul>
            {section.content.methodology.map((item: string, idx: number) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderInsights = () => (
    <div className="insights">
      <h3>{section.title}</h3>
      {section.content?.insights && (
        <ul className="insights-list">
          {section.content.insights.map((insight: string, idx: number) => (
            <li key={idx} className="insight-item">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" className="insight-icon">
                <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
              </svg>
              <span>{insight}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );

  const renderChart = () => (
    <div className="chart-section">
      <h3>{section.title}</h3>
      <div className="chart-placeholder">
        <svg width="100%" height="300" viewBox="0 0 600 300" className="chart">
          <rect x="0" y="0" width="600" height="300" fill="#f9fafb" />
          <text x="300" y="150" textAnchor="middle" fill="#6b7280" fontSize="14">
            Chart: {section.content?.chartType || 'Data visualization'}
          </text>
        </svg>
        <p className="chart-caption">{section.content?.caption}</p>
      </div>
    </div>
  );

  const renderTable = () => (
    <div className="table-section">
      <h3>{section.title}</h3>
      {section.content?.data && (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                {section.content.headers?.map((header: string, idx: number) => (
                  <th key={idx}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {section.content.data.map((row: any[], rowIdx: number) => (
                <tr key={rowIdx}>
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderText = () => (
    <div className="text-section">
      {section.title && <h3>{section.title}</h3>}
      <div className="text-content" dangerouslySetInnerHTML={{ __html: section.content?.text || '' }} />
    </div>
  );

  const renderBullets = () => (
    <div className="bullets-section">
      {section.title && <h3>{section.title}</h3>}
      <ul className="bullets-list">
        {section.content?.bullets?.map((bullet: string, idx: number) => (
          <li key={idx}>{bullet}</li>
        ))}
      </ul>
    </div>
  );

  const renderMetrics = () => (
    <div className="metrics-section">
      {section.title && <h3>{section.title}</h3>}
      <div className="metrics-grid">
        {section.content?.metrics?.map((metric: any, idx: number) => (
          <div key={idx} className="metric-card">
            <div className="metric-label">{metric.label}</div>
            <div className="metric-value">{metric.value}</div>
            {metric.change && (
              <div className={`metric-change ${metric.trend || ''}`}>{metric.change}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderDisclaimer = () => (
    <div className="disclaimer-section">
      {section.title && <h4>{section.title}</h4>}
      <p className="disclaimer-text">{section.content?.text || section.content}</p>
    </div>
  );

  const renderGeneric = () => (
    <div className="generic-section">
      {section.title && <h3>{section.title}</h3>}
      {section.content && (
        <div className="generic-content">
          {typeof section.content === 'string' ? (
            <p>{section.content}</p>
          ) : (
            <pre>{JSON.stringify(section.content, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  );

  // Utility functions
  const formatLabel = (key: string): string => {
    return key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase());
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
  };

  const formatDate = (date: string): string => {
    return new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const formatMetricValue = (value: any, unit?: string): string => {
    if (typeof value === 'number') {
      if (unit === 'currency' || unit === '$') {
        return formatCurrency(value);
      } else if (unit === 'percent' || unit === '%') {
        return `${value.toFixed(1)}%`;
      } else if (unit) {
        return `${value.toLocaleString()} ${unit}`;
      }
      return value.toLocaleString();
    }
    return String(value);
  };

  const getTrendIcon = (trend: string): string => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '→';
    }
  };

  return (
    <section className={`report-section section-${section.type}`} data-section-id={section.id}>
      {renderContent()}

      <style>{`
        .report-section {
          margin-bottom: 2rem;
          page-break-inside: avoid;
        }

        .report-section h2 {
          font-size: 1.875rem;
          font-weight: 700;
          color: #111827;
          margin: 0 0 0.5rem 0;
        }

        .report-section h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #374151;
          margin: 0 0 1rem 0;
        }

        .report-section h4 {
          font-size: 1rem;
          font-weight: 600;
          color: #4b5563;
          margin: 0 0 0.5rem 0;
        }

        .subtitle {
          font-size: 1.125rem;
          color: #6b7280;
          margin: 0;
        }

        .address {
          font-size: 1.125rem;
          font-weight: 500;
          color: #111827;
          margin-bottom: 1rem;
        }

        .property-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 0.75rem;
          margin-bottom: 1rem;
        }

        .detail-item {
          display: flex;
          gap: 0.5rem;
        }

        .detail-label {
          font-weight: 500;
          color: #6b7280;
        }

        .detail-value {
          color: #111827;
        }

        .description {
          color: #4b5563;
          line-height: 1.6;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .metric-card {
          padding: 1rem;
          background: #f9fafb;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
        }

        .metric-label {
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .metric-value {
          font-size: 1.5rem;
          font-weight: 600;
          color: #111827;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .metric-change {
          font-size: 0.875rem;
          color: #6b7280;
          margin-top: 0.25rem;
        }

        .trend {
          font-size: 1.25rem;
        }

        .trend-up {
          color: #059669;
        }

        .trend-down {
          color: #dc2626;
        }

        .trend-stable {
          color: #6b7280;
        }

        .comparables-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .comparable-item {
          padding: 1rem;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
        }

        .comp-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .comp-header h4 {
          margin: 0;
          font-size: 1rem;
          font-weight: 500;
        }

        .comp-price {
          font-size: 1.125rem;
          font-weight: 600;
          color: #059669;
        }

        .comp-details {
          display: flex;
          gap: 0.5rem;
          align-items: center;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .comp-sold-date {
          margin-top: 0.5rem;
          font-size: 0.875rem;
          color: #9ca3af;
        }

        .valuation-primary {
          padding: 1.5rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 12px;
          color: white;
          margin-bottom: 1.5rem;
        }

        .valuation-label {
          font-size: 0.875rem;
          opacity: 0.9;
          margin-bottom: 0.5rem;
        }

        .valuation-value {
          font-size: 2.5rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }

        .valuation-range {
          font-size: 0.875rem;
          opacity: 0.9;
        }

        .methodology {
          padding: 1rem;
          background: #f9fafb;
          border-radius: 8px;
        }

        .methodology ul {
          margin: 0.5rem 0 0 0;
          padding-left: 1.5rem;
        }

        .methodology li {
          margin-bottom: 0.5rem;
          color: #4b5563;
        }

        .insights-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .insight-item {
          display: flex;
          gap: 0.75rem;
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          background: #f0fdf4;
          border-left: 3px solid #10b981;
          border-radius: 4px;
          color: #065f46;
        }

        .insight-icon {
          flex-shrink: 0;
          color: #10b981;
        }

        .chart-placeholder {
          margin-top: 1rem;
        }

        .chart {
          border-radius: 8px;
          border: 1px solid #e5e7eb;
        }

        .chart-caption {
          margin-top: 0.5rem;
          font-size: 0.875rem;
          color: #6b7280;
          text-align: center;
        }

        .table-container {
          overflow-x: auto;
        }

        .data-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }

        .data-table th {
          padding: 0.75rem;
          text-align: left;
          background: #f9fafb;
          border-bottom: 2px solid #e5e7eb;
          font-weight: 600;
          color: #374151;
        }

        .data-table td {
          padding: 0.75rem;
          border-bottom: 1px solid #e5e7eb;
          color: #4b5563;
        }

        .data-table tr:hover {
          background: #f9fafb;
        }

        .text-content {
          line-height: 1.7;
          color: #374151;
        }

        .text-content p {
          margin-bottom: 1rem;
        }

        .bullets-list {
          padding-left: 1.5rem;
          margin: 0;
        }

        .bullets-list li {
          margin-bottom: 0.5rem;
          color: #4b5563;
          line-height: 1.6;
        }

        .disclaimer-section {
          padding: 1rem;
          background: #fef3c7;
          border-left: 3px solid #f59e0b;
          border-radius: 4px;
          margin-top: 2rem;
        }

        .disclaimer-text {
          margin: 0;
          font-size: 0.875rem;
          color: #78350f;
          line-height: 1.6;
        }

        /* Print styles */
        @media print {
          .report-section {
            page-break-inside: avoid;
          }

          .report-section h2,
          .report-section h3 {
            page-break-after: avoid;
          }
        }
      `}</style>
    </section>
  );
});

ReportSection.displayName = 'ReportSection';
