# 🔧 Automation (Support Scripts Only)

This directory contains helper scripts and templates used for Warp + Cursor manual execution of AURA RealtorProAI.

## 📁 Structure
- `scripts/` — Helper utilities (data loaders, verification tools, setup scripts)
- `templates/` — AI prompt templates (CMA, Social, Pitch, etc.)
- `build_logs/` — Manual execution logs or summaries

## 🎯 Purpose
> **Note**: Full automation (Codex) is disabled.  
> All executions are done manually for quality assurance and precision development.

## 🛠️ Available Scripts

### Data & Setup Scripts
- `setup_env.ps1` — Environment setup and API key configuration
- `seed_data.ps1` — Database population with realistic real estate data
- `verify_ai.ps1` — Google Gemini API connection testing
- `check_status.ps1` — System health and component status checking

### Development Helpers
- `backup_config.ps1` — Backup environment and configuration files
- `reset_db.ps1` — Database reset for testing
- `test_endpoints.ps1` — API endpoint validation
- `generate_docs.ps1` — Documentation generation and updates

## 🎨 Template Categories

### AI Content Templates
- `cma_report_template.md` — Comparative Market Analysis structure
- `pitch_deck_template.md` — Property pitch deck framework
- `social_post_template.md` — Social media content guidelines
- `market_analysis_template.md` — Market insight generation

### Development Templates
- `feature_spec_template.md` — New feature specification format
- `bug_report_template.md` — Issue reporting standardization
- `api_endpoint_template.md` — New endpoint development guide

## 🚀 Usage Workflow

1. **Setup Phase**: Run setup scripts for environment configuration
2. **Development Phase**: Use templates for consistent AI content generation
3. **Testing Phase**: Validate with verification scripts
4. **Documentation Phase**: Generate updated documentation

## ⚠️ Manual Execution Only
All scripts are designed to be run manually with careful review of outputs. No automated deployments or unattended operations.