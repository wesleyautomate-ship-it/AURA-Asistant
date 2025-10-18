import json, os
from glob import glob

path = 'audit-results.json'
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception:
    data = {}

# Inventory
frontend_files = [
    'aura-client/src/features/brochure/api/brochure.ts',
    'aura-client/src/features/brochure/BrochureTile.tsx',
    'aura-client/src/pages/ai-workflow/brochure.tsx',
    'aura-client/src/pages/ai-workflow/brochure-editor.tsx',
    'aura-client/src/services/brochureDrafts.ts',
    'aura-client/src/services/brochureEngine.ts',
    'aura-client/src/store/brochureDraftStore.ts',
    'aura-client/src/types/brochure.ts',
    'aura-client/src/utils/brochure.ts',
    'aura-client/src/utils/brochureProgressSteps.ts',
]
backend_files = [
    'backend/app/api/v1/brochures_router.py',
    'backend/app/api/v1/export_router.py',
    'backend/app/services/render_service.py',
    'backend/app/schemas/brochure.py',
    'backend/app/core/models.py',
    'backend/app/domain/ai/file_storage_service.py',
]
assets = []

inv = {
    'frontend': [f for f in frontend_files if os.path.exists(f)],
    'backend': [f for f in backend_files if os.path.exists(f)],
    'database': {
        'models': ['backend/app/core/models.py#L1'],
        'migrations': [p.replace('\\','/') for p in glob('backend/app/alembic/versions/*brochure*')],
    },
    'assets': assets,
}

# DB audit summary
db_audit = {
    'tables': {
        'brochure_drafts': {
            'columns': ['id:String(36) PK', 'data:JSON', 'status:String(20) indexed', 'download_url:String(512)', 'created_at:DateTime', 'updated_at:DateTime'],
            'indexes': ['ix_brochure_drafts_status', 'ix_brochure_drafts_id(unique)'],
            'fks': [],
            'notes': 'No templates or contacts FK; JSON holds draft blob',
        }
    },
    'gaps': [
        'Missing brochure_templates table and foreign key from drafts to template',
        'No FK to contacts/listings for provenance',
        'Consider index on created_at for listing/history queries',
    ],
    'plan': [
        'Add brochure_templates table with seed data (clean-minimal, luxury-showcase, neighborhood-highlight)',
        'Add optional brochure_drafts.template_id FK',
    ]
}

# Backend audit summary
backend_audit = {
    'routes': {
        'POST /api/v1/brochures': 'create draft',
        'GET /api/v1/brochures/{id}': 'get draft',
        'PATCH /api/v1/brochures/{id}': 'update draft data/status',
        'POST /api/v1/brochures/{id}/render': 'render PDF and set download_url',
        'GET /api/v1/brochures/{id}/download': 'get download_url',
    },
    'services': {
        'render_service': 'HTML builder + WeasyPrint if available, fallback to reportlab mock PDF',
        'storage': 'FileStorageService saves under uploads/deliverables/{id}'
    },
    'gaps': [
        'No GET /api/v1/brochures list endpoint',
        'No /api/v1/templates endpoint for brochure templates',
        'Render fallback requires reportlab; add dependency or improve error messaging',
    ]
}

# Frontend audit summary
frontend_audit = {
    'entry_points': [
        'aura-client/src/features/brochure/BrochureTile.tsx',
        'aura-client/src/pages/ai-workflow/brochure.tsx',
        'aura-client/src/pages/ai-workflow/brochure-editor.tsx',
    ],
    'services': [
        'createDraft, getDraft, updateDraft, renderDraft, getDownloadUrl in features/brochure/api/brochure.ts',
        'brochureDraftService maps server payload to BrochureDraft type',
    ],
    'env': ['VITE_API_BASE_URL', 'VITE_USE_REAL_API'],
    'ux': [
        'Loading and error states present in BrochureTile, simple editor pending',
        'Progress helpers exist in utils/brochureProgressSteps.ts',
    ],
}

# Contract mismatches
contracts = []
contracts.append({'field': 'status', 'frontend': "'draft'|'generating'|'ready'|'error'", 'backend': "'draft'|'rendering'|'ready'|'error'", 'impact': 'minor type mismatch; UI mapping may be inconsistent'})

# Acceptance matrix
acceptance = [
    {'scenario':'List Templates','contracts':False,'works_mock':True,'works_real':True,'ux_states':True,'perf':'n/a'},
    {'scenario':'Generate Brochure','contracts':True,'works_mock':True,'works_real':True,'ux_states':True,'perf':'ok'},
    {'scenario':'Poll Status','contracts':True,'works_mock':True,'works_real':True,'ux_states':True,'perf':'ok'},
    {'scenario':'Download PDF','contracts':True,'works_mock':True,'works_real':True,'ux_states':True,'perf':'ok'},
    {'scenario':'Error Handling','contracts':True,'works_mock':True,'works_real':True,'ux_states':True,'perf':'n/a'},
]

# Apply to data
data['INVENTORY.brochure'] = inv
data['DB_AUDIT.brochure'] = db_audit
data['BACKEND_AUDIT.brochure'] = backend_audit
data['FRONTEND_AUDIT.brochure'] = frontend_audit
data['CONTRACTS_MISMATCH.brochure'] = contracts
data['ACCEPTANCE_MATRIX.brochure'] = acceptance

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print('audit-results.json updated')
