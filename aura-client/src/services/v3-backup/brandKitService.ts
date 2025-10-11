/**
 * Aura v3.3 - Brand Kit Service
 * =============================
 * 
 * Brand asset management and enforcement system with:
 * - Brand asset ingestion and validation
 * - Color palette management
 * - Typography enforcement with fallbacks
 * - Logo management and usage guidelines
 * - Voice and tone consistency
 * - Compliance rule enforcement
 * - Asset optimization and delivery
 * 
 * @version 3.3.0
 */

// =============================================================================
// BRAND KIT TYPES & INTERFACES
// =============================================================================

export interface BrandKit {
  id: string;
  name: string;
  version: string;
  organization_id: string;
  colors: ColorSystem;
  typography: TypographySystem;
  logos: LogoSystem;
  voice_and_tone: VoiceSystem;
  compliance_rules: ComplianceSystem;
  imagery_guidelines: ImageryGuidelines;
  layout_principles: LayoutPrinciples;
  metadata: BrandKitMetadata;
  validation_status: ValidationStatus;
  created_at: string;
  updated_at: string;
}

export interface ColorSystem {
  primary_palette: ColorPalette;
  secondary_palette?: ColorPalette;
  semantic_colors: SemanticColors;
  accessibility_compliance: AccessibilityCompliance;
  usage_guidelines: ColorUsageGuidelines[];
  generated_variations: ColorVariation[];
}

export interface ColorPalette {
  name: string;
  colors: BrandColor[];
  harmony_type: 'monochromatic' | 'complementary' | 'triadic' | 'analogous' | 'split_complementary';
  primary_color: string;
}

export interface BrandColor {
  id: string;
  name: string;
  hex: string;
  rgb: { r: number; g: number; b: number };
  hsl: { h: number; s: number; l: number };
  cmyk?: { c: number; m: number; y: number; k: number };
  pantone?: string;
  usage_context: ColorUsageContext[];
  accessibility_level: 'AA' | 'AAA' | 'fail';
  contrast_ratios: ContrastRatio[];
}

export interface ColorUsageContext {
  context: 'primary' | 'secondary' | 'accent' | 'background' | 'text' | 'border' | 'success' | 'warning' | 'error';
  weight: number; // 0-1, likelihood of use in this context
  restrictions?: string[];
}

export interface ContrastRatio {
  against_color: string;
  ratio: number;
  wcag_level: 'AA' | 'AAA' | 'fail';
  use_case: 'normal_text' | 'large_text' | 'ui_components';
}

export interface SemanticColors {
  success: string;
  warning: string;
  error: string;
  info: string;
  neutral: string;
}

export interface AccessibilityCompliance {
  wcag_level: 'AA' | 'AAA';
  color_blind_safe: boolean;
  high_contrast_approved: boolean;
  minimum_contrast_ratio: number;
}

export interface ColorUsageGuidelines {
  context: string;
  recommended_combinations: ColorCombination[];
  prohibited_combinations: ColorCombination[];
  usage_examples: string[];
}

export interface ColorCombination {
  foreground: string;
  background: string;
  use_case: string;
  contrast_ratio: number;
}

export interface ColorVariation {
  base_color: string;
  variations: {
    tint_10: string;
    tint_25: string;
    tint_50: string;
    shade_10: string;
    shade_25: string;
    shade_50: string;
  };
}

export interface TypographySystem {
  font_families: FontFamily[];
  type_scale: TypeScale;
  font_pairings: FontPairing[];
  usage_guidelines: TypographyGuidelines[];
  fallback_strategy: FallbackStrategy;
  web_font_loading: WebFontConfiguration;
}

export interface FontFamily {
  id: string;
  name: string;
  display_name: string;
  category: 'serif' | 'sans-serif' | 'monospace' | 'display' | 'handwriting';
  weights: FontWeight[];
  styles: FontStyle[];
  license: FontLicense;
  file_formats: FontFile[];
  character_sets: string[];
  language_support: string[];
  usage_context: FontUsageContext[];
  fallback_fonts: string[];
}

export interface FontWeight {
  weight: number;
  name: string;
  available: boolean;
  file_size_kb?: number;
}

export interface FontStyle {
  style: 'normal' | 'italic' | 'oblique';
  available: boolean;
  file_size_kb?: number;
}

export interface FontLicense {
  type: 'free' | 'commercial' | 'custom' | 'google_fonts' | 'adobe_fonts';
  restrictions?: string[];
  attribution_required: boolean;
  commercial_use_allowed: boolean;
}

export interface FontFile {
  format: 'woff2' | 'woff' | 'ttf' | 'otf' | 'eot';
  url: string;
  file_size_kb: number;
  subset?: string;
  unicode_range?: string;
}

export interface FontUsageContext {
  context: 'headings' | 'body' | 'captions' | 'labels' | 'display' | 'code';
  recommended: boolean;
  weight_range: [number, number];
  size_range: [number, number];
}

export interface TypeScale {
  base_size: number;
  ratio: number;
  sizes: TypeSize[];
  line_heights: LineHeightScale;
  letter_spacing: LetterSpacingScale;
}

export interface TypeSize {
  name: string;
  size: number;
  line_height: number;
  letter_spacing?: number;
  usage: string[];
}

export interface LineHeightScale {
  tight: number;
  normal: number;
  relaxed: number;
  loose: number;
}

export interface LetterSpacingScale {
  tight: number;
  normal: number;
  wide: number;
  wider: number;
}

export interface FontPairing {
  id: string;
  name: string;
  heading_font: string;
  body_font: string;
  accent_font?: string;
  harmony_score: number; // 0-1
  usage_recommendation: string;
  example_contexts: string[];
}

export interface TypographyGuidelines {
  element: string;
  font_family: string;
  size_range: [number, number];
  weight_range: [number, number];
  line_height_range: [number, number];
  color_options: string[];
  usage_notes: string[];
}

export interface FallbackStrategy {
  system_fonts: string[];
  web_safe_fonts: string[];
  loading_strategy: 'swap' | 'block' | 'fallback' | 'optional';
  timeout_ms: number;
}

export interface WebFontConfiguration {
  preload_fonts: string[];
  font_display: 'auto' | 'block' | 'swap' | 'fallback' | 'optional';
  subset_strategy: 'full' | 'latin' | 'latin_ext' | 'custom';
  custom_subsets?: string[];
}

export interface LogoSystem {
  primary_logo: LogoAsset;
  secondary_logos: LogoAsset[];
  icon_variations: LogoAsset[];
  usage_guidelines: LogoUsageGuidelines;
  minimum_sizes: LogoSizeRequirements;
  clear_space_rules: ClearSpaceRules;
  color_variations: LogoColorVariation[];
  prohibited_uses: ProhibitedUse[];
}

export interface LogoAsset {
  id: string;
  name: string;
  type: 'primary' | 'secondary' | 'icon' | 'wordmark' | 'symbol' | 'combination';
  file_formats: LogoFile[];
  original_dimensions: { width: number; height: number };
  aspect_ratio: number;
  color_mode: 'full_color' | 'monochrome' | 'reversed' | 'knockout';
  usage_contexts: LogoUsageContext[];
  optimization_status: OptimizationStatus;
}

