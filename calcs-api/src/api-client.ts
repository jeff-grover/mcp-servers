import { 
  ApiResponse, 
  CalcsApiConfig, 
  Test, 
  TestStatusResponse, 
  SiteRole, 
  TestResult, 
  FilterType,
  LiftExplorationMeta,
  LiftExplorerResult,
  SitPairLift,
  PredictionTableMetric,
  CustomerCrossMetric,
  Analysis,
  AnalysisCreate,
  AnalysisUpdate,
  ClientResponse,
  JobsSummary,
  FileData,
  SiteUse,
  HealthCheck
} from './types.js';

export class CalcsApiClient {
  private config: CalcsApiConfig;

  constructor(config: CalcsApiConfig) {
    this.config = config;
  }

  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {},
    client?: string
  ): Promise<ApiResponse<T>> {
    const url = `${this.config.baseUrl}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Authorization': `Bearer ${this.config.bearerToken}`,
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>
    };

    // Add client header if specified or use default
    const clientHeader = client || this.config.defaultClient;
    if (clientHeader) {
      headers['client'] = clientHeader;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      const contentType = response.headers.get('content-type');
      let data: T;
      
      if (contentType?.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text() as unknown as T;
      }

      if (!response.ok) {
        return {
          error: `HTTP ${response.status}: ${response.statusText}`,
          status: response.status
        };
      }

      return {
        data,
        status: response.status
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        status: 0
      };
    }
  }

  // Test Management APIs
  async getTests(client?: string): Promise<ApiResponse<Test[]>> {
    return this.makeRequest<Test[]>('/v1/tests/', {}, client);
  }

  async getTestStatus(testId: number, client?: string): Promise<ApiResponse<TestStatusResponse>> {
    return this.makeRequest<TestStatusResponse>(`/v1/tests/${testId}/status`, {}, client);
  }

  async getTestSites(testId: string, client?: string): Promise<ApiResponse<SiteRole[]>> {
    return this.makeRequest<SiteRole[]>(`/v1/tests/${testId}/sites`, {}, client);
  }

  async getCohortId(
    testId: number, 
    implStartDate: string, 
    testStartDate: string, 
    blockoutsString: string = '',
    client?: string
  ): Promise<ApiResponse<string>> {
    const params = new URLSearchParams({
      impl_start_date: implStartDate,
      test_start_date: testStartDate,
      blockouts_string: blockoutsString
    });
    return this.makeRequest<string>(`/v1/tests/${testId}/cohort/id?${params}`, {}, client);
  }

  // Results APIs
  async getTestResults(
    testId: number, 
    filterType: FilterType, 
    filterValue?: number | string,
    client?: string
  ): Promise<ApiResponse<TestResult[]>> {
    const params = new URLSearchParams();
    if (filterValue !== undefined) {
      params.append('filter_value', filterValue.toString());
    }
    const queryString = params.toString() ? `?${params}` : '';
    return this.makeRequest<TestResult[]>(`/v1/results/test/${testId}/${filterType}${queryString}`, {}, client);
  }

  async getLiftExplorerResults(liftExplorerId: string, client?: string): Promise<ApiResponse<LiftExplorerResult[]>> {
    return this.makeRequest<LiftExplorerResult[]>(`/v1/results/lift-explorer/${liftExplorerId}`, {}, client);
  }

  async getSitePairLiftManifest(testId: number, client?: string): Promise<ApiResponse<SitPairLift[]>> {
    return this.makeRequest<SitPairLift[]>(`/v1/results/test/${testId}/site-pair-lift-manifest`, {}, client);
  }

  async getPredictionTable(testId: number, client?: string): Promise<ApiResponse<PredictionTableMetric[]>> {
    return this.makeRequest<PredictionTableMetric[]>(`/v1/results/test/${testId}/prediction-table`, {}, client);
  }

  async getCustomerCross(testId: number, client?: string): Promise<ApiResponse<CustomerCrossMetric[]>> {
    return this.makeRequest<CustomerCrossMetric[]>(`/v1/results/test/${testId}/customer-cross`, {}, client);
  }

  async downloadAllTestData(testId: number, client?: string): Promise<ApiResponse<any>> {
    return this.makeRequest<any>(`/v1/results/test-download-all/${testId}`, {}, client);
  }

  // Lift Explorations APIs
  async getLiftExplorationIds(client?: string): Promise<ApiResponse<LiftExplorationMeta[]>> {
    return this.makeRequest<LiftExplorationMeta[]>('/v1/lift_explorations/', {}, client);
  }

  // Analysis APIs (Rollout)
  async getAnalyses(client?: string): Promise<ApiResponse<Analysis[]>> {
    return this.makeRequest<Analysis[]>('/v1/rollout/analyses', {}, client);
  }

  async getAnalysis(analysisId: string, client?: string): Promise<ApiResponse<Analysis>> {
    return this.makeRequest<Analysis>(`/v1/rollout/analyses/${analysisId}`, {}, client);
  }

  async createAnalysis(analysis: AnalysisCreate, client?: string): Promise<ApiResponse<Analysis>> {
    return this.makeRequest<Analysis>('/v1/rollout/analyses', {
      method: 'POST',
      body: JSON.stringify(analysis)
    }, client);
  }

  async updateAnalysis(analysisId: string, analysis: AnalysisUpdate, client?: string): Promise<ApiResponse<Analysis>> {
    return this.makeRequest<Analysis>(`/v1/rollout/analyses/${analysisId}`, {
      method: 'PUT',
      body: JSON.stringify(analysis)
    }, client);
  }

  async deleteAnalysis(analysisId: string, client?: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/v1/rollout/analyses/${analysisId}`, {
      method: 'DELETE'
    }, client);
  }

  async runAnalysis(analysisId: string, forceRefresh: boolean = false, client?: string): Promise<ApiResponse<object>> {
    const params = new URLSearchParams();
    if (forceRefresh) {
      params.append('force_refresh', 'true');
    }
    const queryString = params.toString() ? `?${params}` : '';
    return this.makeRequest<object>(`/v1/rollout/analyses/${analysisId}/run${queryString}`, {
      method: 'POST'
    }, client);
  }

  async startAnalysis(analysisId: string, forceRefresh: boolean = false, client?: string): Promise<ApiResponse<object>> {
    const params = new URLSearchParams();
    if (forceRefresh) {
      params.append('force_refresh', 'true');
    }
    const queryString = params.toString() ? `?${params}` : '';
    return this.makeRequest<object>(`/v1/rollout/analyses/${analysisId}/start${queryString}`, {
      method: 'POST'
    }, client);
  }

  async getAnalysisResults(analysisId: string, client?: string): Promise<ApiResponse<object>> {
    return this.makeRequest<object>(`/v1/rollout/analyses/${analysisId}/results`, {}, client);
  }

  // Administrative APIs
  async getActiveClients(client?: string): Promise<ApiResponse<ClientResponse[]>> {
    return this.makeRequest<ClientResponse[]>('/v1/clients/', {}, client);
  }

  async getJobsSummary(startDate: string, endDate: string, client?: string): Promise<ApiResponse<JobsSummary>> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate
    });
    return this.makeRequest<JobsSummary>(`/v1/jobs/summary?${params}`, {}, client);
  }

  async getOldestJobDate(client?: string): Promise<ApiResponse<string>> {
    return this.makeRequest<string>('/v1/jobs/oldest-job-date', {}, client);
  }

  async getNewestJobDate(client?: string): Promise<ApiResponse<string>> {
    return this.makeRequest<string>('/v1/jobs/newest-job-date', {}, client);
  }

  async getAllClientsJobsSummary(startDate: string, endDate: string, client?: string): Promise<ApiResponse<Record<string, JobsSummary>>> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate
    });
    return this.makeRequest<Record<string, JobsSummary>>(`/v1/clients/jobs-summary?${params}`, {}, client);
  }

  // Site APIs
  async getSiteTests(clientSiteId: string, client?: string): Promise<ApiResponse<SiteUse[]>> {
    return this.makeRequest<SiteUse[]>(`/v1/sites/${clientSiteId}/tests`, {}, client);
  }

  // Adhoc Data APIs
  async listAdhocFiles(client?: string): Promise<ApiResponse<FileData[]>> {
    return this.makeRequest<FileData[]>('/v1/adhoc/upload/list', {}, client);
  }

  async getColumnNames(fileName: string, client?: string): Promise<ApiResponse<string[]>> {
    const params = new URLSearchParams({ file_name: fileName });
    return this.makeRequest<string[]>(`/v1/adhoc/upload/column?${params}`, {}, client);
  }

  async deleteAdhocFile(fileName: string, client?: string): Promise<ApiResponse<string>> {
    const params = new URLSearchParams({ file_name: fileName });
    return this.makeRequest<string>(`/v1/adhoc/upload?${params}`, {
      method: 'DELETE'
    }, client);
  }

  // Transaction APIs
  async describeTransactions(client?: string): Promise<ApiResponse<object>> {
    return this.makeRequest<object>('/v1/transactions/describe', {}, client);
  }

  // Health Check
  async healthCheck(): Promise<ApiResponse<HealthCheck>> {
    return this.makeRequest<HealthCheck>('/health');
  }

  // Ping endpoint for testing
  async ping(client?: string): Promise<ApiResponse<object>> {
    return this.makeRequest<object>('/v1/rollout/ping', {}, client);
  }
}