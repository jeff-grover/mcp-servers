// TypeScript types generated from Calcs API OpenAPI specification

export interface Test {
  id: number;
  test_name: string;
  test_description: string;
  calcs_status: CalcStatusEnum | null;
  calcs_started: string | null;
  calcs_ended: string | null;
  date_last_edited: string | null;
  parent_test_id: number | null;
  test_type: string;
  test_status: TestStatusEnum;
  week_count: number;
  pre_week_count: number;
}

export enum CalcStatusEnum {
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETE = "COMPLETE",
  FAILED = "FAILED"
}

export enum TestStatusEnum {
  INCOMPLETE = "INCOMPLETE",
  UNSCHEDULED = "UNSCHEDULED",
  SCHEDULED = "SCHEDULED",
  IN_IMPLEMENTATION = "IN_IMPLEMENTATION",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  ARCHIVED = "ARCHIVED"
}

export interface TestStatusResponse {
  test_status: TestStatusEnum;
}

export interface SiteRole {
  client_site_id: string;
  site_id: number;
  site_name: string;
  role: Role;
  latitude: number;
  longitude: number;
}

export enum Role {
  TREATMENT = "TREATMENT",
  CONTROL = "CONTROL"
}

export interface TestResult {
  uuid: number | null;
  out_treatment_value: OutTreatmentValue[];
  out_control_index_value: OutControlIndexValue[];
  out_scaled_control_value: OutScaledControlValue[];
  out_treatment_index_value: OutTreatmentIndexValue[];
  out_actual_control_value: OutActualControlValue[];
  out_lift_period: number[];
  out_lift: number[];
  out_confidence: number[];
  out_actual_control_mean: number | null;
  out_scaled_control_mean: number | null;
  pre_treatment_mean: number | null;
  out_control_pre_to_post_percent_change: number | null;
  pre_control_mean: number | null;
  out_treatment_pre_to_post_percent_change: number | null;
  out_numeric_lift: number | null;
  out_treatment_mean: number | null;
  is_direct: boolean | null;
  non_product_metrics_direct_unsafe: boolean | null;
  slices: Slices[];
  run_id: number | null;
}

export interface OutTreatmentValue {
  period: number | null;
  values: number[];
}

export interface OutControlIndexValue {
  period: number | null;
  values: number[];
}

export interface OutScaledControlValue {
  period: number | null;
  values: number[];
}

export interface OutTreatmentIndexValue {
  period: number | null;
  values: number[];
}

export interface OutActualControlValue {
  period: number | null;
  values: number[];
}

export interface Slices {
  slice_type: number | null;
  values: Values[];
}

export interface Values {
  slice_value: number | null;
  out_numeric_lift: number | null;
  out_lift: number | null;
  out_confidence: number | null;
}

export enum FilterType {
  OVERALL = "OVERALL",
  CUSTOMER_COHORT = "CUSTOMER_COHORT",
  CUSTOMER_SEGMENT = "CUSTOMER_SEGMENT",
  SITE_COHORT = "SITE_COHORT",
  SITE_PAIR = "SITE_PAIR",
  FINISHED_COHORT = "FINISHED_COHORT",
  SITE_TAG = "SITE_TAG"
}

export interface LiftExplorationMeta {
  id: number;
  test_id: number;
  name: string;
  created_by_user_id: number;
  calcs_status: CalcStatusEnum;
  calcs_start_date: string;
  calcs_end_date: string;
  is_calcs_weekly: boolean;
}