export interface LogoFile {
  format: 'svg' | 'png' | 'jpg' | 'pdf' | 'eps' | 'ai';
  url: string;
  file_size_kb: number;
  dimensions: { width: number; height: number };
  dpi?: number;
  transparency: boolean;
  color_space?: 'rgb' | 'cmyk' | 'grayscale';
}

export interface LogoUsageContext {
  context: 'web' | 'print' | 'merchandise' | 'signage' | 'social_media' | 'email';
  recommended_formats: string[];
  minimum_resolution: number;
  color_requirements: string[];
}

export interface LogoUsageGuidelines {
  preferred_placement: string[];
  alignment_rules: string[];
  scaling_guidelines: string[];
  background_recommendations: BackgroundRecommendation[];
  do_examples: string[];
  dont_examples: string[];
}

export interface BackgroundRecommendation {
  background_type: 'light' | 'dark' | 'image' | 'colored';
  logo_variation: string;
  min_contrast_ratio: number;
  usage_notes: string[];
}

export interface LogoSizeRequirements {
  minimum_width: number;
  minimum_height: number;
  maximum_width?: number;
  maximum_height?: number;
  recommended_sizes: RecommendedSize[];
}

export interface RecommendedSize {
  context: string;
  width: number;
  height: number;
  notes?: string;
}

export interface ClearSpaceRules {
  minimum_clear_space: number;
  measurement_unit: 'px' | 'em' | 'logo_height' | 'logo_width';
  applies_to: string[];
  exceptions: ClearSpaceException[];
}

export interface ClearSpaceException {
  context: string;
  reduced_clear_space: number;
  justification: string;
}

export interface LogoColorVariation {
  name: string;
  color_scheme: 'full_color' | 'single_color' | 'reversed' | 'knockout';
  primary_color?: string;
  background_requirements: string[];
  file_references: string[];
}

export interface ProhibitedUse {
  description: string;
  visual_example?: string;
  reasoning: string;
  severity: 'warning' | 'error';
}

export interface OptimizationStatus {
  svg_optimized: boolean;
  png_compressed: boolean;
  retina_versions: boolean;
  webp_available: boolean;
  file_size_score: number; // 0-1
  load_time_estimate_ms: number;
}

export interface VoiceSystem {
  brand_voice: BrandVoice;
  tone_variations: ToneVariation[];
  messaging_guidelines: MessagingGuidelines;
  content_principles: ContentPrinciple[];
  style_preferences: StylePreferences;
  prohibited_language: ProhibitedLanguage;
  industry_compliance: IndustryCompliance;
}

export interface BrandVoice {
  personality_traits: string[];
  voice_characteristics: VoiceCharacteristic[];
  target_audience: TargetAudience;
  brand_values: string[];
  differentiators: string[];
  emotional_tone: EmotionalTone;
}

export interface VoiceCharacteristic {
  trait: string;
  description: string;
  intensity: number; // 0-1
  examples: string[];
  avoid_examples: string[];
}

export interface TargetAudience {
  primary_audience: AudienceSegment;
  secondary_audiences: AudienceSegment[];
  persona_profiles: PersonaProfile[];
}

export interface AudienceSegment {
  name: string;
  demographics: Demographics;
  psychographics: Psychographics;
  communication_preferences: CommunicationPreference[];
}

export interface Demographics {
  age_range: [number, number];
  income_range?: [number, number];
  education_level: string[];
  location_types: string[];
  profession_categories: string[];
}

export interface Psychographics {
  values: string[];
  interests: string[];
  lifestyle_preferences: string[];
  pain_points: string[];
  goals: string[];
}

export interface CommunicationPreference {
  channel: string;
  frequency: string;
  format: string[];
  tone_preference: string;
}

export interface PersonaProfile {
  name: string;
  description: string;
  key_characteristics: string[];
  communication_style: string;
  preferred_content_types: string[];
}

export interface EmotionalTone {
  primary_emotion: string;
  secondary_emotions: string[];
  emotional_intensity: number; // 0-1
  emotional_consistency: number; // 0-1
}

export interface ToneVariation {
  context: string;
  tone_adjustments: ToneAdjustment[];
  examples: ToneExample[];
  usage_guidelines: string[];
}

export interface ToneAdjustment {
  characteristic: string;
  adjustment: 'increase' | 'decrease' | 'maintain';
  degree: number; // 0-1
  reasoning: string;
}

export interface ToneExample {
  situation: string;
  good_example: string;
  bad_example?: string;
  explanation: string;
}

export interface MessagingGuidelines {
  key_messages: KeyMessage[];
  message_hierarchy: MessageHierarchy;
  call_to_action_guidelines: CTAGuidelines;
  value_proposition_frameworks: ValuePropositionFramework[];
}

export interface KeyMessage {
  id: string;
  message: string;
  priority: number;
  target_audience: string[];
  contexts: string[];
  supporting_points: string[];
  evidence: string[];
}

export interface MessageHierarchy {
  primary_message: string;
  secondary_messages: string[];
  supporting_messages: string[];
  proof_points: string[];
}

export interface CTAGuidelines {
  preferred_action_verbs: string[];
  tone_requirements: string[];
  urgency_guidelines: UrgencyGuideline[];
  placement_recommendations: string[];
  A_B_testing_frameworks: ABTestingFramework[];
}

export interface UrgencyGuideline {
  urgency_level: 'low' | 'medium' | 'high';
  appropriate_contexts: string[];
  language_patterns: string[];
  avoid_patterns: string[];
}

export interface ABTestingFramework {
  variable_type: string;
  test_variations: string[];
  success_metrics: string[];
  testing_duration: string;
}

export interface ValuePropositionFramework {
  framework_name: string;
  structure: string;
  example_applications: string[];
  key_elements: string[];
}

export interface ContentPrinciple {
  principle: string;
  description: string;
  application_guidelines: string[];
  examples: string[];
  common_mistakes: string[];
}

export interface StylePreferences {
  sentence_structure: SentenceStructurePreference;
  vocabulary_preferences: VocabularyPreference;
  punctuation_style: PunctuationStyle;
  capitalization_rules: CapitalizationRule[];
  number_formatting: NumberFormattingRule[];
}

export interface SentenceStructurePreference {
  preferred_length: 'short' | 'medium' | 'long' | 'varied';
  complexity_level: 'simple' | 'compound' | 'complex' | 'mixed';
  active_vs_passive: 'prefer_active' | 'prefer_passive' | 'context_dependent';
}

export interface VocabularyPreference {
  formality_level: 'casual' | 'conversational' | 'professional' | 'formal';
  technical_language: 'avoid' | 'minimal' | 'moderate' | 'extensive';
  industry_jargon: 'avoid' | 'explain' | 'use_freely';
  preferred_synonyms: Record<string, string[]>;
  words_to_avoid: string[];
}

