import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  File, 
  X, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  FileText,
  Image,
  FileSpreadsheet
} from 'lucide-react';
import { transactionAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const FileUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending',
      progress: 0,
      fileType: 'bank_statement',
      source: 'other',
      description: '',
    }));
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const removeFile = (id) => {
    setFiles(prev => prev.filter(file => file.id !== id));
  };

  const updateFileMetadata = (id, field, value) => {
    setFiles(prev => prev.map(file => 
      file.id === id ? { ...file, [field]: value } : file
    ));
  };

  const uploadFile = async (fileData) => {
    const formData = new FormData();
    formData.append('file', fileData.file);
    formData.append('file_type', fileData.fileType);
    formData.append('source', fileData.source);
    formData.append('description', fileData.description);

    try {
      const response = await transactionAPI.uploadFile(formData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Upload failed' 
      };
    }
  };

  const processFile = async (uploadId) => {
    try {
      await transactionAPI.processUpload(uploadId);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Processing failed' 
      };
    }
  };

  const handleUploadAll = async () => {
    if (files.length === 0) return;

    setUploading(true);
    const results = [];

    for (const fileData of files) {
      if (fileData.status !== 'pending') continue;

      // Update status to uploading
      setFiles(prev => prev.map(f => 
        f.id === fileData.id ? { ...f, status: 'uploading', progress: 0 } : f
      ));

      // Upload file
      const uploadResult = await uploadFile(fileData);
      
      if (uploadResult.success) {
        // Update status to processing
        setFiles(prev => prev.map(f => 
          f.id === fileData.id ? { 
            ...f, 
            status: 'processing', 
            progress: 50,
            uploadId: uploadResult.data.file_upload.id 
          } : f
        ));

        // Process file
        const processResult = await processFile(uploadResult.data.file_upload.id);
        
        if (processResult.success) {
          setFiles(prev => prev.map(f => 
            f.id === fileData.id ? { ...f, status: 'completed', progress: 100 } : f
          ));
          results.push({ success: true, filename: fileData.file.name });
        } else {
          setFiles(prev => prev.map(f => 
            f.id === fileData.id ? { 
              ...f, 
              status: 'error', 
              error: processResult.error 
            } : f
          ));
          results.push({ success: false, filename: fileData.file.name, error: processResult.error });
        }
      } else {
        setFiles(prev => prev.map(f => 
          f.id === fileData.id ? { 
            ...f, 
            status: 'error', 
            error: uploadResult.error 
          } : f
        ));
        results.push({ success: false, filename: fileData.file.name, error: uploadResult.error });
      }
    }

    setUploading(false);

    // Show results
    const successful = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;

    if (successful > 0) {
      toast.success(`${successful} file(s) uploaded and processed successfully!`);
    }
    if (failed > 0) {
      toast.error(`${failed} file(s) failed to upload or process.`);
    }
  };

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    switch (ext) {
      case 'csv':
      case 'xlsx':
      case 'xls':
        return <FileSpreadsheet className="w-8 h-8 text-green-400" />;
      case 'pdf':
        return <FileText className="w-8 h-8 text-red-400" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
        return <Image className="w-8 h-8 text-blue-400" />;
      default:
        return <File className="w-8 h-8 text-gray-400" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'uploading':
      case 'processing':
        return <LoadingSpinner size="sm" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Upload Financial Documents</h1>
        <p className="text-gray-400 mt-1">
          Upload your bank statements, e-wallet records, or receipts to extract transaction data
        </p>
      </div>

      {/* Upload Area */}
      <div className="card">
        <div className="card-body">
          <div
            {...getRootProps()}
            className={`upload-area ${isDragActive ? 'dragover' : ''}`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-purple-400 font-medium">Drop the files here...</p>
            ) : (
              <div className="text-center">
                <p className="text-white font-medium mb-2">
                  Drag & drop files here, or click to select
                </p>
                <p className="text-gray-400 text-sm">
                  Supports CSV, Excel, PDF, and image files (max 50MB each)
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">
              Files to Upload ({files.length})
            </h2>
            <button
              onClick={handleUploadAll}
              disabled={uploading || files.every(f => f.status !== 'pending')}
              className="btn-primary"
            >
              {uploading ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Processing...
                </>
              ) : (
                'Upload All'
              )}
            </button>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {files.map((fileData) => (
                <div key={fileData.id} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center">
                      {getFileIcon(fileData.file.name)}
                      <div className="ml-3">
                        <div className="font-medium text-white">
                          {fileData.file.name}
                        </div>
                        <div className="text-sm text-gray-400">
                          {(fileData.file.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(fileData.status)}
                      {fileData.status === 'pending' && (
                        <button
                          onClick={() => removeFile(fileData.id)}
                          className="p-1 text-gray-400 hover:text-red-400"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {(fileData.status === 'uploading' || fileData.status === 'processing') && (
                    <div className="mb-3">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ width: `${fileData.progress}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        {fileData.status === 'uploading' ? 'Uploading...' : 'Processing...'}
                      </div>
                    </div>
                  )}

                  {/* Error Message */}
                  {fileData.status === 'error' && (
                    <div className="mb-3 p-2 bg-red-900/50 border border-red-500 rounded text-red-400 text-sm">
                      {fileData.error}
                    </div>
                  )}

                  {/* Metadata Form */}
                  {fileData.status === 'pending' && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                          File Type
                        </label>
                        <select
                          value={fileData.fileType}
                          onChange={(e) => updateFileMetadata(fileData.id, 'fileType', e.target.value)}
                          className="input-field text-sm"
                        >
                          <option value="bank_statement">Bank Statement</option>
                          <option value="ewallet_statement">E-wallet Statement</option>
                          <option value="receipt">Receipt</option>
                          <option value="invoice">Invoice</option>
                          <option value="payslip">Payslip</option>
                          <option value="other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                          Source
                        </label>
                        <select
                          value={fileData.source}
                          onChange={(e) => updateFileMetadata(fileData.id, 'source', e.target.value)}
                          className="input-field text-sm"
                        >
                          <option value="gcash">GCash</option>
                          <option value="paymaya">PayMaya</option>
                          <option value="grabpay">GrabPay</option>
                          <option value="coins_ph">Coins.ph</option>
                          <option value="bpi">BPI</option>
                          <option value="bdo">BDO</option>
                          <option value="metrobank">Metrobank</option>
                          <option value="unionbank">UnionBank</option>
                          <option value="other_bank">Other Bank</option>
                          <option value="other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                          Description (Optional)
                        </label>
                        <input
                          type="text"
                          value={fileData.description}
                          onChange={(e) => updateFileMetadata(fileData.id, 'description', e.target.value)}
                          placeholder="Brief description"
                          className="input-field text-sm"
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-white">Supported File Types</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <FileSpreadsheet className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <div className="font-medium text-white">CSV Files</div>
              <div className="text-sm text-gray-400">Comma-separated values</div>
            </div>
            <div className="text-center">
              <FileSpreadsheet className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <div className="font-medium text-white">Excel Files</div>
              <div className="text-sm text-gray-400">.xlsx, .xls formats</div>
            </div>
            <div className="text-center">
              <FileText className="w-8 h-8 text-red-400 mx-auto mb-2" />
              <div className="font-medium text-white">PDF Files</div>
              <div className="text-sm text-gray-400">Bank statements</div>
            </div>
            <div className="text-center">
              <Image className="w-8 h-8 text-blue-400 mx-auto mb-2" />
              <div className="font-medium text-white">Images</div>
              <div className="text-sm text-gray-400">JPG, PNG receipts</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
