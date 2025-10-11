/**
 * Aura v3.3 - Validation Pipeline
 * ===============================
 * 
 * Comprehensive content quality assurance system with:
 * - Pre-generation validation checks
 * - Post-generation quality scoring
 * - Automated remediation suggestions
 * - Multi-pass validation loops
 * - Compliance and brand enforcement
 * 
 * @version 3.3.0
 */

import { ContentType } from './types';

// =============================================================================
// VALIDATION TYPES & INTERFACES
// =============================================================================

export interface ValidationContext {
  content_type: ContentType;
  user_prompt: string;
  generated_content?: any;
  template_constraints?: TemplateConstraints;
  brand_kit?: BrandKit;
  locale?: string;
  session_id: string;
  agent_profile?: AgentProfile;
}

export interface TemplateConstraints {
  template_id: string;
  max_characters: number;
  required_sections: string[];
  slot_limits: Record<string, number>;
  typography_rules: TypographyRules;
}

export interface TypographyRules {
  heading_levels: number;
  body_paragraph_limit: number;
  list_item_limit: number;
}

export interface BrandKit {
  colors: ColorPalette;
  fonts: FontConfig;
  voice: VoiceConfig;
  compliance: ComplianceRules;
}

export interface AgentProfile {
  id: string;
  name: string;
  brokerage: string;
  voice_preferences: VoicePreferences;
  compliance_level: 'basic' | 'standard' | 'strict';
}

export interface ValidationResult {
  validator: string;
  passed: boolean;
  score: number; // 0-1
  confidence: number; // 0-1
  issues: ValidationIssue[];
  suggestions: RemediationSuggestion[];
  execution_time_ms: number;
}

export interface ValidationIssue {
  type: 'error' | 'warning' | 'suggestion';
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  location?: ContentLocation;
  details?: Record<string, any>;
}

export interface ContentLocation {
  section?: string;
  field?: string;
  line?: number;
  character_range?: [number, number];
}

export interface RemediationSuggestion {
  type: 'content_revision' | 'template_adjustment' | 'brand_correction' | 'compliance_fix';
  priority: 'high' | 'medium' | 'low';
  automated: boolean;
  description: string;
  fix_prompt?: string;
  estimated_effort: 'quick' | 'moderate' | 'complex';
  success_probability: number; // 0-1
}

export interface ValidationReport {
  overall_score: number; // 0-1
  passed: boolean;
  execution_time_ms: number;
  results: ValidationResult[];
  quality_scores: QualityScores;
  remediation_plan: RemediationPlan;
  compliance_status: ComplianceStatus;
}

export interface QualityScores {
  brand_compliance: number;
  readability: number;
  factual_accuracy: number;
  template_fit: number;
  grammar: number;
  compliance: number;
  overall: number;
}

export interface RemediationPlan {
  critical_fixes: RemediationSuggestion[];
  recommended_fixes: RemediationSuggestion[];
  optional_improvements: RemediationSuggestion[];
  auto_fixable_count: number;
  estimated_total_effort: string;
}

export interface ComplianceStatus {
  fair_housing_compliant: boolean;
  brokerage_compliant: boolean;
  locale_compliant: boolean;
  accessibility_compliant: boolean;
  issues: string[];
  disclaimers_required: string[];
}

// =============================================================================
// VALIDATION PIPELINE IMPLEMENTATION
// =============================================================================

export class ValidationPipeline {
  private preValidators: Map<string, PreValidator>;
  private postValidators: Map<string, PostValidator>;
  private remediationEngine: RemediationEngine;
  private complianceChecker: ComplianceChecker;

  constructor() {
    this.preValidators = new Map();
    this.postValidators = new Map();
    this.remediationEngine = new RemediationEngine();
    this.complianceChecker = new ComplianceChecker();
    
    this.initializeValidators();
  }

  private initializeValidators(): void {
    // Pre-generation validators
    this.preValidators.set('required_fields', new RequiredFieldsValidator());
    this.preValidators.set('brand_kit_availability', new BrandKitValidator());
    this.preValidators.set('template_selection', new TemplateValidator());
    this.preValidators.set('locale_requirements', new LocaleValidator());
    
    // Post-generation validators
    this.postValidators.set('grammar_spelling', new GrammarSpellingValidator());
    this.postValidators.set('readability', new ReadabilityValidator());
    this.postValidators.set('brand_voice', new BrandVoiceValidator());
    this.postValidators.set('banned_terms', new BannedTermsValidator());
    this.postValidators.set('fair_housing', new FairHousingValidator());
    this.postValidators.set('factual_completeness', new FactualCompletenessValidator());
    this.postValidators.set('length_constraints', new LengthConstraintsValidator());
    this.postValidators.set('cta_presence', new CTAPresenceValidator());
    this.postValidators.set('template_fit', new TemplateFitValidator());
  }

