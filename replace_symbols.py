from pathlib import Path
text = Path(r"C:\Dev\RealtorProAI\Realtor-assistant\aura-client\src\components\report\ExportToolbar.tsx").read_text(encoding="utf-8")
replacements = {
    '? PDF downloaded': 'PDF downloaded',
    '? ': '',
    '? Share link generated': 'Share link generated',
    '? Link copied to clipboard': 'Link copied to clipboard'
}
for old, new in replacements.items():
    text = text.replace(old, new)
Path(r"C:\Dev\RealtorProAI\Realtor-assistant\aura-client\src\components\report\ExportToolbar.tsx").write_text(text, encoding="utf-8")