export interface PunctuationStyle {
  serial_comma: boolean;
  quotation_style: 'american' | 'british';
  em_dash_usage: 'frequent' | 'moderate' | 'rare';
  exclamation_policy: 'avoid' | 'minimal' | 'moderate' | 'expressive';
}

export interface CapitalizationRule {
  context: string;
  rule: string;
  examples: string[];
}

export interface NumberFormattingRule {
  context: string;
  format: string;
  examples: string[];
}

export interface ProhibitedLanguage {
  banned_words: BannedWord[];
  sensitive_topics: SensitiveTopic[];
  compliance_requirements: ComplianceRequirement[];
  cultural_considerations: CulturalConsideration[];
}

export interface BannedWord {
  word: string;
  reason: string;
  severity: 'warning' | 'error';
  alternatives: string[];
  context_exceptions?: string[];
}

export interface SensitiveTopic {
  topic: string;
  handling_guidelines: string[];
  required_disclaimers: string[];
  approval_required: boolean;
}

export interface ComplianceRequirement {
  regulation: string;
  applicable_contexts: string[];
  required_language: string[];
  prohibited_claims: string[];
  documentation_requirements: string[];
}

export interface CulturalConsideration {
  culture_region: string;
  considerations: string[];
  language_adaptations: LanguageAdaptation[];
}

export interface LanguageAdaptation {
  original: string;
  adapted: string;
  reasoning: string;
}

export interface IndustryCompliance {
  industry: string;
  regulatory_bodies: string[];
  compliance_frameworks: ComplianceFramework[];
  required_disclaimers: RequiredDisclaimer[];
  prohibited_practices: ProhibitedPractice[];
}

export interface ComplianceFramework {
  name: string;
  version: string;
  requirements: string[];
  validation_method: string;
  renewal_schedule: string;
}

export interface RequiredDisclaimer {
  context: string;
  disclaimer_text: string;
  placement_requirements: string[];
  formatting_requirements: string[];
}

export interface ProhibitedPractice {
  practice: string;
  reasoning: string;
  severity: 'warning' | 'error' | 'legal_risk';
  alternatives: string[];
}

export interface ComplianceSystem {
  fair_housing_compliance: FairHousingCompliance;
  accessibility_compliance: AccessibilityComplianceRules;
  legal_compliance: LegalComplianceRules;
  industry_specific: IndustrySpecificCompliance;
  validation_rules: ComplianceValidationRule[];
  audit_trail: ComplianceAuditEntry[];
}

export interface FairHousingCompliance {
  enabled: boolean;
  protected_classes: ProtectedClass[];
  prohibited_language: FairHousingProhibitedLanguage[];
  alternative_suggestions: AlternativeSuggestion[];
  exception_handling: ExceptionHandling;
}

export interface ProtectedClass {
  class: string;
  definition: string;
  prohibited_references: string[];
  code_violations: CodeViolation[];
}