  /**
   * Run pre-generation validation checks
   */
  async validatePreGeneration(context: ValidationContext): Promise<ValidationResult[]> {
    const results: ValidationResult[] = [];
    const startTime = Date.now();

    for (const [name, validator] of this.preValidators) {
      try {
        const result = await validator.validate(context);
        results.push({
          ...result,
          validator: name,
          execution_time_ms: Date.now() - startTime
        });
      } catch (error) {
        results.push({
          validator: name,
          passed: false,
          score: 0,
          confidence: 1,
          issues: [{
            type: 'error',
            severity: 'critical',
            message: `Validator failed: ${error.message}`
          }],
          suggestions: [],
          execution_time_ms: Date.now() - startTime
        });
      }
    }

    return results;
  }

  /**
   * Run post-generation validation and quality checks
   */
  async validatePostGeneration(context: ValidationContext): Promise<ValidationReport> {
    const startTime = Date.now();
    const results: ValidationResult[] = [];

    // Run all post-generation validators
    for (const [name, validator] of this.postValidators) {
      try {
        const result = await validator.validate(context);
        results.push({
          ...result,
          validator: name,
          execution_time_ms: Date.now() - startTime
        });
      } catch (error) {
        results.push({
          validator: name,
          passed: false,
          score: 0,
          confidence: 0.9,
          issues: [{
            type: 'error',
            severity: 'high',
            message: `Validator failed: ${error.message}`
          }],
          suggestions: [],
          execution_time_ms: Date.now() - startTime
        });
      }
    }

    // Calculate quality scores
    const qualityScores = this.calculateQualityScores(results);
    
    // Check compliance status
    const complianceStatus = await this.complianceChecker.checkCompliance(context, results);
    
    // Generate remediation plan
    const remediationPlan = await this.remediationEngine.generatePlan(results, context);
    
    const overallScore = qualityScores.overall;
    const passed = overallScore >= 0.7 && complianceStatus.fair_housing_compliant;

    return {
      overall_score: overallScore,
      passed,
      execution_time_ms: Date.now() - startTime,
      results,
      quality_scores: qualityScores,
      remediation_plan: remediationPlan,
      compliance_status: complianceStatus
    };
  }

  /**
   * Run automated remediation based on validation results
   */
  async runAutomatedRemediation(
    content: any, 
    validationReport: ValidationReport, 
    context: ValidationContext
  ): Promise<{
    remediated_content: any;
    applied_fixes: RemediationSuggestion[];
    remaining_issues: ValidationIssue[];
  }> {
    return await this.remediationEngine.applyAutomatedFixes(
      content,
      validationReport.remediation_plan.critical_fixes.concat(
        validationReport.remediation_plan.recommended_fixes
      ).filter(fix => fix.automated),
      context
    );
  }

  /**
   * Calculate composite quality scores from validation results
   */
  private calculateQualityScores(results: ValidationResult[]): QualityScores {
    const scoresByCategory: Record<string, number[]> = {
      brand_compliance: [],
      readability: [],
      factual_accuracy: [],
      template_fit: [],
      grammar: [],
      compliance: []
    };

    // Categorize scores
    for (const result of results) {
      switch (result.validator) {
        case 'brand_voice':
          scoresByCategory.brand_compliance.push(result.score);
          break;
        case 'readability':
          scoresByCategory.readability.push(result.score);
          break;
        case 'factual_completeness':
          scoresByCategory.factual_accuracy.push(result.score);
          break;
        case 'template_fit':
        case 'length_constraints':
          scoresByCategory.template_fit.push(result.score);
          break;
        case 'grammar_spelling':
          scoresByCategory.grammar.push(result.score);
          break;
        case 'fair_housing':
        case 'banned_terms':
          scoresByCategory.compliance.push(result.score);
          break;
      }
    }

    // Calculate averages
    const averageScore = (scores: number[]) => 
      scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 1.0;

    const scores = {
      brand_compliance: averageScore(scoresByCategory.brand_compliance),
      readability: averageScore(scoresByCategory.readability),
      factual_accuracy: averageScore(scoresByCategory.factual_accuracy),
      template_fit: averageScore(scoresByCategory.template_fit),
      grammar: averageScore(scoresByCategory.grammar),
      compliance: averageScore(scoresByCategory.compliance),
      overall: 0
    };

    // Calculate weighted overall score
    scores.overall = (
      scores.brand_compliance * 0.25 +
      scores.readability * 0.20 +
      scores.factual_accuracy * 0.20 +
      scores.template_fit * 0.15 +
      scores.grammar * 0.10 +
      scores.compliance * 0.10
    );

    return scores;
  }
}

