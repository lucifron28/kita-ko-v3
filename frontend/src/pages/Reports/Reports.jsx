import { useState } from 'react';
import { 
  FileText, 
  Plus, 
  Download, 
  Eye, 
  Trash2,
  Calendar,
  DollarSign,
  CheckCircle,
  Clock,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { formatCurrency, formatDate } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import CreateReportModal from '../../components/Reports/CreateReportModal';
import ReportStatusModal from '../../components/Reports/ReportStatusModal';
import { 
  useReports, 
  useCreateReport, 
  useGeneratePDF, 
  useDownloadReport, 
  useDeleteReport 
} from '../../hooks/useReports';

const Reports = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  
  // React Query hooks
  const { data: reports = [], isLoading, error } = useReports();
  const createReportMutation = useCreateReport();
  const generatePDFMutation = useGeneratePDF();
  const downloadReportMutation = useDownloadReport();
  const deleteReportMutation = useDeleteReport();

  // Event handlers
  const handleCreateReport = (reportData) => {
    createReportMutation.mutate(reportData, {
      onSuccess: () => {
        setShowCreateModal(false);
      },
    });
  };

  const handleGeneratePDF = (reportId) => {
    generatePDFMutation.mutate({ reportId, include_ai_analysis: true });
  };

  const handleDownloadReport = (report) => {
    downloadReportMutation.mutate({ 
      reportId: report.id, 
      title: report.title 
    });
  };

  const handleDeleteReport = (reportId) => {
    if (!confirm('Are you sure you want to delete this report?')) return;
    deleteReportMutation.mutate(reportId);
  };

  const handleViewReport = (report) => {
    setSelectedReport(report);
    setShowStatusModal(true);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'generating':
        return <LoadingSpinner size="sm" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'generating':
        return 'text-yellow-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getPurposeLabel = (purpose) => {
    const purposes = {
      loan_application: 'Loan Application',
      government_subsidy: 'Government Subsidy',
      insurance_application: 'Insurance Application',
      visa_application: 'Visa Application',
      employment_verification: 'Employment Verification',
      other: 'Other',
    };
    return purposes[purpose] || purpose;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">Failed to load reports</h3>
          <p className="text-gray-400">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Income Reports</h1>
          <p className="text-gray-400 mt-1">
            Generate professional income reports for loans, subsidies, and applications
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowCreateModal(true)}
            disabled={createReportMutation.isPending}
            className="btn-primary inline-flex items-center disabled:opacity-50"
          >
            {createReportMutation.isPending ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 mr-2" />
                Create Report
              </>
            )}
          </button>
        </div>
      </div>

      {/* Reports Grid */}
      {reports.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {reports.map((report) => (
            <div key={report.id} className="card">
              <div className="card-header">
                <div className="flex items-start justify-between">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-purple-400 mr-2" />
                    <div>
                      <h3 className="font-medium text-white truncate">
                        {report.title}
                      </h3>
                      <p className="text-sm text-gray-400">
                        {getPurposeLabel(report.purpose)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    {getStatusIcon(report.status)}
                  </div>
                </div>
              </div>

              <div className="card-body">
                {/* Report Details */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Period:</span>
                    <span className="text-white">
                      {formatDate(report.date_from)} - {formatDate(report.date_to)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Total Income:</span>
                    <span className="text-green-400 font-medium">
                      {formatCurrency(report.total_income)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Net Income:</span>
                    <span className="text-white font-medium">
                      {formatCurrency(report.net_income)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Status:</span>
                    <span className={`capitalize ${getStatusColor(report.status)}`}>
                      {report.status}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Created:</span>
                    <span className="text-white">
                      {formatDate(report.created_at)}
                    </span>
                  </div>

                  {report.verification_code && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Verification:</span>
                      <span className="text-purple-400 font-mono text-xs">
                        {report.verification_code}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <div className="card-footer">
                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    {report.status === 'draft' && (
                      <button
                        onClick={() => handleGeneratePDF(report.id)}
                        disabled={generatePDFMutation.isPending}
                        className="btn-primary text-xs px-3 py-1"
                      >
                        {generatePDFMutation.isPending && generatePDFMutation.variables?.reportId === report.id ? (
                          <>
                            <LoadingSpinner size="sm" className="mr-1" />
                            Generating...
                          </>
                        ) : (
                          'Generate PDF'
                        )}
                      </button>
                    )}

                    {report.status === 'completed' && (
                      <>
                        <button
                          onClick={() => handleDownloadReport(report)}
                          disabled={downloadReportMutation.isPending}
                          className="btn-success text-xs px-3 py-1 inline-flex items-center"
                        >
                          {downloadReportMutation.isPending && downloadReportMutation.variables?.reportId === report.id ? (
                            <LoadingSpinner size="sm" className="mr-1" />
                          ) : (
                            <Download className="w-3 h-3 mr-1" />
                          )}
                          Download
                        </button>
                      </>
                    )}
                  </div>

                  <div className="flex space-x-1">
                    <button
                      onClick={() => handleViewReport(report)}
                      className="p-1 text-gray-400 hover:text-blue-400"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteReport(report.id)}
                      disabled={deleteReportMutation.isPending}
                      className="p-1 text-gray-400 hover:text-red-400 disabled:opacity-50"
                      title="Delete Report"
                    >
                      {deleteReportMutation.isPending && deleteReportMutation.variables === report.id ? (
                        <LoadingSpinner size="sm" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Empty State */
        <div className="card">
          <div className="card-body text-center py-12">
            <FileText className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No reports yet</h3>
            <p className="text-gray-400 mb-4">
              Create your first income report to get started with proof-of-income documentation.
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              disabled={createReportMutation.isPending}
              className="btn-primary disabled:opacity-50"
            >
              {createReportMutation.isPending ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Creating...
                </>
              ) : (
                'Create Your First Report'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Report Features */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-white">Report Features</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="w-12 h-12 bg-green-500 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-medium text-white mb-1">AI-Powered Analysis</h3>
              <p className="text-sm text-gray-400">
                Intelligent categorization and insights
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-blue-500 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-medium text-white mb-1">Professional Format</h3>
              <p className="text-sm text-gray-400">
                Bank-ready PDF reports
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <ExternalLink className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-medium text-white mb-1">Verification System</h3>
              <p className="text-sm text-gray-400">
                Unique codes for authenticity
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-orange-500 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <ExternalLink className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-medium text-white mb-1">Easy Access</h3>
              <p className="text-sm text-gray-400">
                Quick links and downloads
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Create Report Modal */}
      {showCreateModal && (
        <CreateReportModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateReport}
        />
      )}

      {/* Report Status Modal */}
      {showStatusModal && selectedReport && (
        <ReportStatusModal
          report={selectedReport}
          onClose={() => {
            setShowStatusModal(false);
            setSelectedReport(null);
          }}
          onDownload={handleDownloadReport}
          onGeneratePDF={handleGeneratePDF}
        />
      )}
    </div>
  );
};

export default Reports;
