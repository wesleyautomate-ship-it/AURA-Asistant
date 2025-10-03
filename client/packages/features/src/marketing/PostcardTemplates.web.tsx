import React, { useMemo, useRef } from 'react';
import { exportSVGToPNG, openPrintWindow } from '../utils/designExport';

export interface PostcardData {
  title: string;
  address: string;
  price?: string;
  beds?: number;
  baths?: number;
  sqft?: number;
  imageUrl?: string;
  agentName?: string;
  agentPhone?: string;
  brandColor?: string; // default purple
}

interface Props {
  data: PostcardData;
}

const CARD_W = 800; // px for on-screen preview; print uses @page sizing
const CARD_H = 500;

const PostcardTemplates: React.FC<Props> = ({ data }) => {
  const ref = useRef<SVGSVGElement | null>(null);
  const brand = data.brandColor || '#7c3aed';

  const headerText = useMemo(() => data.title || 'Just Listed', [data.title]);

  const handleDownloadPNG = () => {
    if (ref.current) exportSVGToPNG(ref.current, 'postcard.png', 2);
  };

  const handlePrint = () => {
    const svg = ref.current;
    if (!svg) return;
    const serializer = new XMLSerializer();
    const source = serializer.serializeToString(svg);
    const html = `<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;">
      <img src="data:image/svg+xml;charset=utf-8,${encodeURIComponent(source)}" style="width:100%;max-width:900px;" />
    </div>`;
    openPrintWindow(html, 'Print Postcard');
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      <div className="p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">Postcard Preview</h3>
        <div className="space-x-2">
          <button onClick={handleDownloadPNG} className="px-3 py-1 rounded-md text-xs font-medium bg-purple-600 text-white hover:bg-purple-700">Download PNG</button>
          <button onClick={handlePrint} className="px-3 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800 hover:bg-gray-200">Print</button>
        </div>
      </div>
      <div className="p-4">
        <svg ref={ref} width={CARD_W} height={CARD_H} viewBox={`0 0 ${CARD_W} ${CARD_H}`} xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor={brand} stopOpacity="1" />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity="1" />
            </linearGradient>
            <clipPath id="rounded">
              <rect x="0" y="0" width={CARD_W} height={CARD_H} rx="24" ry="24" />
            </clipPath>
          </defs>
          <rect x="0" y="0" width={CARD_W} height={CARD_H} fill="url(#g1)" />
          <g clipPath="url(#rounded)">
            {/* Image area */}
            <rect x="24" y="24" width="420" height={CARD_H - 48} fill="#fff" opacity="0.08" />
            {data.imageUrl ? (
              <image href={data.imageUrl} x="24" y="24" width="420" height={CARD_H - 48} preserveAspectRatio="xMidYMid slice" />
            ) : null}

            {/* Text area */}
            <g transform="translate(470, 40)">
              <text x="0" y="0" fill="#fff" fontSize="32" fontWeight="700">{headerText}</text>
              <text x="0" y="50" fill="#ede9fe" fontSize="20">{data.address}</text>
              <g transform="translate(0, 100)">
                {data.price && <text x="0" y="0" fill="#fff" fontSize="28" fontWeight="700">{data.price}</text>}
                <text x="0" y="40" fill="#ede9fe" fontSize="16">
                  {(data.beds || 0) > 0 ? `${data.beds} bed · ` : ''}{(data.baths || 0)} bath · {(data.sqft || 0).toLocaleString()} sqft
                </text>
              </g>
              <g transform="translate(0, 200)">
                <text x="0" y="0" fill="#ede9fe" fontSize="14">Presented by</text>
                <text x="0" y="26" fill="#fff" fontSize="18" fontWeight="600">{data.agentName || 'Your Name'}</text>
                <text x="0" y="48" fill="#ede9fe" fontSize="14">{data.agentPhone || '+971 50 000 0000'}</text>
              </g>
              <rect x="0" y={CARD_H - 190} width={CARD_W - 494} height="2" fill="#a78bfa" />
              <text x="0" y={CARD_H - 150} fill="#ede9fe" fontSize="12">PropertyPro AI · Dubai Real Estate Marketing</text>
            </g>
          </g>
        </svg>
      </div>
    </div>
  );
};

export default PostcardTemplates;