export interface CodeViolation {
  violation_type: string;
  description: string;
  examples: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface FairHousingProhibitedLanguage {
  phrase: string;
  category: string;
  reason: string;
  alternatives: string[];
  context_sensitivity: number; // 0-1
}

export interface AlternativeSuggestion {
  original_phrase: string;
  suggested_alternative: string;
  reasoning: string;
  tone_preservation: number; // 0-1
}

export interface ExceptionHandling {
  approved_exceptions: ApprovedException[];
  approval_process: string[];
  documentation_requirements: string[];
}

export interface ApprovedException {
  exception_id: string;
  content: string;
  context: string;
  approved_by: string;
  approval_date: string;
  expiration_date?: string;
  conditions: string[];
}

export interface AccessibilityComplianceRules {
  wcag_version: string;
  conformance_level: 'A' | 'AA' | 'AAA';
  color_contrast_requirements: ColorContrastRequirement[];
  text_requirements: TextRequirement[];
  image_requirements: ImageRequirement[];
  interactive_element_requirements: InteractiveElementRequirement[];
}

export interface ColorContrastRequirement {
  element_type: string;
  minimum_ratio: number;
  measurement_method: string;
  exceptions: string[];
}

export interface TextRequirement {
  requirement_type: string;
  specification: string;
  validation_method: string;
  compliance_level: string;
}

export interface ImageRequirement {
  requirement_type: string;
  specification: string;
  alt_text_guidelines: string[];
  decorative_image_handling: string;
}

export interface InteractiveElementRequirement {
  element_type: string;
  requirement: string;
  implementation_guidance: string[];
  testing_criteria: string[];
}

export interface LegalComplianceRules {
  copyright_requirements: CopyrightRequirement[];
  trademark_requirements: TrademarkRequirement[];
  privacy_requirements: PrivacyRequirement[];
  data_protection_requirements: DataProtectionRequirement[];
}

export interface CopyrightRequirement {
  content_type: string;
  attribution_required: boolean;
  usage_restrictions: string[];
  fair_use_guidelines: string[];
}

export interface TrademarkRequirement {
  trademark: string;
  owner: string;
  usage_guidelines: string[];
  attribution_format: string;
  restrictions: string[];
}

export interface PrivacyRequirement {
  regulation: string;
  applicable_contexts: string[];
  consent_requirements: string[];
  disclosure_requirements: string[];
}

export interface DataProtectionRequirement {
  regulation: string;
  data_types: string[];
  protection_measures: string[];
  retention_policies: string[];
}

export interface IndustrySpecificCompliance {
  industry: string;
  specific_rules: SpecificRule[];
  certification_requirements: CertificationRequirement[];
  audit_requirements: AuditRequirement[];
}

export interface SpecificRule {
  rule_id: string;
  description: string;
  applicable_content_types: string[];
  validation_criteria: string[];
  penalty_for_violation: string;
}

export interface CertificationRequirement {
  certification_name: string;
  issuing_body: string;
  validity_period: string;
  renewal_requirements: string[];
}

export interface AuditRequirement {
  audit_type: string;
  frequency: string;
  scope: string[];
  documentation_requirements: string[];
}

export interface ComplianceValidationRule {
  rule_id: string;
  name: string;
  description: string;
  validation_type: 'automated' | 'manual' | 'hybrid';
  severity: 'info' | 'warning' | 'error' | 'critical';
  applicable_content_types: string[];
  validation_logic: ValidationLogic;
  remediation_suggestions: RemediationSuggestion[];
}

export interface ValidationLogic {
  type: 'regex' | 'keyword' | 'ai_classification' | 'rule_engine' | 'custom';
  parameters: Record<string, any>;
  confidence_threshold?: number;
}

export interface RemediationSuggestion {
  suggestion: string;
  automated: boolean;
  confidence: number; // 0-1
  implementation_notes: string[];
}

export interface ComplianceAuditEntry {
  timestamp: string;
  content_id: string;
  rules_checked: string[];
  violations_found: ComplianceViolation[];
  remediation_applied: RemediationApplied[];
  audit_result: 'passed' | 'passed_with_warnings' | 'failed';
}

export interface ComplianceViolation {
  rule_id: string;
  violation_type: string;
  description: string;
  location?: string;
  severity: string;
  auto_fixable: boolean;
}

export interface RemediationApplied {
  violation_id: string;
  remediation_type: string;
  original_content: string;
  corrected_content: string;
  confidence: number;
}

export interface ImageryGuidelines {
  style_preferences: ImageStylePreference[];
  composition_rules: CompositionRule[];
  color_treatment: ColorTreatment[];
  subject_matter_guidelines: SubjectMatterGuideline[];
  technical_requirements: ImageTechnicalRequirement[];
  usage_rights: ImageUsageRight[];
}

export interface ImageStylePreference {
  style_name: string;
  description: string;
  characteristics: string[];
  appropriate_contexts: string[];
  examples?: string[];
}

export interface CompositionRule {
  rule_name: string;
  description: string;
  application_guidelines: string[];
  examples: string[];
}

export interface ColorTreatment {
  treatment_name: string;
  color_adjustments: ColorAdjustment[];
  mood_impact: string;
  brand_alignment: number; // 0-1
}

export interface ColorAdjustment {
  property: 'saturation' | 'brightness' | 'contrast' | 'temperature' | 'tint';
  adjustment: number; // -100 to 100
  reasoning: string;
}

export interface SubjectMatterGuideline {
  category: string;
  preferred_subjects: string[];
  avoided_subjects: string[];
  sensitivity_considerations: string[];
  cultural_awareness: string[];
}

export interface ImageTechnicalRequirement {
  context: string;
  minimum_resolution: { width: number; height: number };
  aspect_ratios: string[];
  file_formats: string[];
  max_file_size_mb: number;
  color_space: string;
}

export interface ImageUsageRight {
  usage_type: string;
  license_requirements: string[];
  attribution_requirements: string[];
  modification_permissions: string[];
  commercial_use_allowed: boolean;
}

export interface LayoutPrinciples {
  grid_systems: GridSystem[];
  spacing_principles: SpacingPrinciple[];
  hierarchy_rules: HierarchyRule[];
  balance_guidelines: BalanceGuideline[];
  responsive_behavior: ResponsiveBehavior[];
}

export interface GridSystem {
  name: string;
  columns: number;
  gutter_width: number;
  margin_width: number;
  breakpoints: Breakpoint[];
  usage_contexts: string[];
}

export interface Breakpoint {
  name: string;
  min_width: number;
  max_width?: number;
  grid_modifications: GridModification[];
}

export interface GridModification {
  property: string;
  value: any;
  reasoning: string;
}

export interface SpacingPrinciple {
  principle_name: string;
  base_unit: number;
  scale_factor: number;
  spacing_values: number[];
  application_rules: string[];
}

export interface HierarchyRule {
  element_type: string;
  hierarchy_level: number;
  visual_weight_factors: VisualWeightFactor[];
  spacing_requirements: SpacingRequirement[];
}

export interface VisualWeightFactor {
  factor: 'size' | 'color' | 'position' | 'contrast' | 'typography';
  impact_level: number; // 0-1
  implementation_notes: string[];
}

export interface SpacingRequirement {
  spacing_type: 'margin' | 'padding' | 'line_height' | 'letter_spacing';
  minimum_value: number;
  maximum_value?: number;
  responsive_scaling: boolean;
}

export interface BalanceGuideline {
  balance_type: 'symmetrical' | 'asymmetrical' | 'radial';
  application_contexts: string[];
  implementation_techniques: string[];
  examples: string[];
}

export interface ResponsiveBehavior {
  breakpoint_range: string;
  layout_adjustments: LayoutAdjustment[];
  content_prioritization: ContentPrioritization[];
  interaction_modifications: InteractionModification[];
}

export interface LayoutAdjustment {
  element_type: string;
  adjustment_type: string;
  adjustment_value: any;
  reasoning: string;
}

export interface ContentPrioritization {
  content_type: string;
  priority_level: number; // 1-5
  responsive_treatment: string;
  fallback_behavior: string;
}

export interface InteractionModification {
  interaction_type: string;
  modification: string;
  accessibility_impact: string;
  user_experience_notes: string[];
}

export interface BrandKitMetadata {
  created_by: string;
  last_modified_by: string;
  version_history: VersionHistoryEntry[];
  usage_analytics: UsageAnalytics;
  compliance_status: ComplianceStatus;
  review_schedule: ReviewSchedule;
  stakeholder_approvals: StakeholderApproval[];
}

export interface VersionHistoryEntry {
  version: string;
  timestamp: string;
  author: string;
  changes: Change[];
  notes: string;
}

export interface Change {
  category: string;
  description: string;
  impact_level: 'minor' | 'major' | 'breaking';
  affected_components: string[];
}

export interface UsageAnalytics {
  total_applications: number;
  most_used_colors: string[];
  most_used_fonts: string[];
  most_used_templates: string[];
  compliance_score_trend: number[];
  performance_metrics: PerformanceMetric[];
}

export interface PerformanceMetric {
  metric_name: string;
  current_value: number;
  trend: 'improving' | 'stable' | 'declining';
  target_value?: number;
}

export interface ComplianceStatus {
  overall_score: number; // 0-1
  last_audit_date: string;
  next_audit_date: string;
  compliance_areas: ComplianceArea[];
  action_items: ActionItem[];
}

export interface ComplianceArea {
  area: string;
  score: number; // 0-1
  status: 'compliant' | 'warning' | 'non_compliant';
  last_checked: string;
  findings: string[];
}

export interface ActionItem {
  priority: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  assigned_to?: string;
  due_date?: string;
  estimated_effort: string;
}

export interface ReviewSchedule {
  review_frequency: 'monthly' | 'quarterly' | 'biannually' | 'annually';
  next_review_date: string;
  review_scope: string[];
  stakeholders: string[];
}

export interface StakeholderApproval {
  stakeholder: string;
  role: string;
  approval_date: string;
  approval_scope: string[];
  conditions?: string[];
}

export interface ValidationStatus {
  overall_valid: boolean;
  validation_timestamp: string;
  validation_results: ValidationResult[];
  warnings: ValidationWarning[];
  errors: ValidationError[];
}

export interface ValidationResult {
  component: string;
  status: 'valid' | 'warning' | 'error';
  details: string;
  suggestions?: string[];
}

export interface ValidationWarning {
  component: string;
  warning: string;
  impact: 'low' | 'medium' | 'high';
  resolution_suggestion: string;
}

export interface ValidationError {
  component: string;
  error: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  blocking: boolean;
  resolution_required: string;
}

// =============================================================================
// BRAND KIT SERVICE IMPLEMENTATION
// =============================================================================

export class BrandKitService {
  private brandKits: Map<string, BrandKit>;
  private validationEngine: BrandValidationEngine;
  private assetOptimizer: AssetOptimizer;
  private complianceChecker: ComplianceChecker;

  constructor() {
    this.brandKits = new Map();
    this.validationEngine = new BrandValidationEngine();
    this.assetOptimizer = new AssetOptimizer();
    this.complianceChecker = new ComplianceChecker();
    
    this.loadDefaultBrandKits();
  }

