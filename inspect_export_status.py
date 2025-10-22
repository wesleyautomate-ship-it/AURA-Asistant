from pathlib import Path
import re
text = Path(r"C:\Dev\RealtorProAI\Realtor-assistant\aura-client\src\components\report\ExportToolbar.tsx").read_text(encoding="utf-8")
pattern = re.compile(r"setExportStatus\(([^)]+)\)")
for match in pattern.finditer(text):
    snippet = match.group(0)
    if '?' in snippet:
        print(repr(snippet))
