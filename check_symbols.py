from pathlib import Path
text = Path(r"C:\Dev\RealtorProAI\Realtor-assistant\aura-client\src\components\report\ExportToolbar.tsx").read_text(encoding="utf-8")
if '\u2713' in text:
    print('contains check mark')
if '\u2717' in text:
    print('contains cross mark')