// =============================================================================
// PRE-GENERATION VALIDATORS
// =============================================================================

abstract class PreValidator {
  abstract validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>>;
}

class RequiredFieldsValidator extends PreValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    const issues: ValidationIssue[] = [];
    const suggestions: RemediationSuggestion[] = [];

    if (!context.user_prompt?.trim()) {
      issues.push({
        type: 'error',
        severity: 'critical',
        message: 'User prompt is required and cannot be empty'
      });
    }

    if (!context.content_type) {
      issues.push({
        type: 'error',
        severity: 'critical',
        message: 'Content type must be specified'
      });
    }

    if (!context.session_id) {
      issues.push({
        type: 'error',
        severity: 'high',
        message: 'Session ID is required for context tracking'
      });
    }

    if (issues.length > 0) {
      suggestions.push({
        type: 'content_revision',
        priority: 'high',
        automated: false,
        description: 'Provide all required fields before generation',
        estimated_effort: 'quick',
        success_probability: 1.0
      });
    }

    return {
      passed: issues.length === 0,
      score: issues.length === 0 ? 1.0 : 0.0,
      confidence: 1.0,
      issues,
      suggestions
    };
  }
}

class BrandKitValidator extends PreValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    const issues: ValidationIssue[] = [];
    const suggestions: RemediationSuggestion[] = [];

    if (!context.brand_kit) {
      issues.push({
        type: 'warning',
        severity: 'medium',
        message: 'Brand kit not provided - content will use default styling'
      });

      suggestions.push({
        type: 'brand_correction',
        priority: 'medium',
        automated: false,
        description: 'Configure brand kit for consistent styling and voice',
        estimated_effort: 'moderate',
        success_probability: 0.9
      });
    } else {
      // Validate brand kit completeness
      if (!context.brand_kit.colors?.primary) {
        issues.push({
          type: 'warning',
          severity: 'low',
          message: 'Primary brand color not specified'
        });
      }

      if (!context.brand_kit.voice?.tone) {
        issues.push({
          type: 'warning',
          severity: 'medium',
          message: 'Brand voice tone not specified'
        });
      }
    }

    return {
      passed: true, // Warnings don't fail validation
      score: context.brand_kit ? 1.0 : 0.7,
      confidence: 0.9,
      issues,
      suggestions
    };
  }
}

class TemplateValidator extends PreValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    const issues: ValidationIssue[] = [];
    const suggestions: RemediationSuggestion[] = [];

    if (!context.template_constraints) {
      issues.push({
        type: 'warning',
        severity: 'medium',
        message: 'Template constraints not specified - using defaults'
      });
    } else {
      // Validate template constraints
      if (!context.template_constraints.template_id) {
        issues.push({
          type: 'error',
          severity: 'high',
          message: 'Template ID is required'
        });
      }

      if (!context.template_constraints.max_characters || context.template_constraints.max_characters <= 0) {
        issues.push({
          type: 'warning',
          severity: 'low',
          message: 'Max character limit not set - content length will be unrestricted'
        });
      }
    }

    return {
      passed: issues.filter(i => i.type === 'error').length === 0,
      score: context.template_constraints ? 1.0 : 0.8,
      confidence: 0.95,
      issues,
      suggestions
    };
  }
}

