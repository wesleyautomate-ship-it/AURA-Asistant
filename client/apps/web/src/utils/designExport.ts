// Utilities for exporting designs as PNG and printing
// We avoid external deps by working with inline SVG and print windows

export function exportSVGToPNG(svgElement: SVGSVGElement, fileName = 'design.png', scale = 2) {
  if (!svgElement) return;
  const serializer = new XMLSerializer();
  const source = serializer.serializeToString(svgElement);

  const svgBlob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);

  const image = new Image();
  image.onload = () => {
    const canvas = document.createElement('canvas');
    const width = svgElement.viewBox.baseVal.width || svgElement.clientWidth;
    const height = svgElement.viewBox.baseVal.height || svgElement.clientHeight;
    canvas.width = Math.max(1, Math.floor(width * scale));
    canvas.height = Math.max(1, Math.floor(height * scale));
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) return;
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    }, 'image/png');

    URL.revokeObjectURL(url);
  };
  image.src = url;
}

export function openPrintWindow(html: string, title = 'Print Design', styles: string = '') {
  const w = window.open('', '_blank');
  if (!w) return;
  w.document.open();
  w.document.write(`<!DOCTYPE html><html><head><title>${title}</title>
  <style>
    @page { size: A4; margin: 12mm; }
    @media print {
      .no-print { display: none !important; }
    }
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    ${styles}
  </style>
  </head><body>${html}</body></html>`);
  w.document.close();
  w.focus();
  // Delay print to allow rendering
  setTimeout(() => {
    w.print();
  }, 300);
}
