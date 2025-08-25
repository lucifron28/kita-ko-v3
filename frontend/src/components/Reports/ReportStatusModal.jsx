import { useState, useEffect } from 'react';
import { 
  X, 
  Download, 
  FileText, 
  Shield, 
  AlertCircle, 
  CheckCircle, 
  Clock,
  DollarSign,
  TrendingUp,
  Eye,
  RefreshCw,
  Calendar,
  Database,
  Brain
} from 'lucide-react';
import { reportsAPI, formatCurrency, formatDate, formatDateTime } from '../../services/api';
import LoadingSpinner from '../UI/LoadingSpinner';
import toast from 'react-hot-toast';

const ReportStatusModal = ({ report, onClose, onDownload, onGeneratePDF }) => {
  const [reportDetails, setReportDetails] = useState(report);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchReportDetails();
  }, [report.id]);

  useEffect(() => {
    // Update local state when report prop changes (e.g., after PDF generation)
    setReportDetails(report);
  }, [report]);

  const fetchReportDetails = async () => {
    try {
      setLoading(true);
      const response = await reportsAPI.getReport(report.id);
      setReportDetails(response.data);
    } catch (error) {
      console.error('Failed to fetch report details:', error);
      toast.error('Failed to load report details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'generating':
        return <Clock className="w-6 h-6 text-yellow-600 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-6 h-6 text-red-600" />;
      default:
        return <FileText className="w-6 h-6 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-200 bg-green-900/50 border border-green-800';
      case 'generating':
        return 'text-yellow-200 bg-yellow-900/50 border border-yellow-800';
      case 'failed':
        return 'text-red-200 bg-red-900/50 border border-red-800';
      default:
        return 'text-gray-200 bg-gray-700 border border-gray-600';
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const renderIncomeBreakdown = () => {
    if (!reportDetails.income_breakdown || Object.keys(reportDetails.income_breakdown).length === 0) {
      return <p className="text-gray-400 text-sm">No income data available</p>;
    }

    return (
      <div className="space-y-2">
        {Object.entries(reportDetails.income_breakdown).map(([category, amount]) => (
          <div key={category} className="flex justify-between items-center">
            <span className="text-sm text-gray-300 capitalize">
              {category.replace('_', ' ')}
            </span>
            <span className="text-sm font-medium text-gray-200">
              {formatCurrency(amount)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-8 max-w-md w-full mx-4 border border-gray-700">
          <div className="flex justify-center">
            <LoadingSpinner />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            {getStatusIcon(reportDetails.status)}
            <div>
              <h2 className="text-xl font-semibold text-white">
                {reportDetails.title}
              </h2>
              <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(reportDetails.status)}`}>
                {reportDetails.status.charAt(0).toUpperCase() + reportDetails.status.slice(1)}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Report Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-white flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Report Details
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Period:</span>
                  <span className="font-medium text-gray-200">
                    {formatDate(reportDetails.date_from)} - {formatDate(reportDetails.date_to)}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-400">Purpose:</span>
                  <span className="font-medium capitalize text-gray-200">
                    {reportDetails.purpose?.replace('_', ' ')}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-400">Created:</span>
                  <span className="font-medium text-gray-200">
                    {formatDateTime(reportDetails.created_at)}
                  </span>
                </div>
                
                {reportDetails.completed_at && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Completed:</span>
                    <span className="font-medium text-gray-200">
                      {formatDateTime(reportDetails.completed_at)}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-medium text-white flex items-center">
                <DollarSign className="w-5 h-5 mr-2" />
                Financial Summary
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Income:</span>
                  <span className="font-medium text-green-400">
                    {reportDetails.formatted_total_income || formatCurrency(reportDetails.total_income)}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Expenses:</span>
                  <span className="font-medium text-red-400">
                    {formatCurrency(reportDetails.total_expenses)}
                  </span>
                </div>
                
                <div className="flex justify-between border-t border-gray-700 pt-2">
                  <span className="text-gray-300 font-medium">Net Income:</span>
                  <span className={`font-semibold ${reportDetails.net_income >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {reportDetails.formatted_net_income || formatCurrency(reportDetails.net_income)}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Monthly:</span>
                  <span className="font-medium text-gray-200">
                    {formatCurrency(reportDetails.average_monthly_income)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Data Quality */}
          <div className="border-t border-gray-700 pt-6">
            <h3 className="text-lg font-medium text-white flex items-center mb-4">
              <Database className="w-5 h-5 mr-2" />
              Data Quality & Sources
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-300">Confidence Score</span>
                  <span className={`text-sm font-bold ${getConfidenceColor(reportDetails.confidence_score)}`}>
                    {reportDetails.confidence_score}%
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      reportDetails.confidence_score >= 80 ? 'bg-green-500' :
                      reportDetails.confidence_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${reportDetails.confidence_score}%` }}
                  />
                </div>
              </div>
              
              <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <span className="text-sm text-gray-300">Transactions</span>
                <p className="text-xl font-bold text-white">
                  {reportDetails.transaction_count}
                </p>
              </div>
              
              <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <span className="text-sm text-gray-300">Data Sources</span>
                <p className="text-xl font-bold text-white">
                  {reportDetails.data_sources?.length || 0}
                </p>
                {reportDetails.data_sources && reportDetails.data_sources.length > 0 && (
                  <p className="text-xs text-gray-400 mt-1">
                    {reportDetails.data_sources.join(', ')}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Income Breakdown */}
          {reportDetails.income_breakdown && Object.keys(reportDetails.income_breakdown).length > 0 && (
            <div className="border-t border-gray-700 pt-6">
              <h3 className="text-lg font-medium text-white flex items-center mb-4">
                <TrendingUp className="w-5 h-5 mr-2" />
                Income Breakdown
              </h3>
              <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                {renderIncomeBreakdown()}
              </div>
            </div>
          )}

          {/* AI Insights */}
          {reportDetails.ai_insights && (
            <div className="border-t border-gray-700 pt-6">
              <h3 className="text-lg font-medium text-white flex items-center mb-4">
                <Brain className="w-5 h-5 mr-2" />
                AI Analysis
              </h3>
              <div className="bg-blue-900/30 p-4 rounded-lg border border-blue-800">
                <div className="whitespace-pre-line text-sm text-blue-200">
                  {reportDetails.ai_insights}
                </div>
              </div>
            </div>
          )}

          {/* Anomalies */}
          {reportDetails.anomalies_detected && reportDetails.anomalies_detected.length > 0 && (
            <div className="border-t border-gray-700 pt-6">
              <h3 className="text-lg font-medium text-white flex items-center mb-4">
                <AlertCircle className="w-5 h-5 mr-2" />
                Detected Anomalies
              </h3>
              <div className="bg-yellow-900/30 p-4 rounded-lg border border-yellow-800">
                <ul className="list-disc list-inside space-y-1">
                  {reportDetails.anomalies_detected.map((anomaly, index) => (
                    <li key={index} className="text-sm text-yellow-200">{anomaly}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Legal Notice */}
          <div className="border-t border-gray-700 pt-6">
            <div className="bg-amber-900/30 border border-amber-800 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Shield className="w-5 h-5 text-amber-400 mt-0.5" />
                <div>
                  <h4 className="font-medium text-amber-200">Legal Validity Notice</h4>
                  <p className="text-sm text-amber-300 mt-1">
                    This is a preliminary document that requires notarization for legal validity. 
                    The generated PDF includes signature sections and notary acknowledgment forms 
                    for official use.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between p-6 border-t border-gray-700 bg-gray-800">
          <div className="text-sm text-gray-400">
            Verification Code: <span className="font-mono font-medium text-gray-300">{reportDetails.verification_code}</span>
          </div>
          
          <div className="flex items-center space-x-3">
            {reportDetails.status === 'completed' && reportDetails.pdf_url ? (
              <button
                onClick={() => onDownload(reportDetails)}
                className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Download PDF</span>
              </button>
            ) : reportDetails.status !== 'generating' ? (
              <button
                onClick={() => onGeneratePDF(reportDetails.id)}
                className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                <FileText className="w-4 h-4" />
                <span>Generate PDF</span>
              </button>
            ) : (
              <div className="flex items-center space-x-2 text-yellow-400">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Generating PDF...</span>
              </div>
            )}
            
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-300 bg-gray-700 border border-gray-600 rounded-lg hover:bg-gray-600 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportStatusModal;
