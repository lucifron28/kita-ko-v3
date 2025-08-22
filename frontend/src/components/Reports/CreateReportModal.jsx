import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { X, Calendar, FileText, Target } from 'lucide-react';
import LoadingSpinner from '../UI/LoadingSpinner';

// Validation schema
const schema = yup.object({
  title: yup.string().required('Title is required'),
  report_type: yup.string().required('Report type is required'),
  date_from: yup.string().required('Start date is required').matches(/^\d{4}-\d{2}-\d{2}$/, 'Please enter a valid date'),
  date_to: yup.string().required('End date is required').matches(/^\d{4}-\d{2}-\d{2}$/, 'Please enter a valid date'),
  purpose: yup.string().required('Purpose is required'),
  purpose_description: yup.string(),
}).test('date-range', 'End date must be after start date', function(values) {
  const { date_from, date_to } = values;
  if (date_from && date_to) {
    return new Date(date_to) > new Date(date_from);
  }
  return true;
});

const CreateReportModal = ({ onClose, onSubmit }) => {
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      report_type: 'custom',
      purpose: 'loan_application',
    },
  });

  const reportType = watch('report_type');
  const purpose = watch('purpose');

  const handleFormSubmit = async (data) => {
    setLoading(true);
    try {
      // Auto-generate title if not provided
      if (!data.title || data.title.trim() === '') {
        data.title = generateTitle();
      }
      
      console.log('Form data being submitted:', data);
      await onSubmit(data);
    } finally {
      setLoading(false);
    }
  };

  const reportTypeOptions = [
    { value: 'monthly', label: 'Monthly Report' },
    { value: 'quarterly', label: 'Quarterly Report' },
    { value: 'annual', label: 'Annual Report' },
    { value: 'custom', label: 'Custom Period' },
  ];

  const purposeOptions = [
    { value: 'loan_application', label: 'Loan Application' },
    { value: 'government_subsidy', label: 'Government Subsidy' },
    { value: 'insurance_application', label: 'Insurance Application' },
    { value: 'rental_application', label: 'Rental Application' },
    { value: 'business_registration', label: 'Business Registration' },
    { value: 'visa_application', label: 'Visa Application' },
    { value: 'other', label: 'Other' },
  ];

  // Auto-generate title based on selections
  const generateTitle = () => {
    const typeLabel = reportTypeOptions.find(opt => opt.value === reportType)?.label || 'Report';
    const purposeLabel = purposeOptions.find(opt => opt.value === purpose)?.label || 'General';
    return `${typeLabel} - ${purposeLabel}`;
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Overlay */}
        <div 
          className="fixed inset-0 transition-opacity bg-black/50 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-gray-800 border border-gray-700 shadow-xl rounded-lg z-10">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <FileText className="w-6 h-6 text-purple-400 mr-2" />
              <h3 className="text-lg font-medium text-white">Create Income Report</h3>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            {/* Title */}
            <div className="form-group">
              <label htmlFor="title" className="form-label">
                Report Title
              </label>
              <input
                id="title"
                type="text"
                placeholder={generateTitle()}
                className={`input-field ${errors.title ? 'border-red-500' : ''}`}
                {...register('title')}
              />
              {errors.title && (
                <p className="form-error">{errors.title.message}</p>
              )}
            </div>

            {/* Report Type */}
            <div className="form-group">
              <label htmlFor="report_type" className="form-label">
                Report Type
              </label>
              <select
                id="report_type"
                className={`input-field ${errors.report_type ? 'border-red-500' : ''}`}
                {...register('report_type')}
              >
                {reportTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {errors.report_type && (
                <p className="form-error">{errors.report_type.message}</p>
              )}
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-4">
              <div className="form-group">
                <label htmlFor="date_from" className="form-label">
                  Start Date
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    id="date_from"
                    type="date"
                    className={`input-field-with-icon ${errors.date_from ? 'border-red-500' : ''}`}
                    {...register('date_from', { valueAsDate: false })}
                  />
                </div>
                {errors.date_from && (
                  <p className="form-error">{errors.date_from.message}</p>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="date_to" className="form-label">
                  End Date
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    id="date_to"
                    type="date"
                    className={`input-field-with-icon ${errors.date_to ? 'border-red-500' : ''}`}
                    {...register('date_to', { valueAsDate: false })}
                  />
                </div>
                {errors.date_to && (
                  <p className="form-error">{errors.date_to.message}</p>
                )}
              </div>
            </div>

            {/* Purpose */}
            <div className="form-group">
              <label htmlFor="purpose" className="form-label">
                Purpose
              </label>
              <div className="relative">
                <Target className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <select
                  id="purpose"
                  className={`input-field-with-icon ${errors.purpose ? 'border-red-500' : ''}`}
                  {...register('purpose')}
                >
                  {purposeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              {errors.purpose && (
                <p className="form-error">{errors.purpose.message}</p>
              )}
            </div>

            {/* Purpose Description */}
            <div className="form-group">
              <label htmlFor="purpose_description" className="form-label">
                Description (Optional)
              </label>
              <textarea
                id="purpose_description"
                rows={3}
                placeholder="Provide additional details about the purpose of this report..."
                className="input-field resize-none"
                {...register('purpose_description')}
              />
            </div>

            {/* Info Box */}
            <div className="bg-blue-900/50 border border-blue-500 rounded-lg p-3">
              <div className="flex items-start">
                <FileText className="w-5 h-5 text-blue-400 mr-2 mt-0.5" />
                <div className="text-sm">
                  <p className="text-blue-400 font-medium mb-1">Report Generation</p>
                  <p className="text-blue-300">
                    Your report will include AI-powered analysis, income breakdown, 
                    and professional formatting suitable for official applications.
                  </p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-3 pt-4 relative z-10">
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="btn-secondary flex-1 relative"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex-1 flex justify-center items-center relative"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Creating...
                  </>
                ) : (
                  'Create Report'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateReportModal;