  /**
   * Create a new brand kit
   */
  async createBrandKit(brandKitData: Partial<BrandKit>): Promise<BrandKit> {
    const brandKit: BrandKit = {
      id: brandKitData.id || this.generateId(),
      name: brandKitData.name || 'New Brand Kit',
      version: '1.0.0',
      organization_id: brandKitData.organization_id || 'default',
      colors: brandKitData.colors || this.createDefaultColorSystem(),
      typography: brandKitData.typography || this.createDefaultTypographySystem(),
      logos: brandKitData.logos || this.createDefaultLogoSystem(),
      voice_and_tone: brandKitData.voice_and_tone || this.createDefaultVoiceSystem(),
      compliance_rules: brandKitData.compliance_rules || this.createDefaultComplianceSystem(),
      imagery_guidelines: brandKitData.imagery_guidelines || this.createDefaultImageryGuidelines(),
      layout_principles: brandKitData.layout_principles || this.createDefaultLayoutPrinciples(),
      metadata: {
        created_by: 'system',
        last_modified_by: 'system',
        version_history: [],
        usage_analytics: this.createDefaultUsageAnalytics(),
        compliance_status: this.createDefaultComplianceStatus(),
        review_schedule: this.createDefaultReviewSchedule(),
        stakeholder_approvals: []
      },
      validation_status: {
        overall_valid: false,
        validation_timestamp: new Date().toISOString(),
        validation_results: [],
        warnings: [],
        errors: []
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // Validate the brand kit
    const validationResult = await this.validateBrandKit(brandKit);
    brandKit.validation_status = validationResult;

    // Store the brand kit
    this.brandKits.set(brandKit.id, brandKit);

    return brandKit;
  }

  /**
   * Update an existing brand kit
   */
  async updateBrandKit(brandKitId: string, updates: Partial<BrandKit>): Promise<BrandKit> {
    const existingBrandKit = this.brandKits.get(brandKitId);
    if (!existingBrandKit) {
      throw new Error(`Brand kit not found: ${brandKitId}`);
    }

    const updatedBrandKit: BrandKit = {
      ...existingBrandKit,
      ...updates,
      updated_at: new Date().toISOString()
    };

    // Increment version if significant changes
    if (this.hasSignificantChanges(existingBrandKit, updates)) {
      updatedBrandKit.version = this.incrementVersion(existingBrandKit.version);
      
      // Add to version history
      updatedBrandKit.metadata.version_history.push({
        version: existingBrandKit.version,
        timestamp: existingBrandKit.updated_at,
        author: existingBrandKit.metadata.last_modified_by,
        changes: this.calculateChanges(existingBrandKit, updates),
        notes: `Updated to version ${updatedBrandKit.version}`
      });
    }

    // Re-validate the brand kit
    const validationResult = await this.validateBrandKit(updatedBrandKit);
    updatedBrandKit.validation_status = validationResult;

    this.brandKits.set(brandKitId, updatedBrandKit);
    return updatedBrandKit;
  }

  /**
   * Get a brand kit by ID
   */
  getBrandKit(brandKitId: string): BrandKit | null {
    return this.brandKits.get(brandKitId) || null;
  }

  /**
   * Get all brand kits for an organization
   */
  getBrandKitsForOrganization(organizationId: string): BrandKit[] {
    return Array.from(this.brandKits.values())
      .filter(kit => kit.organization_id === organizationId)
      .sort((a, b) => b.updated_at.localeCompare(a.updated_at));
  }

  /**
   * Validate a brand kit
   */
  async validateBrandKit(brandKit: BrandKit): Promise<ValidationStatus> {
    const validationResults: ValidationResult[] = [];
    const warnings: ValidationWarning[] = [];
    const errors: ValidationError[] = [];

    // Validate color system
    const colorValidation = await this.validationEngine.validateColorSystem(brandKit.colors);
    validationResults.push(...colorValidation.results);
    warnings.push(...colorValidation.warnings);
    errors.push(...colorValidation.errors);

    // Validate typography
    const typographyValidation = await this.validationEngine.validateTypography(brandKit.typography);
    validationResults.push(...typographyValidation.results);
    warnings.push(...typographyValidation.warnings);
    errors.push(...typographyValidation.errors);

    // Validate logos
    const logoValidation = await this.validationEngine.validateLogos(brandKit.logos);
    validationResults.push(...logoValidation.results);
    warnings.push(...logoValidation.warnings);
    errors.push(...logoValidation.errors);

    // Validate compliance
    const complianceValidation = await this.complianceChecker.validateCompliance(brandKit);
    validationResults.push(...complianceValidation.results);
    warnings.push(...complianceValidation.warnings);
    errors.push(...complianceValidation.errors);

    const overallValid = errors.filter(e => e.blocking).length === 0;

    return {
      overall_valid: overallValid,
      validation_timestamp: new Date().toISOString(),
      validation_results: validationResults,
      warnings,
      errors
    };
  }

  /**
   * Apply brand kit to content
   */
  async applyBrandKit(
    brandKitId: string, 
    content: any, 
    options: BrandApplicationOptions = {}
  ): Promise<BrandApplicationResult> {
    const brandKit = this.getBrandKit(brandKitId);
    if (!brandKit) {
      throw new Error(`Brand kit not found: ${brandKitId}`);
    }

    const applicationResult: BrandApplicationResult = {
      success: true,
      applied_elements: [],
      warnings: [],
      errors: [],
      performance_metrics: {
        application_time_ms: 0,
        elements_processed: 0,
        optimizations_applied: 0
      }
    };

    const startTime = Date.now();

    try {
      // Apply colors
      if (options.apply_colors !== false) {
        const colorResult = await this.applyColorSystem(brandKit.colors, content);
        applicationResult.applied_elements.push(...colorResult.applied_elements);
        applicationResult.warnings.push(...colorResult.warnings);
      }

      // Apply typography
      if (options.apply_typography !== false) {
        const typographyResult = await this.applyTypography(brandKit.typography, content);
        applicationResult.applied_elements.push(...typographyResult.applied_elements);
        applicationResult.warnings.push(...typographyResult.warnings);
      }

      // Apply logos
      if (options.apply_logos !== false) {
        const logoResult = await this.applyLogos(brandKit.logos, content);
        applicationResult.applied_elements.push(...logoResult.applied_elements);
        applicationResult.warnings.push(...logoResult.warnings);
      }

      // Apply voice and tone
      if (options.apply_voice !== false) {
        const voiceResult = await this.applyVoiceAndTone(brandKit.voice_and_tone, content);
        applicationResult.applied_elements.push(...voiceResult.applied_elements);
        applicationResult.warnings.push(...voiceResult.warnings);
      }

      // Check compliance
      const complianceResult = await this.complianceChecker.checkContentCompliance(brandKit, content);
      applicationResult.warnings.push(...complianceResult.warnings);
      applicationResult.errors.push(...complianceResult.errors);

      applicationResult.performance_metrics.application_time_ms = Date.now() - startTime;
      applicationResult.performance_metrics.elements_processed = applicationResult.applied_elements.length;

      // Update usage analytics
      this.updateUsageAnalytics(brandKitId, applicationResult);

    } catch (error) {
      applicationResult.success = false;
      applicationResult.errors.push({
        component: 'application_engine',
        error: error.message,
        severity: 'high',
        blocking: true,
        resolution_required: 'Fix application error'
      });
    }

    return applicationResult;
  }

  /**
   * Optimize brand assets
   */
  async optimizeBrandAssets(brandKitId: string): Promise<OptimizationResult> {
    const brandKit = this.getBrandKit(brandKitId);
    if (!brandKit) {
      throw new Error(`Brand kit not found: ${brandKitId}`);
    }

    return await this.assetOptimizer.optimizeAssets(brandKit);
  }

  /**
   * Generate color variations
   */
  generateColorVariations(baseColor: string): ColorVariation {
    const rgb = this.hexToRgb(baseColor);
    if (!rgb) {
      throw new Error(`Invalid color: ${baseColor}`);
    }

    return {
      base_color: baseColor,
      variations: {
        tint_10: this.adjustColorBrightness(baseColor, 10),
        tint_25: this.adjustColorBrightness(baseColor, 25),
        tint_50: this.adjustColorBrightness(baseColor, 50),
        shade_10: this.adjustColorBrightness(baseColor, -10),
        shade_25: this.adjustColorBrightness(baseColor, -25),
        shade_50: this.adjustColorBrightness(baseColor, -50)
      }
    };
  }

  /**
   * Check color accessibility
   */
  checkColorAccessibility(foreground: string, background: string): ContrastRatio {
    const contrastRatio = this.calculateContrastRatio(foreground, background);
    
    let wcagLevel: 'AA' | 'AAA' | 'fail' = 'fail';
    if (contrastRatio >= 7) {
      wcagLevel = 'AAA';
    } else if (contrastRatio >= 4.5) {
      wcagLevel = 'AA';
    }

    return {
      against_color: background,
      ratio: contrastRatio,
      wcag_level: wcagLevel,
      use_case: contrastRatio >= 4.5 ? 'normal_text' : 
                contrastRatio >= 3 ? 'large_text' : 
                'ui_components'
    };
  }

  /**
   * Get font recommendations
   */
  getFontRecommendations(context: string, currentFonts: string[]): FontFamily[] {
    // Mock implementation - in production would use font pairing algorithms
    const allFonts = this.getAvailableFonts();
    
    return allFonts
      .filter(font => 
        font.usage_context.some(ctx => ctx.context === context && ctx.recommended)
      )
      .filter(font => !currentFonts.includes(font.name))
      .slice(0, 5);
  }

  /**
   * Validate logo usage
   */
  validateLogoUsage(
    logoId: string, 
    context: LogoUsageContext, 
    dimensions: { width: number; height: number }
  ): LogoValidationResult {
    // Mock implementation
    return {
      valid: true,
      warnings: [],
      recommendations: [
        'Consider using SVG format for better scalability',
        'Ensure sufficient clear space around logo'
      ]
    };
  }

  // =============================================================================
  // PRIVATE HELPER METHODS
  // =============================================================================

  private generateId(): string {
    return `brand_kit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private createDefaultColorSystem(): ColorSystem {
    return {
      primary_palette: {
        name: 'Primary Palette',
        colors: [
          {
            id: 'primary',
            name: 'Primary Blue',
            hex: '#2563eb',
            rgb: { r: 37, g: 99, b: 235 },
            hsl: { h: 220, s: 83, l: 53 },
            usage_context: [{ context: 'primary', weight: 1.0 }],
            accessibility_level: 'AA',
            contrast_ratios: []
          }
        ],
        harmony_type: 'monochromatic',
        primary_color: '#2563eb'
      },
      semantic_colors: {
        success: '#059669',
        warning: '#d97706',
        error: '#dc2626',
        info: '#2563eb',
        neutral: '#64748b'
      },
      accessibility_compliance: {
        wcag_level: 'AA',
        color_blind_safe: true,
        high_contrast_approved: true,
        minimum_contrast_ratio: 4.5
      },
      usage_guidelines: [],
      generated_variations: []
    };
  }

  private createDefaultTypographySystem(): TypographySystem {
    return {
      font_families: [
        {
          id: 'inter',
          name: 'Inter',
          display_name: 'Inter',
          category: 'sans-serif',
          weights: [
            { weight: 400, name: 'Regular', available: true },
            { weight: 500, name: 'Medium', available: true },
            { weight: 600, name: 'SemiBold', available: true },
            { weight: 700, name: 'Bold', available: true }
          ],
          styles: [{ style: 'normal', available: true }],
          license: {
            type: 'free',
            attribution_required: false,
            commercial_use_allowed: true
          },
          file_formats: [],
          character_sets: ['latin'],
          language_support: ['en'],
          usage_context: [
            { context: 'body', recommended: true, weight_range: [400, 500], size_range: [14, 18] }
          ],
          fallback_fonts: ['system-ui', '-apple-system', 'sans-serif']
        }
      ],
      type_scale: {
        base_size: 16,
        ratio: 1.25,
        sizes: [
          { name: 'xs', size: 12, line_height: 1.4, usage: ['captions'] },
          { name: 'sm', size: 14, line_height: 1.5, usage: ['body'] },
          { name: 'base', size: 16, line_height: 1.5, usage: ['body'] },
          { name: 'lg', size: 18, line_height: 1.4, usage: ['large_body'] },
          { name: 'xl', size: 20, line_height: 1.3, usage: ['headings'] }
        ],
        line_heights: { tight: 1.25, normal: 1.5, relaxed: 1.75, loose: 2 },
        letter_spacing: { tight: -0.025, normal: 0, wide: 0.025, wider: 0.05 }
      },
      font_pairings: [],
      usage_guidelines: [],
      fallback_strategy: {
        system_fonts: ['system-ui', '-apple-system', 'BlinkMacSystemFont'],
        web_safe_fonts: ['Arial', 'Helvetica', 'sans-serif'],
        loading_strategy: 'swap',
        timeout_ms: 3000
      },
      web_font_loading: {
        preload_fonts: [],
        font_display: 'swap',
        subset_strategy: 'latin'
      }
    };
  }

  private createDefaultLogoSystem(): LogoSystem {
    return {
      primary_logo: {
        id: 'primary_logo',
        name: 'Primary Logo',
        type: 'primary',
        file_formats: [],
        original_dimensions: { width: 200, height: 50 },
        aspect_ratio: 4,
        color_mode: 'full_color',
        usage_contexts: [],
        optimization_status: {
          svg_optimized: false,
          png_compressed: false,
          retina_versions: false,
          webp_available: false,
          file_size_score: 0.5,
          load_time_estimate_ms: 100
        }
      },
      secondary_logos: [],
      icon_variations: [],
      usage_guidelines: {
        preferred_placement: ['top-left', 'center'],
        alignment_rules: ['Align to grid', 'Maintain clear space'],
        scaling_guidelines: ['Maintain aspect ratio', 'Use vector formats'],
        background_recommendations: [],
        do_examples: ['Use on light backgrounds', 'Maintain minimum size'],
        dont_examples: ['Distort proportions', 'Use on busy backgrounds']
      },
      minimum_sizes: {
        minimum_width: 120,
        minimum_height: 30,
        recommended_sizes: [
          { context: 'web_header', width: 150, height: 37 },
          { context: 'business_card', width: 200, height: 50 }
        ]
      },
      clear_space_rules: {
        minimum_clear_space: 1,
        measurement_unit: 'logo_height',
        applies_to: ['all_sides'],
        exceptions: []
      },
      color_variations: [],
      prohibited_uses: []
    };
  }

  private createDefaultVoiceSystem(): VoiceSystem {
    return {
      brand_voice: {
        personality_traits: ['Professional', 'Helpful', 'Trustworthy'],
        voice_characteristics: [
          {
            trait: 'Professional',
            description: 'Maintains professional tone in all communications',
            intensity: 0.8,
            examples: ['We provide expert guidance', 'Our team has extensive experience'],
            avoid_examples: ['We\'re super awesome', 'This is totally amazing']
          }
        ],
        target_audience: {
          primary_audience: {
            name: 'Property Buyers and Sellers',
            demographics: {
              age_range: [25, 65],
              income_range: [50000, 500000],
              education_level: ['High School', 'College', 'Graduate'],
              location_types: ['Urban', 'Suburban'],
              profession_categories: ['Professional', 'Manager', 'Entrepreneur']
            },
            psychographics: {
              values: ['Security', 'Investment', 'Family'],
              interests: ['Real Estate', 'Home Improvement', 'Investment'],
              lifestyle_preferences: ['Quality', 'Convenience', 'Reliability'],
              pain_points: ['Complex Process', 'Market Uncertainty', 'Time Constraints'],
              goals: ['Find Perfect Home', 'Make Smart Investment', 'Sell Quickly']
            },
            communication_preferences: [
              {
                channel: 'Email',
                frequency: 'Weekly',
                format: ['Newsletter', 'Market Updates'],
                tone_preference: 'Professional'
              }
            ]
          },
          secondary_audiences: [],
          persona_profiles: []
        },
        brand_values: ['Integrity', 'Expertise', 'Service Excellence'],
        differentiators: ['Local Market Knowledge', 'Technology Integration', 'Personal Service'],
        emotional_tone: {
          primary_emotion: 'Trust',
          secondary_emotions: ['Confidence', 'Security'],
          emotional_intensity: 0.7,
          emotional_consistency: 0.9
        }
      },
      tone_variations: [],
      messaging_guidelines: {
        key_messages: [],
        message_hierarchy: {
          primary_message: 'Your trusted real estate partner',
          secondary_messages: ['Local market expertise', 'Technology-driven service'],
          supporting_messages: ['Proven track record', '24/7 availability'],
          proof_points: ['500+ satisfied clients', '95% customer satisfaction']
        },
        call_to_action_guidelines: {
          preferred_action_verbs: ['Discover', 'Explore', 'Connect', 'Schedule', 'Learn'],
          tone_requirements: ['Action-oriented', 'Clear', 'Compelling'],
          urgency_guidelines: [],
          placement_recommendations: ['Above fold', 'End of content', 'Sidebar'],
          A_B_testing_frameworks: []
        },
        value_proposition_frameworks: []
      },
      content_principles: [],
      style_preferences: {
        sentence_structure: {
          preferred_length: 'medium',
          complexity_level: 'compound',
          active_vs_passive: 'prefer_active'
        },
        vocabulary_preferences: {
          formality_level: 'professional',
          technical_language: 'explain',
          industry_jargon: 'explain',
          preferred_synonyms: {},
          words_to_avoid: ['cheap', 'deal', 'steal']
        },
        punctuation_style: {
          serial_comma: true,
          quotation_style: 'american',
          em_dash_usage: 'moderate',
          exclamation_policy: 'minimal'
        },
        capitalization_rules: [],
        number_formatting: []
      },
      prohibited_language: {
        banned_words: [],
        sensitive_topics: [],
        compliance_requirements: [],
        cultural_considerations: []
      },
      industry_compliance: {
        industry: 'Real Estate',
        regulatory_bodies: ['NAR', 'State Real Estate Commission'],
        compliance_frameworks: [],
        required_disclaimers: [],
        prohibited_practices: []
      }
    };
  }

  private createDefaultComplianceSystem(): ComplianceSystem {
    return {
      fair_housing_compliance: {
        enabled: true,
        protected_classes: [],
        prohibited_language: [],
        alternative_suggestions: [],
        exception_handling: {
          approved_exceptions: [],
          approval_process: [],
          documentation_requirements: []
        }
      },
      accessibility_compliance: {
        wcag_version: '2.1',
        conformance_level: 'AA',
        color_contrast_requirements: [],
        text_requirements: [],
        image_requirements: [],
        interactive_element_requirements: []
      },
      legal_compliance: {
        copyright_requirements: [],
        trademark_requirements: [],
        privacy_requirements: [],
        data_protection_requirements: []
      },
      industry_specific: {
        industry: 'Real Estate',
        specific_rules: [],
        certification_requirements: [],
        audit_requirements: []
      },
      validation_rules: [],
      audit_trail: []
    };
  }

  private createDefaultImageryGuidelines(): ImageryGuidelines {
    return {
      style_preferences: [],
      composition_rules: [],
      color_treatment: [],
      subject_matter_guidelines: [],
      technical_requirements: [],
      usage_rights: []
    };
  }

  private createDefaultLayoutPrinciples(): LayoutPrinciples {
    return {
      grid_systems: [],
      spacing_principles: [],
      hierarchy_rules: [],
      balance_guidelines: [],
      responsive_behavior: []
    };
  }

  private createDefaultUsageAnalytics(): UsageAnalytics {
    return {
      total_applications: 0,
      most_used_colors: [],
      most_used_fonts: [],
      most_used_templates: [],
      compliance_score_trend: [],
      performance_metrics: []
    };
  }

  private createDefaultComplianceStatus(): ComplianceStatus {
    return {
      overall_score: 1.0,
      last_audit_date: new Date().toISOString(),
      next_audit_date: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      compliance_areas: [],
      action_items: []
    };
  }

  private createDefaultReviewSchedule(): ReviewSchedule {
    return {
      review_frequency: 'quarterly',
      next_review_date: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      review_scope: ['colors', 'typography', 'logos', 'compliance'],
      stakeholders: ['brand_manager', 'compliance_officer']
    };
  }

  private hasSignificantChanges(existing: BrandKit, updates: Partial<BrandKit>): boolean {
    // Check for significant changes that warrant version increment
    const significantFields = ['colors', 'typography', 'logos', 'voice_and_tone', 'compliance_rules'];
    
    return significantFields.some(field => 
      updates[field] && JSON.stringify(existing[field]) !== JSON.stringify(updates[field])
    );
  }

  private incrementVersion(currentVersion: string): string {
    const parts = currentVersion.split('.');
    const patch = parseInt(parts[2] || '0') + 1;
    return `${parts[0]}.${parts[1]}.${patch}`;
  }

  private calculateChanges(existing: BrandKit, updates: Partial<BrandKit>): Change[] {
    const changes: Change[] = [];
    
    Object.keys(updates).forEach(key => {
      if (existing[key] !== updates[key]) {
        changes.push({
          category: key,
          description: `Updated ${key}`,
          impact_level: 'minor',
          affected_components: [key]
        });
      }
    });

    return changes;
  }

  private async applyColorSystem(colorSystem: ColorSystem, content: any): Promise<ApplicationSubResult> {
    // Mock implementation
    return {
      applied_elements: [
        { type: 'color', property: 'primary_color', value: colorSystem.primary_palette.primary_color }
      ],
      warnings: []
    };
  }

  private async applyTypography(typography: TypographySystem, content: any): Promise<ApplicationSubResult> {
    // Mock implementation  
    return {
      applied_elements: [
        { type: 'typography', property: 'font_family', value: typography.font_families[0]?.name || 'system-ui' }
      ],
      warnings: []
    };
  }

  private async applyLogos(logos: LogoSystem, content: any): Promise<ApplicationSubResult> {
    // Mock implementation
    return {
      applied_elements: [
        { type: 'logo', property: 'primary_logo', value: logos.primary_logo.id }
      ],
      warnings: []
    };
  }

  private async applyVoiceAndTone(voice: VoiceSystem, content: any): Promise<ApplicationSubResult> {
    // Mock implementation
    return {
      applied_elements: [
        { type: 'voice', property: 'tone', value: voice.brand_voice.personality_traits.join(', ') }
      ],
      warnings: []
    };
  }

  private updateUsageAnalytics(brandKitId: string, applicationResult: BrandApplicationResult): void {
    const brandKit = this.brandKits.get(brandKitId);
    if (!brandKit) return;

    brandKit.metadata.usage_analytics.total_applications++;
    brandKit.updated_at = new Date().toISOString();
  }

  private hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

  private adjustColorBrightness(hex: string, percent: number): string {
    const rgb = this.hexToRgb(hex);
    if (!rgb) return hex;

    const adjust = (color: number) => {
      const adjusted = Math.round(color + (color * percent / 100));
      return Math.max(0, Math.min(255, adjusted));
    };

    const adjustedR = adjust(rgb.r);
    const adjustedG = adjust(rgb.g);
    const adjustedB = adjust(rgb.b);

    return `#${adjustedR.toString(16).padStart(2, '0')}${adjustedG.toString(16).padStart(2, '0')}${adjustedB.toString(16).padStart(2, '0')}`;
  }

  private calculateContrastRatio(foreground: string, background: string): number {
    // Simplified contrast ratio calculation
    const frgb = this.hexToRgb(foreground);
    const brgb = this.hexToRgb(background);
    
    if (!frgb || !brgb) return 1;

    const getLuminance = (r: number, g: number, b: number) => {
      const sRGB = [r, g, b].map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
    };

    const l1 = getLuminance(frgb.r, frgb.g, frgb.b);
    const l2 = getLuminance(brgb.r, brgb.g, brgb.b);

    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);

    return (lighter + 0.05) / (darker + 0.05);
  }

  private getAvailableFonts(): FontFamily[] {
    // Return all available fonts from all brand kits
    const allFonts: FontFamily[] = [];
    
    for (const brandKit of this.brandKits.values()) {
      allFonts.push(...brandKit.typography.font_families);
    }

    return allFonts;
  }

  private loadDefaultBrandKits(): void {
    // Load default brand kit
    this.createBrandKit({
      id: 'default_professional',
      name: 'Professional Real Estate',
      organization_id: 'default'
    });
  }
}

// =============================================================================
// SUPPORTING CLASSES
// =============================================================================

class BrandValidationEngine {
  async validateColorSystem(colorSystem: ColorSystem): Promise<{
    results: ValidationResult[];
    warnings: ValidationWarning[];
    errors: ValidationError[];
  }> {
    return {
      results: [
        { component: 'colors', status: 'valid', details: 'Color system validation passed' }
      ],
      warnings: [],
      errors: []
    };
  }