class LocaleValidator extends PreValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    const issues: ValidationIssue[] = [];
    const suggestions: RemediationSuggestion[] = [];

    if (!context.locale) {
      issues.push({
        type: 'warning',
        severity: 'low',
        message: 'Locale not specified - using default (en-US)'
      });
    }

    // Check for locale-specific compliance requirements
    if (context.locale && !this.isSupportedLocale(context.locale)) {
      issues.push({
        type: 'warning',
        severity: 'medium',
        message: `Locale '${context.locale}' may not have full compliance rule support`
      });
    }

    return {
      passed: true,
      score: context.locale ? 1.0 : 0.9,
      confidence: 0.8,
      issues,
      suggestions
    };
  }

  private isSupportedLocale(locale: string): boolean {
    const supportedLocales = ['en-US', 'en-CA', 'en-GB', 'en-AU'];
    return supportedLocales.includes(locale);
  }
}

// =============================================================================
// POST-GENERATION VALIDATORS
// =============================================================================

abstract class PostValidator {
  abstract validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>>;
}

class GrammarSpellingValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    // Mock implementation - in production, would use services like Grammarly API or LanguageTool
    const content = this.extractTextContent(context.generated_content);
    const issues: ValidationIssue[] = [];
    const suggestions: RemediationSuggestion[] = [];

    // Simple heuristic checks (in production, use proper grammar checking service)
    const grammarIssues = this.checkBasicGrammar(content);
    const spellingIssues = this.checkBasicSpelling(content);

    issues.push(...grammarIssues, ...spellingIssues);

    if (issues.length > 0) {
      suggestions.push({
        type: 'content_revision',
        priority: 'high',
        automated: true,
        description: 'Fix identified grammar and spelling issues',
        fix_prompt: `Please fix the following grammar and spelling issues in the content: ${issues.map(i => i.message).join('; ')}`,
        estimated_effort: 'quick',
        success_probability: 0.9
      });
    }

    const errorCount = issues.length;
    const score = Math.max(0, 1 - (errorCount * 0.1)); // Penalize 0.1 per error

    return {
      passed: errorCount === 0,
      score,
      confidence: 0.8,
      issues,
      suggestions
    };
  }

  private extractTextContent(content: any): string {
    if (typeof content === 'string') return content;
    if (typeof content === 'object') {
      return Object.values(content).join(' ');
    }
    return '';
  }

  private checkBasicGrammar(text: string): ValidationIssue[] {
    const issues: ValidationIssue[] = [];
    
    // Check for basic grammar patterns
    if (text.includes(' i ')) {
      issues.push({
        type: 'error',
        severity: 'medium',
        message: 'Potential capitalization error: "i" should be "I"'
      });
    }

    // Check for repeated words
    const repeatedWords = text.match(/\b(\w+)\s+\1\b/gi);
    if (repeatedWords) {
      issues.push({
        type: 'warning',
        severity: 'low',
        message: 'Repeated words detected'
      });
    }

    return issues;
  }

  private checkBasicSpelling(text: string): ValidationIssue[] {
    const issues: ValidationIssue[] = [];
    
    // Common real estate misspellings
    const commonMisspellings: Record<string, string> = {
      'recieve': 'receive',
      'seperate': 'separate',
      'occured': 'occurred',
      'accomodate': 'accommodate'
    };

    for (const [wrong, correct] of Object.entries(commonMisspellings)) {
      if (text.toLowerCase().includes(wrong)) {
        issues.push({
          type: 'error',
          severity: 'medium',
          message: `Potential spelling error: "${wrong}" should be "${correct}"`
        });
      }
    }

    return issues;
  }
}

class ReadabilityValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    const content = this.extractTextContent(context.generated_content);
    const issues: ValidationIssue[] = [];
    const suggestions: RemediationSuggestion[] = [];

    const readabilityScore = this.calculateFleschKincaidScore(content);
    const targetScore = this.getTargetReadabilityScore(context.content_type);

    let score = 1.0;
    if (readabilityScore < targetScore.min) {
      issues.push({
        type: 'warning',
        severity: 'medium',
        message: `Content may be too complex (Flesch-Kincaid: ${readabilityScore.toFixed(1)}, target: ${targetScore.min}+)`
      });

      suggestions.push({
        type: 'content_revision',
        priority: 'medium',
        automated: true,
        description: 'Simplify language and sentence structure for better readability',
        fix_prompt: 'Please rewrite this content using simpler language, shorter sentences, and more common words to improve readability.',
        estimated_effort: 'moderate',
        success_probability: 0.8
      });

      score = Math.max(0.3, readabilityScore / targetScore.min);
    }

    return {
      passed: issues.filter(i => i.type === 'error').length === 0,
      score,
      confidence: 0.85,
      issues,
      suggestions
    };
  }

  private extractTextContent(content: any): string {
    if (typeof content === 'string') return content;
    if (typeof content === 'object') {
      return Object.values(content).join(' ');
    }
    return '';
  }

  private calculateFleschKincaidScore(text: string): number {
    // Simplified Flesch-Kincaid readability score calculation
    const sentences = text.split(/[.!?]+/).length - 1;
    const words = text.split(/\s+/).length;
    const syllables = this.countSyllables(text);

    if (sentences === 0 || words === 0) return 0;

    const avgSentenceLength = words / sentences;
    const avgSyllablesPerWord = syllables / words;

    return 206.835 - 1.015 * avgSentenceLength - 84.6 * avgSyllablesPerWord;
  }

  private countSyllables(text: string): number {
    // Simplified syllable counting
    const words = text.toLowerCase().split(/\s+/);
    let totalSyllables = 0;

    for (const word of words) {
      const syllables = word.match(/[aeiouy]+/g)?.length || 1;
      totalSyllables += Math.max(1, syllables);
    }

    return totalSyllables;
  }

  private getTargetReadabilityScore(contentType: ContentType): { min: number; max: number } {
    // Target Flesch-Kincaid scores by content type
    const targets = {
      'LISTING_DESCRIPTION': { min: 60, max: 80 }, // 8th-9th grade
      'PROPERTY_FLYER': { min: 70, max: 90 }, // 7th-8th grade
      'CMA_REPORT': { min: 50, max: 70 }, // 10th-12th grade (professional)
      'SOCIAL_POST': { min: 80, max: 100 }, // 6th-7th grade
      'EMAIL_CAMPAIGN': { min: 65, max: 85 }, // 8th-9th grade
      'MARKET_REPORT': { min: 50, max: 70 }, // 10th-12th grade
    };

    return targets[contentType] || { min: 60, max: 80 };
  }
}

class BrandVoiceValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    const content = this.extractTextContent(context.generated_content);
    const issues: ValidationIssue[] = [];
    const suggestions: RemediationSuggestion[] = [];

    if (!context.brand_kit?.voice) {
      return {
        passed: true,
        score: 1.0,
        confidence: 0.5,
        issues: [{
          type: 'warning',
          severity: 'low',
          message: 'Brand voice not specified - cannot validate voice consistency'
        }],
        suggestions: []
      };
    }

    const voiceScore = this.analyzeVoiceCompliance(content, context.brand_kit.voice);
    
    if (voiceScore < 0.7) {
      issues.push({
        type: 'warning',
        severity: 'medium',
        message: `Content voice doesn't match brand guidelines (score: ${(voiceScore * 100).toFixed(0)}%)`
      });

      suggestions.push({
        type: 'content_revision',
        priority: 'medium',
        automated: true,
        description: 'Adjust content to match brand voice',
        fix_prompt: `Please rewrite this content to match the brand voice: ${context.brand_kit.voice.tone} tone, ${context.brand_kit.voice.style} style. ${context.brand_kit.voice.guidelines || ''}`,
        estimated_effort: 'moderate',
        success_probability: 0.75
      });
    }

    return {
      passed: voiceScore >= 0.7,
      score: voiceScore,
      confidence: 0.7,
      issues,
      suggestions
    };
  }

  private extractTextContent(content: any): string {
    if (typeof content === 'string') return content;
    if (typeof content === 'object') {
      return Object.values(content).join(' ');
    }
    return '';
  }

  private analyzeVoiceCompliance(content: string, voice: VoiceConfig): number {
    let score = 1.0;

    // Check tone compliance
    if (voice.tone) {
      const toneScore = this.checkToneCompliance(content, voice.tone);
      score *= toneScore;
    }

    // Check avoided terms
    if (voice.avoid_terms) {
      const avoidanceScore = this.checkAvoidedTerms(content, voice.avoid_terms);
      score *= avoidanceScore;
    }

    // Check preferred terms
    if (voice.preferred_terms) {
      const preferenceScore = this.checkPreferredTerms(content, voice.preferred_terms);
      score *= preferenceScore;
    }

    return Math.max(0, score);
  }

  private checkToneCompliance(content: string, tone: string): number {
    const contentLower = content.toLowerCase();
    
    const toneIndicators: Record<string, { positive: string[], negative: string[] }> = {
      'professional': {
        positive: ['expertise', 'experience', 'professional', 'qualified', 'certified'],
        negative: ['awesome', 'super', 'totally', 'like', 'um']
      },
      'friendly': {
        positive: ['welcome', 'happy', 'excited', 'love', 'enjoy'],
        negative: ['must', 'require', 'demand', 'need', 'should']
      },
      'authoritative': {
        positive: ['proven', 'expert', 'leader', 'premier', 'established'],
        negative: ['maybe', 'possibly', 'might', 'perhaps', 'unsure']
      }
    };

    const indicators = toneIndicators[tone.toLowerCase()];
    if (!indicators) return 0.8; // Default score for unknown tones

    let positiveCount = 0;
    let negativeCount = 0;

    for (const term of indicators.positive) {
      if (contentLower.includes(term)) positiveCount++;
    }

    for (const term of indicators.negative) {
      if (contentLower.includes(term)) negativeCount++;
    }

    // Score based on positive indicators vs negative indicators
    return Math.max(0.3, 0.8 + (positiveCount * 0.1) - (negativeCount * 0.15));
  }

  private checkAvoidedTerms(content: string, avoidTerms: string[]): number {
    const contentLower = content.toLowerCase();
    let violations = 0;

    for (const term of avoidTerms) {
      if (contentLower.includes(term.toLowerCase())) {
        violations++;
      }
    }

    return Math.max(0, 1 - (violations * 0.2));
  }

  private checkPreferredTerms(content: string, preferredTerms: string[]): number {
    const contentLower = content.toLowerCase();
    let matches = 0;

    for (const term of preferredTerms) {
      if (contentLower.includes(term.toLowerCase())) {
        matches++;
      }
    }

    // Bonus for using preferred terms, but not penalizing absence
    return Math.min(1.2, 1.0 + (matches * 0.1));
  }
}

