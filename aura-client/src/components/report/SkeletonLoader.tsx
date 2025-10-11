/**
 * Skeleton Loader Component
 * ==========================
 * 
 * Loading placeholders for content sections
 * Used during initial content fetch and partial data loads
 * 
 * Version: 3.2
 * Phase: Track 2.4 - Rendering Components
 */

import React from 'react';

interface SkeletonLoaderProps {
  variant?: 'text' | 'title' | 'card' | 'metric' | 'full-page';
  count?: number;
  className?: string;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant = 'text',
  count = 1,
  className = '',
}) => {
  const renderSkeleton = () => {
    switch (variant) {
      case 'title':
        return <div className="skeleton skeleton-title" />;
      case 'card':
        return (
          <div className="skeleton-card">
            <div className="skeleton skeleton-title-sm" />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" style={{ width: '80%' }} />
          </div>
        );
      case 'metric':
        return (
          <div className="skeleton-metric">
            <div className="skeleton skeleton-text-sm" />
            <div className="skeleton skeleton-title" />
          </div>
        );
      case 'full-page':
        return (
          <div className="skeleton-full-page">
            <div className="skeleton skeleton-title" style={{ marginBottom: '1rem' }} />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" style={{ width: '90%', marginBottom: '2rem' }} />
            
            <div className="skeleton-grid">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="skeleton-card">
                  <div className="skeleton skeleton-title-sm" />
                  <div className="skeleton skeleton-text" />
                  <div className="skeleton skeleton-text" style={{ width: '70%' }} />
                </div>
              ))}
            </div>

            <div className="skeleton skeleton-title-sm" style={{ marginTop: '2rem', marginBottom: '1rem' }} />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" style={{ width: '85%' }} />
          </div>
        );
      case 'text':
      default:
        return <div className="skeleton skeleton-text" />;
    }
  };

  return (
    <div className={`skeleton-loader ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <React.Fragment key={index}>{renderSkeleton()}</React.Fragment>
      ))}

      <style>{`
        @keyframes shimmer {
          0% {
            background-position: -1000px 0;
          }
          100% {
            background-position: 1000px 0;
          }
        }

        .skeleton {
          background: linear-gradient(
            90deg,
            #f0f0f0 0%,
            #f8f8f8 50%,
            #f0f0f0 100%
          );
          background-size: 1000px 100%;
          animation: shimmer 2s infinite;
          border-radius: 4px;
        }

        .skeleton-loader {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .skeleton-title {
          height: 2rem;
          width: 60%;
          margin-bottom: 0.5rem;
        }

        .skeleton-title-sm {
          height: 1.5rem;
          width: 40%;
          margin-bottom: 0.5rem;
        }

        .skeleton-text {
          height: 1rem;
          width: 100%;
        }

        .skeleton-text-sm {
          height: 0.875rem;
          width: 50%;
        }

        .skeleton-card {
          padding: 1rem;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .skeleton-metric {
          padding: 1rem;
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .skeleton-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .skeleton-full-page {
          padding: 1rem;
        }

        /* Accessible loading state */
        .skeleton-loader {
          position: relative;
        }

        .skeleton-loader::before {
          content: 'Loading content...';
          position: absolute;
          left: -10000px;
          width: 1px;
          height: 1px;
          overflow: hidden;
        }

        @media (prefers-reduced-motion: reduce) {
          .skeleton {
            animation: none;
            background: #f0f0f0;
          }
        }
      `}</style>
    </div>
  );
};
