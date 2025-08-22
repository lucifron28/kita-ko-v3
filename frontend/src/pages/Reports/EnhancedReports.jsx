import { useState, useEffect } from 'react';
import { 
  FileText, 
  Plus, 
  Download, 
  Eye, 
  Share, 
  Trash2,
  Calendar,
  DollarSign,
  CheckCircle,
  Clock,
  AlertCircle,
  ExternalLink,
  RefreshCw,
  Shield,
  Users,
  TrendingUp
} from 'lucide-react';
import { reportsAPI, formatCurrency, formatDate, downloadFile } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import CreateReportModal from '../../components/Reports/CreateReportModal';
import ReportStatusModal from '../../components/Reports/ReportStatusModal';
import toast from 'react-hot-toast';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [generatingPDF, setGeneratingPDF] = useState({});
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetchReports();
    fetchAnalytics();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await reportsAPI.getReports();
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await reportsAPI.getAnalytics();
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const handleCreateReport = async (reportData) => {
    try {
      // Validate that user has transactions in the selected period
      const response = await reportsAPI.createReport(reportData);
      
      if (response.data.report.transaction_count === 0) {
        toast.error('No transactions found for the selected period. Please upload transaction data first.');
        return;
      }

      toast.success('Report created successfully!');
      setReports(prev => [response.data.report, ...prev]);
      setShowCreateModal(false);
      
      // Refresh analytics
      fetchAnalytics();
    } catch (error) {
      console.error('Failed to create report:', error);
      const errorMessage = error.response?.data?.details || 'Failed to create report';
      toast.error(errorMessage);
    }
  };

  const handleGeneratePDF = async (reportId) => {
    console.log('Generate PDF called for report:', reportId);
    
    try {
      setGeneratingPDF(prev => ({ ...prev, [reportId]: true }));
      
      console.log('Making API call to generate PDF...');
      const response = await reportsAPI.generatePDF({
        report_id: reportId,
        include_ai_analysis: true,
      });

      console.log('API response:', response.data);

      if (response.data.report) {
        toast.success('PDF generated successfully!');
        
        // Update the report in the list
        setReports(prev => prev.map(report => 
          report.id === reportId 
            ? { ...report, ...response.data.report }
            : report
        ));
        
        // Show status modal for progress
        const report = reports.find(r => r.id === reportId);
        setSelectedReport(report);
        setShowStatusModal(true);
      }
    } catch (error) {
      console.error('Failed to generate PDF:', error);
      console.error('Error details:', error.response?.data);
      const errorMessage = error.response?.data?.details || error.message || 'Failed to generate PDF';
      toast.error(errorMessage);
    } finally {
      setGeneratingPDF(prev => ({ ...prev, [reportId]: false }));
    }
  };

  const handleDownloadReport = async (report) => {
    try {
      if (!report.pdf_url) {
        toast.error('PDF not available. Please generate the PDF first.');
        return;
      }

      const response = await reportsAPI.downloadReport(report.id);
      const filename = `${report.title.replace(/[^a-z0-9]/gi, '_')}.pdf`;
      downloadFile(response.data, filename);
      toast.success('Report downloaded successfully!');
    } catch (error) {
      console.error('Failed to download report:', error);
      toast.error('Failed to download report');
    }
  };

  const handleDeleteReport = async (reportId) => {
    if (!confirm('Are you sure you want to delete this report? This action cannot be undone.')) return;

    try {
      await reportsAPI.deleteReport(reportId);
      setReports(prev => prev.filter(report => report.id !== reportId));
      toast.success('Report deleted successfully!');
      fetchAnalytics(); // Refresh analytics
    } catch (error) {
      console.error('Failed to delete report:', error);
      toast.error('Failed to delete report');
    }
  };

  const handleViewReport = (report) => {
    setSelectedReport(report);
    setShowStatusModal(true);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'generating':
        return <Clock className="w-5 h-5 text-yellow-600 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'generating':
        return 'text-yellow-600 bg-yellow-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Income Reports</h1>
          <p className="text-gray-600 mt-1">
            Generate and manage your proof of income documents
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Create Report</span>
        </button>
      </div>

      {/* Analytics Summary */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Reports</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.total_reports}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-green-600">{analytics.completed_reports}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-blue-600">{analytics.success_rate.toFixed(1)}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Downloads</p>
                <p className="text-2xl font-bold text-purple-600">{analytics.total_downloads}</p>
              </div>
              <Download className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>
      )}

      {/* Important Notice */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Shield className="w-6 h-6 text-amber-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-amber-800">Legal Notice</h3>
            <p className="text-amber-700 mt-1">
              All generated reports are preliminary documents that require notarization for legal validity. 
              These reports are intended to facilitate the preparation of official income documentation.
            </p>
          </div>
        </div>
      </div>

      {/* Reports List */}
      {reports.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No reports yet</h3>
          <p className="text-gray-600 mb-4">
            Create your first income report to get started
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Your First Report
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {report.title}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                      {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">
                        {formatDate(report.date_from)} - {formatDate(report.date_to)}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <DollarSign className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">
                        {report.formatted_total_income || formatCurrency(report.total_income)}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Users className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">
                        {report.transaction_count} transactions
                      </span>
                    </div>
                  </div>

                  {report.confidence_score && (
                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600">Data Confidence</span>
                        <span className="font-medium">{report.confidence_score}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            report.confidence_score >= 80 ? 'bg-green-500' :
                            report.confidence_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${report.confidence_score}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  {getStatusIcon(report.status)}
                  
                  <button
                    onClick={() => handleViewReport(report)}
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>

                  {report.status === 'completed' && report.pdf_url ? (
                    <button
                      onClick={() => handleDownloadReport(report)}
                      className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-100 rounded-lg transition-colors"
                      title="Download PDF"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  ) : (
                    <button
                      onClick={() => handleGeneratePDF(report.id)}
                      disabled={generatingPDF[report.id] || report.status === 'generating'}
                      className="p-2 text-green-600 hover:text-green-700 hover:bg-green-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Generate PDF"
                    >
                      {generatingPDF[report.id] ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <FileText className="w-4 h-4" />
                      )}
                    </button>
                  )}

                  <button
                    onClick={() => handleDeleteReport(report.id)}
                    className="p-2 text-red-600 hover:text-red-700 hover:bg-red-100 rounded-lg transition-colors"
                    title="Delete Report"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      {showCreateModal && (
        <CreateReportModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateReport}
        />
      )}

      {showStatusModal && selectedReport && (
        <ReportStatusModal
          report={selectedReport}
          onClose={() => {
            setShowStatusModal(false);
            setSelectedReport(null);
            fetchReports(); // Refresh reports after viewing details
          }}
          onDownload={handleDownloadReport}
          onGeneratePDF={handleGeneratePDF}
        />
      )}
    </div>
  );
};

export default Reports;
