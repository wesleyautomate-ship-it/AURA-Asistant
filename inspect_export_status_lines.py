from pathlib import Path
text = Path(r"C:\Dev\RealtorProAI\Realtor-assistant\aura-client\src\components\report\ExportToolbar.tsx").read_text(encoding="utf-8")
for line in text.splitlines():
    if 'setExportStatus' in line:
        print(repr(line))
