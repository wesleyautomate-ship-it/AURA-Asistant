/**
 * Export Toolbar Component
 * ========================
 * 
 * Provides export actions (PDF, HTML share link) with status indicators
 * Shows last export timestamp and handles export operations
 * 
 * Version: 3.2
 * Phase: Track 2.4 - Rendering Components
 */

import { useState } from 'react';
import { ContentType as SchemaContentType } from '../../types/contentSchemas';
import { 
  exportContent, 
  copyShareLink, 
  openShareLink,
  formatExpirationDate,
  type ExportResult 
} from '../../utils/exporter';
import { useCommandStore } from '../../store/commandStore';

interface ExportToolbarProps {
  taskId: string;
  contentType: SchemaContentType;
  exportedAt?: string;
  className?: string;
}

export const ExportToolbar = ({
  taskId,
  contentType,
  exportedAt,
  className = '',
}: ExportToolbarProps) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<string>('');
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [expiresAt, setExpiresAt] = useState<string | null>(null);
  const [showShareDialog, setShowShareDialog] = useState(false);

  const getExportStatus = useCommandStore((state) => state.getExportStatus);
  const status = getExportStatus(taskId);

  const handleExportPDF = async () => {
    setIsExporting(true);
    setExportStatus('Generating PDF...');

    const result: ExportResult = await exportContent({
      taskId,
      contentType,
      format: 'pdf',
    });

    if (result.success) {
      setExportStatus('PDF downloaded');
      setTimeout(() => setExportStatus(''), 3000);
    } else {
      setExportStatus(result.error ? f'Export failed: {result.error}' : 'Export failed');
      setTimeout(() => setExportStatus(''), 5000);
    }

    setIsExporting(false);
  };

  const handleGenerateShareLink = async () => {
    setIsExporting(true);
    setExportStatus('Generating share link...');

    const result: ExportResult = await exportContent({
      taskId,
      contentType,
      format: 'html',
    });

    if (result.success && result.shareUrl) {
      setShareUrl(result.shareUrl);
      setExpiresAt(result.expiresAt || null);
      setShowShareDialog(true);
      setExportStatus('Share link generated');
      setTimeout(() => setExportStatus(''), 3000);
    } else {
      setExportStatus(result.error ? f'Failed to generate link: {result.error}' : 'Failed to generate link');
      setTimeout(() => setExportStatus(''), 5000);
    }

    setIsExporting(false);
  };

  const handleCopyLink = async () => {
    if (shareUrl) {
      const success = await copyShareLink(shareUrl);
      if (success) {
        setExportStatus('Link copied to clipboard');
        setTimeout(() => setExportStatus(''), 2000);
      } else {
        setExportStatus('Failed to copy link');
        setTimeout(() => setExportStatus(''), 3000);
      }
    }
  };

  const handleOpenLink = () => {
    if (shareUrl) {
      openShareLink(shareUrl);
    }
  };

  return (
    <div className={`export-toolbar ${className}`}>
      {/* Export Actions */}
      <div className="export-actions">
        <button
          onClick={handleExportPDF}
          disabled={isExporting}
          className="export-btn export-pdf"
          aria-label="Export as PDF"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6z" />
            <path d="M9 8a.5.5 0 01.5-.5h1a.5.5 0 010 1h-1A.5.5 0 019 8z" />
            <path d="M9 10.5a.5.5 0 01.5-.5h1a.5.5 0 010 1h-1a.5.5 0 01-.5-.5z" />
            <path d="M9 13a.5.5 0 01.5-.5h1a.5.5 0 010 1h-1A.5.5 0 019 13z" />
          </svg>
          <span>Export PDF</span>
        </button>

        <button
          onClick={handleGenerateShareLink}
          disabled={isExporting}
          className="export-btn export-share"
          aria-label="Generate share link"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
          </svg>
          <span>Get Share Link</span>
        </button>
      </div>

      {/* Status Indicators */}
      <div className="export-status">
        {isExporting && (
          <div className="status-indicator exporting">
            <div className="spinner" />
            <span>Exporting...</span>
          </div>
        )}

        {exportStatus && !isExporting && (
          <div className={`status-indicator ${exportStatus.startsWith('✓') 'success' : 'error'}`}>
            <span>{exportStatus}</span>
          </div>
        )}

        {exportedAt && !isExporting && !exportStatus && (
          <div className="status-indicator last-export">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
              <path d="M7.5 3a.5.5 0 0 1 .5.5v4.793l2.146-2.147a.5.5 0 0 1 .708.708l-3 3a.5.5 0 0 1-.708 0l-3-3a.5.5 0 1 1 .708-.708L7.5 8.293V3.5a.5.5 0 0 1 .5-.5z"/>
            </svg>
            <span>Last exported: {new Date(exportedAt).toLocaleDateString()}</span>
          </div>
        )}

        {status && status.export_count > 0 && (
          <div className="export-badge">
            <span>{status.export_count} {status.export_count === 1 'export' : 'exports'}</span>
            {status.formats_available.length > 0 && (
              <span className="formats">({status.formats_available.join(', ')})</span>
            )}
          </div>
        )}
      </div>

      {/* Share Link Dialog */}
      {showShareDialog && shareUrl && (
        <div className="share-dialog-overlay" onClick={() => setShowShareDialog(false)}>
          <div className="share-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="share-dialog-header">
              <h3>Share Link Generated</h3>
              <button
                onClick={() => setShowShareDialog(false)}
                className="close-btn"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="share-dialog-body">
              <div className="share-url-box">
                <input
                  type="text"
                  value={shareUrl}
                  readOnly
                  className="share-url-input"
                  onClick={(e) => (e.target as HTMLInputElement).select()}
                />
              </div>

              {expiresAt && (
                <p className="expiration-notice">
                  {formatExpirationDate(expiresAt)}
                </p>
              )}

              <div className="share-actions">
                <button onClick={handleCopyLink} className="btn-primary">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
                    <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"/>
                  </svg>
                  Copy Link
                </button>

                <button onClick={handleOpenLink} className="btn-secondary">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"/>
                    <path d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"/>
                  </svg>
                  Open Link
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .export-toolbar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
          padding: 1rem;
          background: white;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          margin-bottom: 1.5rem;
        }

        .export-actions {
          display: flex;
          gap: 0.75rem;
        }

        .export-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.625rem 1rem;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          background: white;
          color: #374151;
          font-size: 0.875rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .export-btn:hover:not(:disabled) {
          background: #f9fafb;
          border-color: #d1d5db;
        }

        .export-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .export-pdf:hover:not(:disabled) {
          background: #fef2f2;
          border-color: #fecaca;
          color: #dc2626;
        }

        .export-share:hover:not(:disabled) {
          background: #eff6ff;
          border-color: #bfdbfe;
          color: #2563eb;
        }

        .export-status {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
        }

        .status-indicator.exporting {
          color: #6b7280;
        }

        .status-indicator.success {
          color: #059669;
        }

        .status-indicator.error {
          color: #dc2626;
        }

        .status-indicator.last-export {
          color: #6b7280;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #e5e7eb;
          border-top-color: #3b82f6;
          border-radius: 50%;
          animation: spin 0.6s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .export-badge {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.25rem 0.75rem;
          background: #f3f4f6;
          border-radius: 9999px;
          font-size: 0.75rem;
          color: #6b7280;
        }

        .export-badge .formats {
          color: #9ca3af;
        }

        /* Share Dialog */
        .share-dialog-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 1rem;
        }

        .share-dialog {
          background: white;
          border-radius: 12px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
          max-width: 500px;
          width: 100%;
        }

        .share-dialog-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1.5rem;
          border-bottom: 1px solid #e5e7eb;
        }

        .share-dialog-header h3 {
          margin: 0;
          font-size: 1.125rem;
          font-weight: 600;
          color: #111827;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 1.5rem;
          color: #9ca3af;
          cursor: pointer;
          padding: 0;
          width: 2rem;
          height: 2rem;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
        }

        .close-btn:hover {
          background: #f3f4f6;
          color: #6b7280;
        }

        .share-dialog-body {
          padding: 1.5rem;
        }

        .share-url-box {
          margin-bottom: 1rem;
        }

        .share-url-input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          font-size: 0.875rem;
          font-family: monospace;
          color: #374151;
          background: #f9fafb;
        }

        .share-url-input:focus {
          outline: none;
          border-color: #3b82f6;
          background: white;
        }

        .expiration-notice {
          margin: 0 0 1rem 0;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .share-actions {
          display: flex;
          gap: 0.75rem;
        }

        .btn-primary,
        .btn-secondary {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.625rem 1rem;
          border: 1px solid;
          border-radius: 6px;
          font-size: 0.875rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .btn-primary {
          background: #3b82f6;
          border-color: #3b82f6;
          color: white;
        }

        .btn-primary:hover {
          background: #2563eb;
          border-color: #2563eb;
        }

        .btn-secondary {
          background: white;
          border-color: #e5e7eb;
          color: #374151;
        }

        .btn-secondary:hover {
          background: #f9fafb;
          border-color: #d1d5db;
        }

        /* Print styles */
        @media print {
          .export-toolbar {
            display: none;
          }
        }

        /* Responsive */
        @media (max-width: 640px) {
          .export-toolbar {
            flex-direction: column;
            align-items: stretch;
          }

          .export-actions {
            flex-direction: column;
          }

          .export-btn {
            justify-content: center;
          }

          .export-status {
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};
