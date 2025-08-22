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
  const [statusPolling, setStatusPolling] = useState(false);

  useEffect(() => {
    if (report.status === 'generating') {
      startStatusPolling();
    }
    fetchReportDetails();
  }, [report.id]);

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

  const startStatusPolling = () => {
    if (statusPolling) return;
    
    setStatusPolling(true);
    const interval = setInterval(async () => {
      try {
        const response = await reportsAPI.getReportStatus(report.id);
        const status = response.data;
        
        setReportDetails(prev => ({
          ...prev,
          status: status.status,
          pdf_url: status.pdf_available ? prev.pdf_url : null
        }));

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          setStatusPolling(false);
          fetchReportDetails(); // Get full updated details
          
          if (status.status === 'completed') {
            toast.success('PDF generated successfully!');
          } else if (status.status === 'failed') {
            toast.error(`PDF generation failed: ${status.message}`);
          }
        }
      } catch (error) {
        console.error('Status polling error:', error);
        clearInterval(interval);
        setStatusPolling(false);
      }
    }, 2000);

    return () => {
      clearInterval(interval);
      setStatusPolling(false);
    };
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
        return 'text-green-700 bg-green-100';
      case 'generating':
        return 'text-yellow-700 bg-yellow-100';
      case 'failed':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const renderIncomeBreakdown = () => {
    if (!reportDetails.income_breakdown || Object.keys(reportDetails.income_breakdown).length === 0) {
      return <p className="text-gray-500 text-sm">No income data available</p>;
    }

    return (
      <div className="space-y-2">
        {Object.entries(reportDetails.income_breakdown).map(([category, amount]) => (
          <div key={category} className="flex justify-between items-center">
            <span className="text-sm text-gray-600 capitalize">
              {category.replace('_', ' ')}
            </span>
            <span className="text-sm font-medium">
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
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="flex justify-center">
            <LoadingSpinner />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            {getStatusIcon(reportDetails.status)}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {reportDetails.title}
              </h2>
              <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(reportDetails.status)}`}>
                {reportDetails.status.charAt(0).toUpperCase() + reportDetails.status.slice(1)}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Report Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Report Details
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Period:</span>
                  <span className="font-medium">
                    {formatDate(reportDetails.date_from)} - {formatDate(reportDetails.date_to)}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Purpose:</span>
                  <span className="font-medium capitalize">
                    {reportDetails.purpose?.replace('_', ' ')}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Created:</span>
                  <span className="font-medium">
                    {formatDateTime(reportDetails.created_at)}
                  </span>
                </div>
                
                {reportDetails.completed_at && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Completed:</span>
                    <span className="font-medium">
                      {formatDateTime(reportDetails.completed_at)}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <DollarSign className="w-5 h-5 mr-2" />
                Financial Summary
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Income:</span>
                  <span className="font-medium text-green-600">
                    {reportDetails.formatted_total_income || formatCurrency(reportDetails.total_income)}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Expenses:</span>
                  <span className="font-medium text-red-600">
                    {formatCurrency(reportDetails.total_expenses)}
                  </span>
                </div>
                
                <div className="flex justify-between border-t pt-2">
                  <span className="text-gray-600 font-medium">Net Income:</span>
                  <span className={`font-semibold ${reportDetails.net_income >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {reportDetails.formatted_net_income || formatCurrency(reportDetails.net_income)}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Monthly:</span>
                  <span className="font-medium">
                    {formatCurrency(reportDetails.average_monthly_income)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Data Quality */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 flex items-center mb-4">
              <Database className="w-5 h-5 mr-2" />
              Data Quality & Sources
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Confidence Score</span>
                  <span className={`text-sm font-bold ${getConfidenceColor(reportDetails.confidence_score)}`}>
                    {reportDetails.confidence_score}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      reportDetails.confidence_score >= 80 ? 'bg-green-500' :
                      reportDetails.confidence_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${reportDetails.confidence_score}%` }}
                  />
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <span className="text-sm text-gray-600">Transactions</span>
                <p className="text-xl font-bold text-gray-900">
                  {reportDetails.transaction_count}
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <span className="text-sm text-gray-600">Data Sources</span>
                <p className="text-xl font-bold text-gray-900">
                  {reportDetails.data_sources?.length || 0}
                </p>
                {reportDetails.data_sources && reportDetails.data_sources.length > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    {reportDetails.data_sources.join(', ')}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Income Breakdown */}
          {reportDetails.income_breakdown && Object.keys(reportDetails.income_breakdown).length > 0 && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 flex items-center mb-4">
                <TrendingUp className="w-5 h-5 mr-2" />
                Income Breakdown
              </h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                {renderIncomeBreakdown()}
              </div>
            </div>
          )}

          {/* AI Insights */}
          {reportDetails.ai_insights && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 flex items-center mb-4">
                <Brain className="w-5 h-5 mr-2" />
                AI Analysis
              </h3>
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="whitespace-pre-line text-sm text-blue-800">
                  {reportDetails.ai_insights}
                </div>
              </div>
            </div>
          )}

          {/* Anomalies */}
          {reportDetails.anomalies_detected && reportDetails.anomalies_detected.length > 0 && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 flex items-center mb-4">
                <AlertCircle className="w-5 h-5 mr-2" />
                Detected Anomalies
              </h3>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <ul className="list-disc list-inside space-y-1">
                  {reportDetails.anomalies_detected.map((anomaly, index) => (
                    <li key={index} className="text-sm text-yellow-800">{anomaly}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Legal Notice */}
          <div className="border-t pt-6">
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Shield className="w-5 h-5 text-amber-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-amber-800">Legal Validity Notice</h4>
                  <p className="text-sm text-amber-700 mt-1">
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
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-500">
            Verification Code: <span className="font-mono font-medium">{reportDetails.verification_code}</span>
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
              <div className="flex items-center space-x-2 text-yellow-600">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Generating PDF...</span>
              </div>
            )}
            
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
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