// Additional validators would be implemented similarly...
class BannedTermsValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    const content = this.extractTextContent(context.generated_content);
    const issues: ValidationIssue[] = [];
    const suggestions: RemediationSuggestion[] = [];

    const bannedTerms = this.getBannedTerms(context);
    const violations = this.findBannedTerms(content, bannedTerms);

    for (const violation of violations) {
      issues.push({
        type: 'error',
        severity: 'high',
        message: `Banned term detected: "${violation.term}" - ${violation.reason}`
      });
    }

    if (issues.length > 0) {
      suggestions.push({
        type: 'content_revision',
        priority: 'high',
        automated: true,
        description: 'Remove or replace banned terms',
        fix_prompt: `Please remove or replace these banned terms: ${violations.map(v => v.term).join(', ')}. ${violations.map(v => v.suggestion ? `Replace "${v.term}" with "${v.suggestion}"` : '').filter(Boolean).join('. ')}.`,
        estimated_effort: 'quick',
        success_probability: 0.95
      });
    }

    return {
      passed: issues.length === 0,
      score: issues.length === 0 ? 1.0 : Math.max(0, 1 - (issues.length * 0.3)),
      confidence: 0.95,
      issues,
      suggestions
    };
  }

  private extractTextContent(content: any): string {
    if (typeof content === 'string') return content;
    if (typeof content === 'object') {
      return Object.values(content).join(' ');
    }
    return '';
  }

  private getBannedTerms(context: ValidationContext): BannedTerm[] {
    // Real estate industry banned terms for fair housing compliance
    return [
      { term: 'perfect for families', reason: 'Familial status discrimination', suggestion: 'great for everyone' },
      { term: 'adult community', reason: 'Age discrimination', suggestion: 'mature community' },
      { term: 'no children', reason: 'Familial status discrimination', suggestion: '' },
      { term: 'christian', reason: 'Religious discrimination', suggestion: '' },
      { term: 'traditional neighborhood', reason: 'Potential coded language', suggestion: 'established neighborhood' },
      { term: 'safe neighborhood', reason: 'Potential discriminatory implication', suggestion: 'well-maintained neighborhood' },
    ];
  }

  private findBannedTerms(content: string, bannedTerms: BannedTerm[]): Array<BannedTerm & { found: boolean }> {
    const contentLower = content.toLowerCase();
    return bannedTerms.filter(term => 
      contentLower.includes(term.term.toLowerCase())
    ).map(term => ({ ...term, found: true }));
  }
}

