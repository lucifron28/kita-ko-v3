import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reportsAPI } from '../services/api';
import toast from 'react-hot-toast';

// Query keys
export const QUERY_KEYS = {
  reports: ['reports'],
  report: (id) => ['reports', id],
};

// Fetch reports
export const useReports = () => {
  return useQuery({
    queryKey: QUERY_KEYS.reports,
    queryFn: async () => {
      const response = await reportsAPI.getReports();
      // Ensure we always return an array
      return Array.isArray(response.data) ? response.data : 
             Array.isArray(response.data.results) ? response.data.results : [];
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    cacheTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Create report mutation
export const useCreateReport = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (reportData) => reportsAPI.createReport(reportData),
    onSuccess: (response) => {
      // Update the reports cache
      queryClient.setQueryData(QUERY_KEYS.reports, (old = []) => {
        const newReport = response.data.report || response.data;
        return [newReport, ...old];
      });
      
      toast.success('Report created successfully!');
    },
    onError: (error) => {
      console.error('Failed to create report:', error);
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          Object.values(error.response?.data || {}).flat().join(', ') ||
                          'Failed to create report';
      toast.error(errorMessage);
    },
  });
};

// Generate PDF mutation
export const useGeneratePDF = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ reportId, include_ai_analysis = true }) => 
      reportsAPI.generatePDF({ report_id: reportId, include_ai_analysis }),
    onSuccess: (response, variables) => {
      // Update the specific report in cache to show generating status
      queryClient.setQueryData(QUERY_KEYS.reports, (old = []) => {
        return old.map(report => 
          report.id === variables.reportId 
            ? { ...report, status: 'generating' }
            : report
        );
      });
      
      // Start status polling
      const pollForCompletion = async () => {
        const startTime = Date.now();
        const maxWaitTime = 5 * 60 * 1000; // 5 minutes
        
        const poll = async () => {
          try {
            if (Date.now() - startTime > maxWaitTime) {
              toast.error('PDF generation is taking longer than expected');
              return;
            }
            
            const statusResponse = await reportsAPI.getReportStatus(variables.reportId);
            const status = statusResponse.data;
            
            // Update cache with status
            queryClient.setQueryData(QUERY_KEYS.reports, (old = []) => {
              return old.map(report => 
                report.id === variables.reportId 
                  ? { 
                      ...report, 
                      status: status.status,
                      pdf_file: status.pdf_available ? report.pdf_file || 'generated' : null 
                    }
                  : report
              );
            });
            
            if (status.status === 'completed') {
              toast.success('PDF generated successfully!');
              
              // Refresh the full report data
              setTimeout(async () => {
                try {
                  const reportResponse = await reportsAPI.getReport(variables.reportId);
                  queryClient.setQueryData(QUERY_KEYS.reports, (old = []) => {
                    return old.map(report => 
                      report.id === variables.reportId ? reportResponse.data : report
                    );
                  });
                } catch (e) {
                  console.error('Failed to refresh report:', e);
                }
              }, 500);
              
            } else if (status.status === 'failed') {
              toast.error(`PDF generation failed: ${status.message || 'Unknown error'}`);
            } else {
              // Continue polling
              setTimeout(poll, 3000);
            }
            
          } catch (error) {
            console.error('Status polling error:', error);
            // Continue polling on temporary errors
            setTimeout(poll, 5000);
          }
        };
        
        poll();
      };
      
      pollForCompletion();
      toast.success('PDF generation started! Please wait...');
    },
    onError: (error) => {
      console.error('Failed to generate PDF:', error);
      toast.error('Failed to start PDF generation');
    },
  });
};

// Download report mutation
export const useDownloadReport = () => {
  return useMutation({
    mutationFn: ({ reportId, title }) => reportsAPI.downloadReport(reportId),
    onSuccess: (response, variables) => {
      // Handle file download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${variables.title}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Report downloaded successfully!');
    },
    onError: (error) => {
      console.error('Failed to download report:', error);
      toast.error('Failed to download report');
    },
  });
};

// Delete report mutation
export const useDeleteReport = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (reportId) => reportsAPI.deleteReport(reportId),
    onSuccess: (_, reportId) => {
      // Remove the report from cache
      queryClient.setQueryData(QUERY_KEYS.reports, (old = []) => {
        return old.filter(report => report.id !== reportId);
      });
      
      toast.success('Report deleted successfully!');
    },
    onError: (error) => {
      console.error('Failed to delete report:', error);
      toast.error('Failed to delete report');
    },
  });
};
