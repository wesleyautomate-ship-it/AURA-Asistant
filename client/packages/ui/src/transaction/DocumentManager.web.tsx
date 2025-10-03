import React from 'react';
import { TransactionDocument } from '@propertypro/features/types';

export type DocumentManagerProps = {
  documents: TransactionDocument[];
  onDocumentsChange?: (docs: TransactionDocument[]) => void;
  readOnly?: boolean;
};

const bytesToKB = (n: number) => `${(n / 1024).toFixed(1)} KB`;

const DocumentManager: React.FC<DocumentManagerProps> = ({ documents = [], onDocumentsChange, readOnly = false }) => {
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  const handlePick = () => {
    fileInputRef.current?.click();
  };

  const onInputChange: React.ChangeEventHandler<HTMLInputElement> = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    const newDocs: TransactionDocument[] = files.map((f) => ({
      id: `${Date.now()}-${f.name}`,
      name: f.name,
      type: f.type || 'application/octet-stream',
      url: URL.createObjectURL(f),
      uploadedAt: new Date().toISOString(),
      size: f.size,
    }));

    onDocumentsChange?.([...(documents || []), ...newDocs]);

    // reset input for same-file selections later
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeDoc = (id: string) => {
    if (readOnly) return;
    onDocumentsChange?.(documents.filter((d) => d.id !== id));
  };

  return (
    <div>
      {!readOnly && (
        <div className="mb-3 flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={onInputChange}
          />
          <button
            type="button"
            onClick={handlePick}
            className="px-3 py-1.5 rounded bg-orange-600 text-white text-sm"
          >
            Upload
          </button>
          <span className="text-xs text-gray-500">PDF, images, or any file</span>
        </div>
      )}

      {!documents?.length ? (
        <div className="p-6 text-center text-gray-500 bg-gray-50 border rounded">
          No documents yet
        </div>
      ) : (
        <ul className="divide-y border rounded">
          {documents.map((doc) => (
            <li key={doc.id} className="flex items-center justify-between p-3">
              <div className="min-w-0">
                <div className="text-sm font-medium truncate">{doc.name}</div>
                <div className="text-xs text-gray-500">{(doc.type || 'FILE').toUpperCase()} - {bytesToKB(doc.size)}</div>
              </div>
              <div className="flex items-center gap-2">
                <a href={doc.url} target="_blank" rel="noreferrer" className="text-sm text-gray-600 hover:underline">
                  Preview
                </a>
                {!readOnly && (
                  <button onClick={() => removeDoc(doc.id)} className="text-sm text-rose-600 hover:underline">
                    Remove
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DocumentManager;
