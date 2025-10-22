from pathlib import Path
line = Path(r"C:\Dev\RealtorProAI\Realtor-assistant\aura-client\src\components\contacts\ContactDetailHeader.tsx").read_text(encoding="utf-8").splitlines()[34]
print(repr(line))
print([hex(ord(ch)) for ch in line])
