import json
path = 'audit-results.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
# Update contracts mismatch to empty and note fix applied
data['CONTRACTS_MISMATCH.brochure'] = []
fixes = data.get('FIXES_APPLIED.brochure', [])
fixes.append('Aligned frontend BrochureDraft.status to include \'rendering\' to match backend')
fixes.append('Added backend tests for brochure routes and reportlab dependency')

data['FIXES_APPLIED.brochure'] = fixes
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print('audit-results.json updated (contracts + fixes)')