export interface LiftExplorerResult {
  uuid: number;
  out_treatment_value: LEOutTreatmentValue[];
  out_control_index_value: LEOutControlIndexValue[];
  out_scaled_control_value: LEOutScaledControlValue[];
  out_treatment_index_value: LEOutTreatmentIndexValue[];
  out_actual_control_value: LEOutActualControlValue[];
  out_lift_period: number[];
  out_lift: number[];
  out_confidence: number[];
  out_actual_control_mean: number;
  out_scaled_control_mean: number;
  pre_treatment_mean: number;
  out_control_pre_to_post_percent_change: number;
  pre_control_mean: number;
  out_treatment_pre_to_post_percent_change: number;
  out_numeric_lift: number;
  out_treatment_mean: number;
  out_numeric_lift_list: number[];
  product_view_id: string;
  group_by_type: GroupingItemType | null;
  group_by_id: number | null;
  filter_type: FilterType;
  filter_value: number | null;
  group_by_tags: GroupByTag[];
}

export interface LEOutTreatmentValue {
  period: number;
  values: number[];
}

export interface LEOutControlIndexValue {
  period: number;
  values: number[];
}

export interface LEOutScaledControlValue {
  period: number;
  values: number[];
}

export interface LEOutTreatmentIndexValue {
  period: number;
  values: number[];
}

export interface LEOutActualControlValue {
  period: number;
  values: number[];
}

export enum GroupingItemType {
  PRODUCT = "product",
  HIERARCHY = "hierarchy"
}

export interface GroupByTag {
  column: string;
  value: string;
}

export interface SitPairLift {
  is_direct: boolean;
  is_low_sales_outlier: boolean;
  pair_id: number;
  comparability: number;
  treatment_site_name: string;
  control_site_name: string;
  treatment_site_address: string;
  control_site_address: string;
  points: Point[];
}

export interface Point {
  metric_uuid: number;
  non_product_metrics_direct_unsafe: boolean;
  is_outlier: boolean;
  out_lift: number;
  out_numeric_lift: number;
  out_confidence: number;
}

export interface PredictionTableMetric {
  metric_uuid: number;
  best_rmse: number;
  explained_variation: number;
  sites: PredictionTableSite[];
}

export interface PredictionTableSite {
  site_id: number;
  site_name: string;
  predicted_lift: number;
  avg_yearly_dc: number;
  site_test_type: string;
  attributes: Record<string, string | number>;
}

export interface CustomerCrossMetric {
  is_direct: boolean;
  uuid: number;
  filter_value: number;
  slice_value: number;
  out_lift: number | null;
  out_numeric_lift: number | null;
  out_confidence: number;
  run_id: number;
}

export interface Analysis {
  name: string;
  description: string;
  measurementLength: number;
  startDate: string;
  hasImplementationPeriod: boolean;
  implementationLength: number | null;
  selectedProducts: object[];
  transactionAttributeFilter: object | null;
  includeTags: SimpleTag[];
  excludeTags: SimpleTag[];
  id: string;
  createdAt: string;
}

export interface AnalysisCreate {
  name: string;
  description: string;
  measurementLength: number;
  startDate: string;
  hasImplementationPeriod: boolean;
  implementationLength: number | null;
  selectedProducts: object[];
  transactionAttributeFilter: object | null;
  includeTags: SimpleTag[];
  excludeTags: SimpleTag[];
}

export interface AnalysisUpdate {
  name?: string | null;
  description?: string | null;
  measurementLength?: number | null;
  startDate?: string | null;
  hasImplementationPeriod?: boolean | null;
  implementationLength?: number | null;
  selectedProducts?: object[] | null;
  transactionAttributeFilter?: object | null;
  includeTags?: SimpleTag[] | null;
  excludeTags?: SimpleTag[] | null;
}

export interface SimpleTag {
  id: string;
  text: string;
}

export interface ClientResponse {
  client: string;
}

export interface JobsSummary {
  job_count: number;
  v_cpu_hours: number;
}

export interface FileData {
  name: string;
  size: number;
  last_modified: string;
}

export interface SiteUse {
  test_id: number;
  role: Role;
}

export interface HealthCheck {
  status: string;
  data?: string | null;
}

export interface HTTPValidationError {
  detail?: ValidationError[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

// API Request/Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface CalcsApiConfig {
  baseUrl: string;
  bearerToken: string;
  defaultClient: string;
}