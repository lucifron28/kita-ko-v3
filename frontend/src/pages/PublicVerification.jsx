import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle,
  FileText,
  Calendar,
  User,
  Hash,
  ExternalLink
} from 'lucide-react';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const PublicVerification = () => {
  const { verificationCode } = useParams();
  const [verificationData, setVerificationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchVerificationData();
  }, [verificationCode]);

  const fetchVerificationData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/reports/verify-public/${verificationCode}/`);
      const data = await response.json();
      
      if (response.ok) {
        setVerificationData(data);
      } else {
        setError(data.message || 'Verification failed');
      }
    } catch (err) {
      setError('Unable to verify document at this time');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (statusClass) => {
    switch (statusClass) {
      case 'verified':
        return <CheckCircle className="w-16 h-16 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-16 h-16 text-red-500" />;
      case 'pending':
        return <Clock className="w-16 h-16 text-yellow-500" />;
      case 'not_submitted':
        return <AlertCircle className="w-16 h-16 text-gray-500" />;
      default:
        return <AlertCircle className="w-16 h-16 text-red-500" />;
    }
  };

  const getStatusColor = (statusClass) => {
    switch (statusClass) {
      case 'verified':
        return 'bg-green-50 border-green-200';
      case 'rejected':
        return 'bg-red-50 border-red-200';
      case 'pending':
        return 'bg-yellow-50 border-yellow-200';
      case 'not_submitted':
        return 'bg-gray-50 border-gray-200';
      default:
        return 'bg-red-50 border-red-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Verifying document...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-12 h-12 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">Document Verification</h1>
          </div>
          <p className="text-gray-600">KitaKo Income Report Verification System</p>
        </div>

        {error ? (
          /* Error State */
          <div className="bg-white rounded-lg shadow-lg border border-red-200 p-8 text-center">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-red-800 mb-2">Verification Failed</h2>
            <p className="text-red-600 mb-4">{error}</p>
            <p className="text-sm text-gray-500">
              Please check the verification code and try again, or contact KitaKo support.
            </p>
          </div>
        ) : (
          /* Verification Results */
          <div className={`bg-white rounded-lg shadow-lg border-2 ${getStatusColor(verificationData?.status_class)} p-8`}>
            {/* Status Icon and Title */}
            <div className="text-center mb-8">
              {getStatusIcon(verificationData?.status_class)}
              <h2 className="text-3xl font-bold text-gray-900 mt-4 mb-2">
                {verificationData?.verified ? 'Document Verified' : 'Document Not Verified'}
              </h2>
              <p className="text-lg text-gray-600">{verificationData?.message}</p>
            </div>

            {/* Document Information */}
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-900 border-b pb-2">
                  Document Information
                </h3>
                
                <div className="flex items-start space-x-3">
                  <FileText className="w-5 h-5 text-gray-500 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Document Title</p>
                    <p className="text-gray-600">{verificationData?.document_title}</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <User className="w-5 h-5 text-gray-500 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Report Holder</p>
                    <p className="text-gray-600">{verificationData?.user_email}</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Calendar className="w-5 h-5 text-gray-500 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Created Date</p>
                    <p className="text-gray-600">{verificationData?.created_date}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-900 border-b pb-2">
                  Verification Details
                </h3>
                
                <div className="flex items-start space-x-3">
                  <Hash className="w-5 h-5 text-gray-500 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Verification Code</p>
                    <p className="text-gray-600 font-mono">{verificationData?.verification_code}</p>
                  </div>
                </div>

                {verificationData?.document_hash && (
                  <div className="flex items-start space-x-3">
                    <Hash className="w-5 h-5 text-gray-500 mt-1" />
                    <div>
                      <p className="font-medium text-gray-900">Document Hash</p>
                      <p className="text-gray-600 font-mono text-sm break-all">
                        {verificationData.document_hash}
                      </p>
                    </div>
                  </div>
                )}

                {/* Verification Status Details */}
                {verificationData?.verified_date && (
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-1" />
                    <div>
                      <p className="font-medium text-gray-900">Verified On</p>
                      <p className="text-gray-600">{verificationData.verified_date}</p>
                    </div>
                  </div>
                )}

                {verificationData?.rejected_date && (
                  <div className="flex items-start space-x-3">
                    <XCircle className="w-5 h-5 text-red-500 mt-1" />
                    <div>
                      <p className="font-medium text-gray-900">Rejected On</p>
                      <p className="text-gray-600">{verificationData.rejected_date}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Admin Notes */}
            {verificationData?.admin_notes && (
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Administrator Notes</h4>
                <p className="text-gray-700">{verificationData.admin_notes}</p>
              </div>
            )}

            {/* Legal Notice */}
            <div className="border-t pt-6">
              <div className="bg-blue-50 rounded-lg p-6">
                <div className="flex items-start space-x-3">
                  <Shield className="w-6 h-6 text-blue-600 mt-1" />
                  <div>
                    <h4 className="font-semibold text-blue-900 mb-2">Legal Notice</h4>
                    <p className="text-blue-800 text-sm leading-relaxed">
                      This verification system confirms the authenticity of documents generated by the KitaKo platform. 
                      {verificationData?.verified ? 
                        ' This document has been reviewed and approved by KitaKo administrators.' :
                        ' This document has not been verified or has been rejected by KitaKo administrators.'
                      }
                      {' '}For legal validity, documents may require additional notarization depending on their intended use.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* KitaKo Branding */}
            <div className="text-center mt-8 pt-6 border-t">
              <p className="text-gray-500 text-sm">
                Verified by{' '}
                <a 
                  href="https://kita-ko-2b521254f5f2.herokuapp.com" 
                  className="text-blue-600 hover:text-blue-800 font-medium"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  KitaKo Platform <ExternalLink className="inline w-3 h-3 ml-1" />
                </a>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PublicVerification;
