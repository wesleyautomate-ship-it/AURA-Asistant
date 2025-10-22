from pathlib import Path
path = Path(r"C:\Dev\RealtorProAI\Realtor-assistant\aura-client\src\components\report\ExportToolbar.tsx")
lines = path.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if 'PDF downloaded' in line:
        lines[i] = "      setExportStatus('PDF downloaded');"
    elif 'Export failed' in line:
        lines[i] = "      setExportStatus(result.error ? f'Export failed: {result.error}' : 'Export failed');"
    elif 'Share link generated' in line:
        lines[i] = "      setExportStatus('Share link generated');"
    elif 'Failed to generate link' in line:
        lines[i] = "      setExportStatus(result.error ? f'Failed to generate link: {result.error}' : 'Failed to generate link');"
    elif 'Link copied to clipboard' in line:
        lines[i] = "        setExportStatus('Link copied to clipboard');"
    elif 'Failed to copy link' in line:
        lines[i] = "        setExportStatus('Failed to copy link');"
path.write_text('\n'.join(lines) + '\n', encoding="utf-8")