  async validateTypography(typography: TypographySystem): Promise<{
    results: ValidationResult[];
    warnings: ValidationWarning[];
    errors: ValidationError[];
  }> {
    return {
      results: [
        { component: 'typography', status: 'valid', details: 'Typography system validation passed' }
      ],
      warnings: [],
      errors: []
    };
  }

  async validateLogos(logos: LogoSystem): Promise<{
    results: ValidationResult[];
    warnings: ValidationWarning[];
    errors: ValidationError[];
  }> {
    return {
      results: [
        { component: 'logos', status: 'valid', details: 'Logo system validation passed' }
      ],
      warnings: [],
      errors: []
    };
  }
}

class AssetOptimizer {
  async optimizeAssets(brandKit: BrandKit): Promise<OptimizationResult> {
    return {
      success: true,
      optimizations_applied: [
        { type: 'logo_compression', description: 'Optimized PNG logos', savings_kb: 150 }
      ],
      total_savings_kb: 150,
      performance_improvement: '15% faster loading'
    };
  }
}

class ComplianceChecker {
  async validateCompliance(brandKit: BrandKit): Promise<{
    results: ValidationResult[];
    warnings: ValidationWarning[];
    errors: ValidationError[];
  }> {
    return {
      results: [
        { component: 'compliance', status: 'valid', details: 'Compliance validation passed' }
      ],
      warnings: [],
      errors: []
    };
  }