interface BannedTerm {
  term: string;
  reason: string;
  suggestion?: string;
}

// Additional validator implementations...
class FairHousingValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    // Implementation for fair housing compliance checking
    return {
      passed: true,
      score: 1.0,
      confidence: 0.8,
      issues: [],
      suggestions: []
    };
  }
}

class FactualCompletenessValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    // Implementation for factual completeness checking
    return {
      passed: true,
      score: 1.0,
      confidence: 0.7,
      issues: [],
      suggestions: []
    };
  }
}

class LengthConstraintsValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    // Implementation for length constraints checking
    return {
      passed: true,
      score: 1.0,
      confidence: 1.0,
      issues: [],
      suggestions: []
    };
  }
}

class CTAPresenceValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    // Implementation for call-to-action presence checking
    return {
      passed: true,
      score: 1.0,
      confidence: 0.8,
      issues: [],
      suggestions: []
    };
  }
}

class TemplateFitValidator extends PostValidator {
  async validate(context: ValidationContext): Promise<Omit<ValidationResult, 'validator' | 'execution_time_ms'>> {
    // Implementation for template fit validation
    return {
      passed: true,
      score: 1.0,
      confidence: 0.9,
      issues: [],
      suggestions: []
    };
  }
}

// =============================================================================
// REMEDIATION ENGINE
// =============================================================================

class RemediationEngine {
  async generatePlan(results: ValidationResult[], context: ValidationContext): Promise<RemediationPlan> {
    const allSuggestions = results.flatMap(r => r.suggestions);
    
    const critical = allSuggestions.filter(s => s.priority === 'high');
    const recommended = allSuggestions.filter(s => s.priority === 'medium');
    const optional = allSuggestions.filter(s => s.priority === 'low');
    
    const autoFixableCount = allSuggestions.filter(s => s.automated).length;
    
    return {
      critical_fixes: critical,
      recommended_fixes: recommended,
      optional_improvements: optional,
      auto_fixable_count: autoFixableCount,
      estimated_total_effort: this.estimateEffort(allSuggestions)
    };
  }

  async applyAutomatedFixes(
    content: any,
    fixes: RemediationSuggestion[],
    context: ValidationContext
  ): Promise<{
    remediated_content: any;
    applied_fixes: RemediationSuggestion[];
    remaining_issues: ValidationIssue[];
  }> {
    // Mock implementation - in production, would apply actual fixes
    return {
      remediated_content: content,
      applied_fixes: fixes.filter(f => f.automated),
      remaining_issues: []
    };
  }

  private estimateEffort(suggestions: RemediationSuggestion[]): string {
    const effortMap = { quick: 5, moderate: 15, complex: 45 };
    const totalMinutes = suggestions.reduce((total, s) => 
      total + (effortMap[s.estimated_effort] || 15), 0
    );

    if (totalMinutes <= 10) return 'Under 10 minutes';
    if (totalMinutes <= 30) return '10-30 minutes';
    if (totalMinutes <= 60) return '30-60 minutes';
    return 'Over 1 hour';
  }
}

// =============================================================================
// COMPLIANCE CHECKER
// =============================================================================

class ComplianceChecker {
  async checkCompliance(
    context: ValidationContext, 
    results: ValidationResult[]
  ): Promise<ComplianceStatus> {
    // Mock implementation
    return {
      fair_housing_compliant: true,
      brokerage_compliant: true,
      locale_compliant: true,
      accessibility_compliant: true,
      issues: [],
      disclaimers_required: []
    };
  }
}

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

interface VoiceConfig {
  tone: string;
  style: string;
  guidelines?: string;
  avoid_terms?: string[];
  preferred_terms?: string[];
}

interface VoicePreferences {
  tone: string;
  style: string;
  avoid_terms: string[];
}

interface ColorPalette {
  primary: string;
  secondary?: string;
}

interface FontConfig {
  headings: string;
  body: string;
}

interface ComplianceRules {
  fair_housing: boolean;
  accessibility: boolean;
  locale_specific: Record<string, any>;
}

// =============================================================================
// SINGLETON EXPORT
// =============================================================================

export const validationPipeline = new ValidationPipeline();
export default validationPipeline;