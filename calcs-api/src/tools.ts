import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { CalcsApiClient } from './api-client.js';
import { FilterType } from './types.js';

// Zod schemas for validation
const TestIdSchema = z.object({
  test_id: z.number().describe('The ID of the test')
});

const TestIdStringSchema = z.object({
  test_id: z.string().describe('The ID of the test')
});

const ClientSchema = z.object({
  client: z.string().optional().describe('Client identifier (optional, uses default if not provided)')
});

const TestResultsSchema = z.object({
  test_id: z.number().describe('The ID of the test'),
  filter_type: z.nativeEnum(FilterType).describe('The type of filter to apply'),
  filter_value: z.union([z.number(), z.string()]).optional().describe('The filter value (optional)'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const LiftExplorerSchema = z.object({
  lift_explorer_id: z.string().describe('The ID of the lift explorer'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const AnalysisIdSchema = z.object({
  analysis_id: z.string().describe('The ID of the analysis'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const CreateAnalysisSchema = z.object({
  name: z.string().describe('Name of the analysis'),
  description: z.string().describe('Description of the analysis'),
  measurementLength: z.number().describe('Length of measurement period'),
  startDate: z.string().describe('Start date for the analysis'),
  hasImplementationPeriod: z.boolean().describe('Whether analysis has implementation period'),
  implementationLength: z.number().optional().describe('Length of implementation period'),
  selectedProducts: z.array(z.object({})).default([]).describe('Selected products for analysis'),
  transactionAttributeFilter: z.object({}).optional().describe('Transaction attribute filter'),
  includeTags: z.array(z.object({ id: z.string(), text: z.string() })).default([]).describe('Tags to include'),
  excludeTags: z.array(z.object({ id: z.string(), text: z.string() })).default([]).describe('Tags to exclude'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const UpdateAnalysisSchema = z.object({
  analysis_id: z.string().describe('The ID of the analysis'),
  name: z.string().optional().describe('Name of the analysis'),
  description: z.string().optional().describe('Description of the analysis'),
  measurementLength: z.number().optional().describe('Length of measurement period'),
  startDate: z.string().optional().describe('Start date for the analysis'),
  hasImplementationPeriod: z.boolean().optional().describe('Whether analysis has implementation period'),
  implementationLength: z.number().optional().describe('Length of implementation period'),
  selectedProducts: z.array(z.object({})).optional().describe('Selected products for analysis'),
  transactionAttributeFilter: z.object({}).optional().describe('Transaction attribute filter'),
  includeTags: z.array(z.object({ id: z.string(), text: z.string() })).optional().describe('Tags to include'),
  excludeTags: z.array(z.object({ id: z.string(), text: z.string() })).optional().describe('Tags to exclude'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const RunAnalysisSchema = z.object({
  analysis_id: z.string().describe('The ID of the analysis'),
  force_refresh: z.boolean().default(false).describe('Whether to force refresh'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const DateRangeSchema = z.object({
  start_date: z.string().describe('Start date (YYYY-MM-DD format)'),
  end_date: z.string().describe('End date (YYYY-MM-DD format)'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const CohortIdSchema = z.object({
  test_id: z.number().describe('The ID of the test'),
  impl_start_date: z.string().describe('Implementation start date'),
  test_start_date: z.string().describe('Test start date'),
  blockouts_string: z.string().default('').describe('Blockouts string (optional)'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const FileNameSchema = z.object({
  file_name: z.string().describe('Name of the file'),
  client: z.string().optional().describe('Client identifier (optional)')
});

const SiteIdSchema = z.object({
  client_site_id: z.string().describe('Client site ID'),
  client: z.string().optional().describe('Client identifier (optional)')
});

export function createTools(apiClient: CalcsApiClient): Tool[] {
  return [
    // Test Management Tools
    {
      name: 'get_tests',
      description: 'Get all tests for a client',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional, uses default if not provided)' }
        }
      }
    },
    {
      name: 'get_test_status',
      description: 'Get the status of a specific test',
      inputSchema: {
        type: 'object',
        properties: {
          test_id: { type: 'number', description: 'The ID of the test' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['test_id']
      }
    },
    {
      name: 'get_test_sites',
      description: 'Get treatment and control sites for a test',
      inputSchema: {
        type: 'object',
        properties: {
          test_id: { type: 'string', description: 'The ID of the test' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['test_id']
      }
    },
    {
      name: 'get_cohort_id',
      description: 'Get the hashed cohort ID for a test',
      inputSchema: {
        type: 'object',
        properties: {
          test_id: { type: 'number', description: 'The ID of the test' },
          impl_start_date: { type: 'string', description: 'Implementation start date' },
          test_start_date: { type: 'string', description: 'Test start date' },
          blockouts_string: { type: 'string', description: 'Blockouts string (optional)' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['test_id', 'impl_start_date', 'test_start_date']
      }
    },

    // Results Tools
    {
      name: 'get_test_results',
      description: 'Get test results with optional filtering',
      inputSchema: {
        type: 'object',
        properties: {
          test_id: { type: 'number', description: 'The ID of the test' },
          filter_type: { 
            type: 'string', 
            enum: ['OVERALL', 'CUSTOMER_COHORT', 'CUSTOMER_SEGMENT', 'SITE_COHORT', 'SITE_PAIR', 'FINISHED_COHORT', 'SITE_TAG'],
            description: 'The type of filter to apply' 
          },
          filter_value: { type: ['number', 'string'], description: 'The filter value (optional)' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['test_id', 'filter_type']
      }
    },
    {
      name: 'get_lift_explorer_results',
      description: 'Get lift explorer results',
      inputSchema: {
        type: 'object',
        properties: {
          lift_explorer_id: { type: 'string', description: 'The ID of the lift explorer' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['lift_explorer_id']
      }
    },
    {
      name: 'get_site_pair_lift_manifest',
      description: 'Get site pair lift manifest for a test',
      inputSchema: {
        type: 'object',
        properties: {
          test_id: { type: 'number', description: 'The ID of the test' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['test_id']
      }
    },
    {
      name: 'get_prediction_table',
      description: 'Get prediction table for a test',
      inputSchema: {
        type: 'object',
        properties: {
          test_id: { type: 'number', description: 'The ID of the test' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['test_id']
      }
    },
    {
      name: 'get_customer_cross',
      description: 'Get customer cross data for a test',
      inputSchema: {
        type: 'object',
        properties: {
          test_id: { type: 'number', description: 'The ID of the test' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['test_id']
      }
    },
    {
      name: 'download_all_test_data',
      description: 'Download all chart data for a test',
      inputSchema: {
        type: 'object',
        properties: {
          test_id: { type: 'number', description: 'The ID of the test' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['test_id']
      }
    },

    // Lift Exploration Tools
    {
      name: 'get_lift_exploration_ids',
      description: 'Get list of valid lift explorer IDs',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional)' }
        }
      }
    },

    // Analysis Management Tools
    {
      name: 'get_analyses',
      description: 'Get all analyses for a client',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional)' }
        }
      }
    },
    {
      name: 'get_analysis',
      description: 'Get a specific analysis by ID',
      inputSchema: {
        type: 'object',
        properties: {
          analysis_id: { type: 'string', description: 'The ID of the analysis' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['analysis_id']
      }
    },
    {
      name: 'create_analysis',
      description: 'Create a new analysis',
      inputSchema: {
        type: 'object',
        properties: {
          name: { type: 'string', description: 'Name of the analysis' },
          description: { type: 'string', description: 'Description of the analysis' },
          measurementLength: { type: 'number', description: 'Length of measurement period' },
          startDate: { type: 'string', description: 'Start date for the analysis' },
          hasImplementationPeriod: { type: 'boolean', description: 'Whether analysis has implementation period' },
          implementationLength: { type: 'number', description: 'Length of implementation period (optional)' },
          selectedProducts: { type: 'array', items: { type: 'object' }, description: 'Selected products for analysis' },
          transactionAttributeFilter: { type: 'object', description: 'Transaction attribute filter (optional)' },
          includeTags: { 
            type: 'array', 
            items: { 
              type: 'object',
              properties: {
                id: { type: 'string' },
                text: { type: 'string' }
              }
            }, 
            description: 'Tags to include' 
          },
          excludeTags: { 
            type: 'array', 
            items: { 
              type: 'object',
              properties: {
                id: { type: 'string' },
                text: { type: 'string' }
              }
            }, 
            description: 'Tags to exclude' 
          },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['name', 'description', 'measurementLength', 'startDate', 'hasImplementationPeriod']
      }
    },
    {
      name: 'update_analysis',
      description: 'Update an existing analysis',
      inputSchema: {
        type: 'object',
        properties: {
          analysis_id: { type: 'string', description: 'The ID of the analysis' },
          name: { type: 'string', description: 'Name of the analysis (optional)' },
          description: { type: 'string', description: 'Description of the analysis (optional)' },
          measurementLength: { type: 'number', description: 'Length of measurement period (optional)' },
          startDate: { type: 'string', description: 'Start date for the analysis (optional)' },
          hasImplementationPeriod: { type: 'boolean', description: 'Whether analysis has implementation period (optional)' },
          implementationLength: { type: 'number', description: 'Length of implementation period (optional)' },
          selectedProducts: { type: 'array', items: { type: 'object' }, description: 'Selected products for analysis (optional)' },
          transactionAttributeFilter: { type: 'object', description: 'Transaction attribute filter (optional)' },
          includeTags: { 
            type: 'array', 
            items: { 
              type: 'object',
              properties: {
                id: { type: 'string' },
                text: { type: 'string' }
              }
            }, 
            description: 'Tags to include (optional)' 
          },
          excludeTags: { 
            type: 'array', 
            items: { 
              type: 'object',
              properties: {
                id: { type: 'string' },
                text: { type: 'string' }
              }
            }, 
            description: 'Tags to exclude (optional)' 
          },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['analysis_id']
      }
    },
    {
      name: 'delete_analysis',
      description: 'Delete an analysis',
      inputSchema: {
        type: 'object',
        properties: {
          analysis_id: { type: 'string', description: 'The ID of the analysis' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['analysis_id']
      }
    },
    {
      name: 'run_analysis',
      description: 'Run an analysis (synchronous)',
      inputSchema: {
        type: 'object',
        properties: {
          analysis_id: { type: 'string', description: 'The ID of the analysis' },
          force_refresh: { type: 'boolean', description: 'Whether to force refresh (default: false)' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['analysis_id']
      }
    },
    {
      name: 'start_analysis',
      description: 'Start an analysis asynchronously',
      inputSchema: {
        type: 'object',
        properties: {
          analysis_id: { type: 'string', description: 'The ID of the analysis' },
          force_refresh: { type: 'boolean', description: 'Whether to force refresh (default: false)' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['analysis_id']
      }
    },
    {
      name: 'get_analysis_results',
      description: 'Get results of a completed analysis',
      inputSchema: {
        type: 'object',
        properties: {
          analysis_id: { type: 'string', description: 'The ID of the analysis' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['analysis_id']
      }
    },

    // Administrative Tools
    {
      name: 'get_active_clients',
      description: 'Get all active clients',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional)' }
        }
      }
    },
    {
      name: 'get_jobs_summary',
      description: 'Get summary of jobs in a date range',
      inputSchema: {
        type: 'object',
        properties: {
          start_date: { type: 'string', description: 'Start date (YYYY-MM-DD format)' },
          end_date: { type: 'string', description: 'End date (YYYY-MM-DD format)' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['start_date', 'end_date']
      }
    },
    {
      name: 'get_oldest_job_date',
      description: 'Get the date of the oldest job for a client',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional)' }
        }
      }
    },
    {
      name: 'get_newest_job_date',
      description: 'Get the date of the newest job for a client',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional)' }
        }
      }
    },
    {
      name: 'get_all_clients_jobs_summary',
      description: 'Get job summary for all clients in a date range',
      inputSchema: {
        type: 'object',
        properties: {
          start_date: { type: 'string', description: 'Start date (YYYY-MM-DD format)' },
          end_date: { type: 'string', description: 'End date (YYYY-MM-DD format)' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['start_date', 'end_date']
      }
    },

    // Site Tools
    {
      name: 'get_site_tests',
      description: 'Get all tests where a site has treatment or control role',
      inputSchema: {
        type: 'object',
        properties: {
          client_site_id: { type: 'string', description: 'Client site ID' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['client_site_id']
      }
    },

    // Adhoc Data Tools
    {
      name: 'list_adhoc_files',
      description: 'List uploaded adhoc files for a client',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional)' }
        }
      }
    },
    {
      name: 'get_column_names',
      description: 'Get column names from an uploaded adhoc file',
      inputSchema: {
        type: 'object',
        properties: {
          file_name: { type: 'string', description: 'Name of the file' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['file_name']
      }
    },
    {
      name: 'delete_adhoc_file',
      description: 'Delete an uploaded adhoc file',
      inputSchema: {
        type: 'object',
        properties: {
          file_name: { type: 'string', description: 'Name of the file' },
          client: { type: 'string', description: 'Client identifier (optional)' }
        },
        required: ['file_name']
      }
    },

    // Transaction Tools
    {
      name: 'describe_transactions',
      description: 'Get descriptive overview of the transactions table',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional)' }
        }
      }
    },

    // Utility Tools
    {
      name: 'health_check',
      description: 'Check API health status',
      inputSchema: {
        type: 'object',
        properties: {}
      }
    },
    {
      name: 'ping',
      description: 'Simple ping test to check API accessibility',
      inputSchema: {
        type: 'object',
        properties: {
          client: { type: 'string', description: 'Client identifier (optional)' }
        }
      }
    }
  ];
}

// Tool handlers
export async function handleToolCall(name: string, args: any, apiClient: CalcsApiClient) {
  try {
    switch (name) {
      // Test Management
      case 'get_tests': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.getTests(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_test_status': {
        const parsed = TestIdSchema.extend({ client: z.string().optional() }).parse(args);
        const result = await apiClient.getTestStatus(parsed.test_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_test_sites': {
        const parsed = TestIdStringSchema.extend({ client: z.string().optional() }).parse(args);
        const result = await apiClient.getTestSites(parsed.test_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_cohort_id': {
        const parsed = CohortIdSchema.parse(args);
        const result = await apiClient.getCohortId(
          parsed.test_id, 
          parsed.impl_start_date, 
          parsed.test_start_date, 
          parsed.blockouts_string,
          parsed.client
        );
        return result.error ? { error: result.error } : result.data;
      }

      // Results
      case 'get_test_results': {
        const parsed = TestResultsSchema.parse(args);
        const result = await apiClient.getTestResults(
          parsed.test_id, 
          parsed.filter_type, 
          parsed.filter_value,
          parsed.client
        );
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_lift_explorer_results': {
        const parsed = LiftExplorerSchema.parse(args);
        const result = await apiClient.getLiftExplorerResults(parsed.lift_explorer_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_site_pair_lift_manifest': {
        const parsed = TestIdSchema.extend({ client: z.string().optional() }).parse(args);
        const result = await apiClient.getSitePairLiftManifest(parsed.test_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_prediction_table': {
        const parsed = TestIdSchema.extend({ client: z.string().optional() }).parse(args);
        const result = await apiClient.getPredictionTable(parsed.test_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_customer_cross': {
        const parsed = TestIdSchema.extend({ client: z.string().optional() }).parse(args);
        const result = await apiClient.getCustomerCross(parsed.test_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'download_all_test_data': {
        const parsed = TestIdSchema.extend({ client: z.string().optional() }).parse(args);
        const result = await apiClient.downloadAllTestData(parsed.test_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      // Lift Explorations
      case 'get_lift_exploration_ids': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.getLiftExplorationIds(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      // Analysis Management
      case 'get_analyses': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.getAnalyses(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_analysis': {
        const parsed = AnalysisIdSchema.parse(args);
        const result = await apiClient.getAnalysis(parsed.analysis_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'create_analysis': {
        const parsed = CreateAnalysisSchema.parse(args);
        const { client, ...analysisData } = parsed;
        // Convert undefined to null for API compatibility
        const apiData = {
          ...analysisData,
          implementationLength: analysisData.implementationLength ?? null,
          transactionAttributeFilter: analysisData.transactionAttributeFilter ?? null
        };
        const result = await apiClient.createAnalysis(apiData, client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'update_analysis': {
        const parsed = UpdateAnalysisSchema.parse(args);
        const { analysis_id, client, ...updateData } = parsed;
        // Convert undefined to null for API compatibility
        const apiData = {
          name: updateData.name ?? null,
          description: updateData.description ?? null,
          measurementLength: updateData.measurementLength ?? null,
          startDate: updateData.startDate ?? null,
          hasImplementationPeriod: updateData.hasImplementationPeriod ?? null,
          implementationLength: updateData.implementationLength ?? null,
          selectedProducts: updateData.selectedProducts ?? null,
          transactionAttributeFilter: updateData.transactionAttributeFilter ?? null,
          includeTags: updateData.includeTags ?? null,
          excludeTags: updateData.excludeTags ?? null
        };
        const result = await apiClient.updateAnalysis(analysis_id, apiData, client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'delete_analysis': {
        const parsed = AnalysisIdSchema.parse(args);
        const result = await apiClient.deleteAnalysis(parsed.analysis_id, parsed.client);
        return result.error ? { error: result.error } : { success: true };
      }

      case 'run_analysis': {
        const parsed = RunAnalysisSchema.parse(args);
        const result = await apiClient.runAnalysis(parsed.analysis_id, parsed.force_refresh, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'start_analysis': {
        const parsed = RunAnalysisSchema.parse(args);
        const result = await apiClient.startAnalysis(parsed.analysis_id, parsed.force_refresh, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_analysis_results': {
        const parsed = AnalysisIdSchema.parse(args);
        const result = await apiClient.getAnalysisResults(parsed.analysis_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      // Administrative
      case 'get_active_clients': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.getActiveClients(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_jobs_summary': {
        const parsed = DateRangeSchema.parse(args);
        const result = await apiClient.getJobsSummary(parsed.start_date, parsed.end_date, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_oldest_job_date': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.getOldestJobDate(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_newest_job_date': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.getNewestJobDate(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_all_clients_jobs_summary': {
        const parsed = DateRangeSchema.parse(args);
        const result = await apiClient.getAllClientsJobsSummary(parsed.start_date, parsed.end_date, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      // Sites
      case 'get_site_tests': {
        const parsed = SiteIdSchema.parse(args);
        const result = await apiClient.getSiteTests(parsed.client_site_id, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      // Adhoc Data
      case 'list_adhoc_files': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.listAdhocFiles(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'get_column_names': {
        const parsed = FileNameSchema.parse(args);
        const result = await apiClient.getColumnNames(parsed.file_name, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      case 'delete_adhoc_file': {
        const parsed = FileNameSchema.parse(args);
        const result = await apiClient.deleteAdhocFile(parsed.file_name, parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      // Transactions
      case 'describe_transactions': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.describeTransactions(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      // Utility
      case 'health_check': {
        const result = await apiClient.healthCheck();
        return result.error ? { error: result.error } : result.data;
      }

      case 'ping': {
        const parsed = ClientSchema.parse(args);
        const result = await apiClient.ping(parsed.client);
        return result.error ? { error: result.error } : result.data;
      }

      default:
        return { error: `Unknown tool: ${name}` };
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { error: `Validation error: ${error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ')}` };
    }
    return { error: error instanceof Error ? error.message : 'Unknown error occurred' };
  }
}