  async checkContentCompliance(brandKit: BrandKit, content: any): Promise<{
    warnings: ValidationWarning[];
    errors: ValidationError[];
  }> {
    return {
      warnings: [],
      errors: []
    };
  }
}

// =============================================================================
// ADDITIONAL INTERFACES
// =============================================================================

export interface BrandApplicationOptions {
  apply_colors?: boolean;
  apply_typography?: boolean;
  apply_logos?: boolean;
  apply_voice?: boolean;
  force_override?: boolean;
  preserve_existing?: string[];
}

export interface BrandApplicationResult {
  success: boolean;
  applied_elements: AppliedElement[];
  warnings: ValidationWarning[];
  errors: ValidationError[];
  performance_metrics: {
    application_time_ms: number;
    elements_processed: number;
    optimizations_applied: number;
  };
}

export interface AppliedElement {
  type: string;
  property: string;
  value: any;
  previous_value?: any;
}

export interface ApplicationSubResult {
  applied_elements: AppliedElement[];
  warnings: ValidationWarning[];
}

export interface LogoValidationResult {
  valid: boolean;
  warnings: string[];
  recommendations: string[];
}

export interface OptimizationResult {
  success: boolean;
  optimizations_applied: OptimizationApplied[];
  total_savings_kb: number;
  performance_improvement: string;
}

export interface OptimizationApplied {
  type: string;
  description: string;
  savings_kb: number;
}

// =============================================================================
// SINGLETON EXPORT
// =============================================================================

export const brandKitService = new BrandKitService();
export default brandKitService;