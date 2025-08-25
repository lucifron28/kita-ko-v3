import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Briefcase, 
  CreditCard,
  Building,
  Save,
  Lock,
  Eye,
  EyeOff
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useProfile } from '../../hooks/useAuth';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

// Validation schemas
const profileSchema = yup.object({
  first_name: yup.string().required('First name is required'),
  last_name: yup.string().required('Last name is required'),
  middle_name: yup.string(),
  phone_number: yup.string(),
  address_line_1: yup.string(),
  address_line_2: yup.string(),
  city: yup.string(),
  province: yup.string(),
  postal_code: yup.string(),
  occupation_description: yup.string(),
});

const passwordSchema = yup.object({
  old_password: yup.string().required('Current password is required'),
  new_password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    )
    .required('New password is required'),
  new_password_confirm: yup
    .string()
    .oneOf([yup.ref('new_password')], 'Passwords must match')
    .required('Please confirm your password'),
});

const Profile = () => {
  const { updateProfile, changePassword } = useAuth();
  const { data: user, isLoading } = useProfile();
  const [activeTab, setActiveTab] = useState('profile');
  const [showPasswords, setShowPasswords] = useState({
    old: false,
    new: false,
    confirm: false,
  });

  // Profile form
  const profileForm = useForm({
    resolver: yupResolver(profileSchema),
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      middle_name: user?.middle_name || '',
      phone_number: user?.phone_number || '',
      address_line_1: user?.address_line_1 || '',
      address_line_2: user?.address_line_2 || '',
      city: user?.city || '',
      province: user?.province || '',
      postal_code: user?.postal_code || '',
      occupation_description: user?.occupation_description || '',
    },
  });

  // Password form
  const passwordForm = useForm({
    resolver: yupResolver(passwordSchema),
  });

  const onProfileSubmit = async (data) => {
    await updateProfile(data);
  };

  const onPasswordSubmit = async (data) => {
    const result = await changePassword(data);
    if (result.success) {
      passwordForm.reset();
    }
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const tabs = [
    { id: 'profile', label: 'Profile Information', icon: User },
    { id: 'financial', label: 'Financial Information', icon: CreditCard },
    { id: 'security', label: 'Security', icon: Lock },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Profile Settings</h1>
        <p className="text-gray-400 mt-1">
          Manage your account information and preferences
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Profile Information Tab */}
      {activeTab === 'profile' && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-white">Personal Information</h2>
          </div>
          <div className="card-body">
            <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-6">
              {/* Basic Information */}
              <div>
                <h3 className="text-md font-medium text-white mb-4">Basic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="form-group">
                    <label className="form-label">First Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        className={`input-field-with-icon ${profileForm.formState.errors.first_name ? 'border-red-500' : ''}`}
                        {...profileForm.register('first_name')}
                      />
                    </div>
                    {profileForm.formState.errors.first_name && (
                      <p className="form-error">{profileForm.formState.errors.first_name.message}</p>
                    )}
                  </div>

                  <div className="form-group">
                    <label className="form-label">Middle Name</label>
                    <input
                      type="text"
                      className="input-field"
                      {...profileForm.register('middle_name')}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Last Name</label>
                    <input
                      type="text"
                      className={`input-field ${profileForm.formState.errors.last_name ? 'border-red-500' : ''}`}
                      {...profileForm.register('last_name')}
                    />
                    {profileForm.formState.errors.last_name && (
                      <p className="form-error">{profileForm.formState.errors.last_name.message}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div>
                <h3 className="text-md font-medium text-white mb-4">Contact Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="form-group">
                    <label className="form-label">Email Address</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="email"
                        value={user?.email || ''}
                        disabled
                        className="input-field-with-icon opacity-50 cursor-not-allowed"
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Phone Number</label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="tel"
                        placeholder="+63 9XX XXX XXXX"
                        className="input-field-with-icon"
                        {...profileForm.register('phone_number')}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Address Information */}
              <div>
                <h3 className="text-md font-medium text-white mb-4">Address Information</h3>
                <div className="space-y-4">
                  <div className="form-group">
                    <label className="form-label">Address Line 1</label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Street address, building, house number"
                        className="input-field-with-icon"
                        {...profileForm.register('address_line_1')}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Address Line 2 (Optional)</label>
                    <input
                      type="text"
                      placeholder="Apartment, suite, unit, building, floor, etc."
                      className="input-field"
                      {...profileForm.register('address_line_2')}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="form-group">
                      <label className="form-label">City</label>
                      <input
                        type="text"
                        className="input-field"
                        {...profileForm.register('city')}
                      />
                    </div>

                    <div className="form-group">
                      <label className="form-label">Province</label>
                      <input
                        type="text"
                        className="input-field"
                        {...profileForm.register('province')}
                      />
                    </div>

                    <div className="form-group">
                      <label className="form-label">Postal Code</label>
                      <input
                        type="text"
                        className="input-field"
                        {...profileForm.register('postal_code')}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Occupation Information */}
              <div>
                <h3 className="text-md font-medium text-white mb-4">Occupation Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="form-group">
                    <label className="form-label">Primary Occupation</label>
                    <div className="relative">
                      <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        value={user?.primary_occupation || ''}
                        disabled
                        className="input-field-with-icon opacity-50 cursor-not-allowed capitalize"
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">Contact support to change occupation</p>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Occupation Description</label>
                    <textarea
                      rows={3}
                      placeholder="Describe your work in detail..."
                      className="input-field resize-none"
                      {...profileForm.register('occupation_description')}
                    />
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={profileForm.formState.isSubmitting}
                  className="btn-primary inline-flex items-center"
                >
                  {profileForm.formState.isSubmitting ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Financial Information Tab */}
      {activeTab === 'financial' && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-white">Financial Information</h2>
          </div>
          <div className="card-body">
            <div className="space-y-6">
              {/* E-wallet Services */}
              <div>
                <h3 className="text-md font-medium text-white mb-4">E-wallet Services</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { key: 'has_gcash', label: 'GCash' },
                    { key: 'has_paymaya', label: 'PayMaya' },
                    { key: 'has_grabpay', label: 'GrabPay' },
                    { key: 'has_coins_ph', label: 'Coins.ph' },
                  ].map((service) => (
                    <div key={service.key} className="flex items-center">
                      <input
                        type="checkbox"
                        id={service.key}
                        checked={user?.profile?.[service.key] || false}
                        className="mr-2"
                        readOnly
                      />
                      <label htmlFor={service.key} className="text-sm text-gray-300">
                        {service.label}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Banking Information */}
              <div>
                <h3 className="text-md font-medium text-white mb-4">Banking Information</h3>
                <div className="space-y-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="has_bank_account"
                      checked={user?.profile?.has_bank_account || false}
                      className="mr-2"
                      readOnly
                    />
                    <label htmlFor="has_bank_account" className="text-sm text-gray-300">
                      I have a bank account
                    </label>
                  </div>

                  {user?.profile?.bank_names && (
                    <div className="form-group">
                      <label className="form-label">Bank Names</label>
                      <input
                        type="text"
                        value={user.profile.bank_names}
                        disabled
                        className="input-field opacity-50 cursor-not-allowed"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Business Information */}
              {user?.profile?.business_name && (
                <div>
                  <h3 className="text-md font-medium text-white mb-4">Business Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="form-group">
                      <label className="form-label">Business Name</label>
                      <div className="relative">
                        <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="text"
                          value={user.profile.business_name}
                          disabled
                          className="input-field pl-10 opacity-50 cursor-not-allowed"
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Business Type</label>
                      <input
                        type="text"
                        value={user.profile.business_type || ''}
                        disabled
                        className="input-field opacity-50 cursor-not-allowed"
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-blue-900/50 border border-blue-500 rounded-lg p-4">
                <div className="flex items-start">
                  <CreditCard className="w-5 h-5 text-blue-400 mr-2 mt-0.5" />
                  <div className="text-sm">
                    <p className="text-blue-400 font-medium mb-1">Financial Information</p>
                    <p className="text-blue-300">
                      This information is used to better categorize your transactions and generate more accurate reports. 
                      Contact support to update financial service preferences.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-white">Security Settings</h2>
          </div>
          <div className="card-body">
            <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-6">
              <div>
                <h3 className="text-md font-medium text-white mb-4">Change Password</h3>
                
                <div className="space-y-4">
                  {/* Current Password */}
                  <div className="form-group">
                    <label className="form-label">Current Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type={showPasswords.old ? 'text' : 'password'}
                        className={`input-field-with-icons ${passwordForm.formState.errors.old_password ? 'border-red-500' : ''}`}
                        {...passwordForm.register('old_password')}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        onClick={() => togglePasswordVisibility('old')}
                      >
                        {showPasswords.old ? (
                          <EyeOff className="h-4 w-4 text-gray-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {passwordForm.formState.errors.old_password && (
                      <p className="form-error">{passwordForm.formState.errors.old_password.message}</p>
                    )}
                  </div>

                  {/* New Password */}
                  <div className="form-group">
                    <label className="form-label">New Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type={showPasswords.new ? 'text' : 'password'}
                        className={`input-field-with-icons ${passwordForm.formState.errors.new_password ? 'border-red-500' : ''}`}
                        {...passwordForm.register('new_password')}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        onClick={() => togglePasswordVisibility('new')}
                      >
                        {showPasswords.new ? (
                          <EyeOff className="h-4 w-4 text-gray-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {passwordForm.formState.errors.new_password && (
                      <p className="form-error">{passwordForm.formState.errors.new_password.message}</p>
                    )}
                  </div>

                  {/* Confirm New Password */}
                  <div className="form-group">
                    <label className="form-label">Confirm New Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type={showPasswords.confirm ? 'text' : 'password'}
                        className={`input-field-with-icons ${passwordForm.formState.errors.new_password_confirm ? 'border-red-500' : ''}`}
                        {...passwordForm.register('new_password_confirm')}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        onClick={() => togglePasswordVisibility('confirm')}
                      >
                        {showPasswords.confirm ? (
                          <EyeOff className="h-4 w-4 text-gray-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {passwordForm.formState.errors.new_password_confirm && (
                      <p className="form-error">{passwordForm.formState.errors.new_password_confirm.message}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={passwordForm.formState.isSubmitting}
                  className="btn-primary inline-flex items-center"
                >
                  {passwordForm.formState.isSubmitting ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Updating...
                    </>
                  ) : (
                    <>
                      <Lock className="w-4 h-4 mr-2" />
                      Update Password
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Security Info */}
            <div className="mt-6 bg-green-900/50 border border-green-500 rounded-lg p-4">
              <div className="flex items-start">
                <Lock className="w-5 h-5 text-green-400 mr-2 mt-0.5" />
                <div className="text-sm">
                  <p className="text-green-400 font-medium mb-1">Security Best Practices</p>
                  <ul className="text-green-300 space-y-1">
                    <li>• Use a strong, unique password</li>
                    <li>• Include uppercase, lowercase, numbers, and symbols</li>
                    <li>• Don't reuse passwords from other accounts</li>
                    <li>• Change your password regularly</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
