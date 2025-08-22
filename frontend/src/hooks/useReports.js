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
      // Update the specific report in cache
      queryClient.setQueryData(QUERY_KEYS.reports, (old = []) => {
        return old.map(report => 
          report.id === variables.reportId 
            ? { ...report, status: 'completed', pdf_file: response.data.report.pdf_file }
            : report
        );
      });
      
      toast.success('PDF generated successfully!');
    },
    onError: (error) => {
      console.error('Failed to generate PDF:', error);
      toast.error('Failed to generate PDF');
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
