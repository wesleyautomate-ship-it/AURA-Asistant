/**
 * Content Export Utility
 * ======================
 * 
 * Handles PDF and HTML exports with file downloads and share links
 * Integrates with backend export API and updates store state
 * 
 * Version: 3.2
 * Phase: Track 2.6 - Export Integration
 */

import { ContentType as SchemaContentType } from '../types/contentSchemas';
import { useCommandStore } from '../store/commandStore';
import api from '../services/http';

export interface ExportOptions {
  taskId: string;
  contentType: SchemaContentType;
  format: 'pdf' | 'html';
  includeBranding?: boolean;
}

export interface ExportResult {
  success: boolean;
  format: 'pdf' | 'html';
  message: string;
  shareUrl?: string;
  expiresAt?: string;
  error?: string;
}

/**
 * Export content as PDF and trigger browser download
 */
export const exportAsPDF = async (options: ExportOptions): Promise<ExportResult> => {
  const { taskId, contentType, includeBranding = true } = options;

  console.group('[Export:PDF]');
  console.log('Starting PDF export for task:', taskId);
  console.log('Content type:', contentType);
  console.time('PDF Export');

  try {
    const response = await api.post<Blob>(
      '/export',
      {
        task_id: taskId,
        content_type: contentType,
        format: 'pdf',
        include_branding: includeBranding,
      },
      { responseType: 'blob' }
    );

    const contentDisposition = response.headers['content-disposition'];
    let filename = `${contentType.toLowerCase()}_${taskId}.pdf`;
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '');
      }
    }

    // Download the PDF file
    const blob = response.data;
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    // Update store
    const store = useCommandStore.getState();
    store.markExported(taskId, 'pdf');

    console.log('PDF download triggered:', filename);
    console.timeEnd('PDF Export');
    console.groupEnd();

    return {
      success: true,
      format: 'pdf',
      message: `PDF downloaded successfully: ${filename}`,
    };
  } catch (error) {
    console.error('PDF export failed:', error);
    console.timeEnd('PDF Export');
    console.groupEnd();

    return {
      success: false,
      format: 'pdf',
      message: 'Failed to export PDF',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

/**
 * Export content as HTML and generate share link
 */
export const exportAsHTML = async (options: ExportOptions): Promise<ExportResult> => {
  const { taskId, contentType, includeBranding = true } = options;

  console.group('[Export:HTML]');
  console.log('Generating HTML share link for task:', taskId);
  console.log('Content type:', contentType);
  console.time('HTML Export');

  try {
    const { data } = await api.post<{
      share_url: string;
      expires_at?: string;
      message?: string;
    }>(
      '/export',
      {
        task_id: taskId,
        content_type: contentType,
        format: 'html',
        include_branding: includeBranding,
      }
    );

    if (!data.share_url) {
      throw new Error('No share URL returned from server');
    }

    // Update store
    const store = useCommandStore.getState();
    store.markExported(taskId, 'html');

    console.log('Share link generated:', data.share_url);
    console.log('Expires at:', data.expires_at);
    console.timeEnd('HTML Export');
    console.groupEnd();

    return {
      success: true,
      format: 'html',
      message: 'Share link generated successfully',
      shareUrl: data.share_url,
      expiresAt: data.expires_at,
    };
  } catch (error) {
    console.error('HTML export failed:', error);
    console.timeEnd('HTML Export');
    console.groupEnd();

    return {
      success: false,
      format: 'html',
      message: 'Failed to generate share link',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

/**
 * Copy share URL to clipboard
 */
export const copyShareLink = async (shareUrl: string): Promise<boolean> => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(shareUrl);
      console.log('[Export] Share link copied to clipboard');
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareUrl;
      textArea.style.position = 'fixed';
      textArea.style.left = '-9999px';
      document.body.appendChild(textArea);
      textArea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      if (success) {
        console.log('[Export] Share link copied to clipboard (fallback)');
      }
      return success;
    }
  } catch (error) {
    console.error('[Export] Failed to copy share link:', error);
    return false;
  }
};

/**
 * Open share URL in new tab
 */
export const openShareLink = (shareUrl: string): void => {
  try {
    window.open(shareUrl, '_blank', 'noopener,noreferrer');
    console.log('[Export] Share link opened in new tab');
  } catch (error) {
    console.error('[Export] Failed to open share link:', error);
  }
};

/**
 * Revoke share link (if backend supports it)
 */
export const revokeShareLink = async (taskId: string): Promise<boolean> => {
  console.log('[Export] Revoking share link for task:', taskId);

  try {
    await api.post('/export/revoke/' + taskId);
    console.log('[Export] Share link revoked successfully');
    return true;
  } catch (error) {
    console.error('[Export] Failed to revoke share link:', error);
    return false;
  }
};

/**
 * Get export status for a task
 */
export const getExportStatus = async (taskId: string) => {
  try {
    const { data } = await api.get(`/export/status/${taskId}`);
    return data;
  } catch (error) {
    console.error('[Export] Failed to get export status:', error);
    return null;
  }
};

/**
 * Main export function that handles both formats
 */
export const exportContent = async (options: ExportOptions): Promise<ExportResult> => {
  if (options.format === 'pdf') {
    return exportAsPDF(options);
  } else {
    return exportAsHTML(options);
  }
};

/**
 * Helper to format expiration date
 */
export const formatExpirationDate = (expiresAt: string): string => {
  try {
    const date = new Date(expiresAt);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 1) {
      return `Expires in ${diffDays} days`;
    } else if (diffHours > 1) {
      return `Expires in ${diffHours} hours`;
    } else if (diffHours === 1) {
      return 'Expires in 1 hour';
    } else {
      return 'Expires soon';
    }
  } catch (error) {
    return 'Expires soon';
  }
};
