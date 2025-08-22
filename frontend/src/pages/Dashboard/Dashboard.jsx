import { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  CreditCard, 
  TrendingUp, 
  DollarSign,
  Calendar,
  Activity,
  Plus,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { formatCurrency, formatDate } from '../../services/api';
import { useDashboard } from '../../hooks/useAuth';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Dashboard = () => {
  const { user } = useAuth();
  const { data: dashboardData, isLoading, error } = useDashboard();

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
          <h3 className="text-lg font-medium text-white mb-2">Failed to load dashboard</h3>
          <p className="text-gray-400">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.statistics || {};
  const recentUploads = dashboardData?.recent_uploads || [];
  const recentTransactions = dashboardData?.recent_transactions || [];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-gray-400 mt-1">
            Here's what's happening with your financial data
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link to="/upload" className="btn-primary inline-flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            Upload Files
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="stat-card">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <Upload className="w-6 h-6 text-white" />
            </div>
            <div className="ml-4">
              <div className="stat-value">{stats.file_uploads || 0}</div>
              <div className="stat-label">Files Uploaded</div>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <CreditCard className="w-6 h-6 text-white" />
            </div>
            <div className="ml-4">
              <div className="stat-value">{stats.transactions || 0}</div>
              <div className="stat-label">Transactions</div>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div className="ml-4">
              <div className="stat-value">{stats.reports || 0}</div>
              <div className="stat-label">Reports Generated</div>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div className="ml-4">
              <div className="stat-value">85%</div>
              <div className="stat-label">AI Accuracy</div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-white">Quick Actions</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              to="/upload"
              className="flex items-center p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
            >
              <Upload className="w-8 h-8 text-blue-400 mr-3" />
              <div>
                <div className="font-medium text-white">Upload Files</div>
                <div className="text-sm text-gray-400">Add new documents</div>
              </div>
            </Link>

            <Link
              to="/transactions"
              className="flex items-center p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
            >
              <CreditCard className="w-8 h-8 text-green-400 mr-3" />
              <div>
                <div className="font-medium text-white">View Transactions</div>
                <div className="text-sm text-gray-400">Manage your data</div>
              </div>
            </Link>

            <Link
              to="/reports"
              className="flex items-center p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
            >
              <FileText className="w-8 h-8 text-purple-400 mr-3" />
              <div>
                <div className="font-medium text-white">Generate Report</div>
                <div className="text-sm text-gray-400">Create income proof</div>
              </div>
            </Link>

            <Link
              to="/profile"
              className="flex items-center p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
            >
              <Activity className="w-8 h-8 text-orange-400 mr-3" />
              <div>
                <div className="font-medium text-white">Profile Settings</div>
                <div className="text-sm text-gray-400">Update your info</div>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Uploads */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Recent Uploads</h2>
            <Link to="/upload" className="text-purple-400 hover:text-purple-300 text-sm">
              View all
            </Link>
          </div>
          <div className="card-body">
            {recentUploads.length > 0 ? (
              <div className="space-y-3">
                {recentUploads.map((upload) => (
                  <div key={upload.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                        <Upload className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <div className="font-medium text-white text-sm">
                          {upload.original_filename}
                        </div>
                        <div className="text-xs text-gray-400">
                          {formatDate(upload.created_at)}
                        </div>
                      </div>
                    </div>
                    <div className={`badge ${
                      upload.processing_status === 'processed' ? 'badge-success' :
                      upload.processing_status === 'processing' ? 'badge-warning' :
                      upload.processing_status === 'failed' ? 'badge-danger' :
                      'badge-info'
                    }`}>
                      {upload.processing_status}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Upload className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                <p className="text-gray-400">No files uploaded yet</p>
                <Link to="/upload" className="text-purple-400 hover:text-purple-300 text-sm">
                  Upload your first file
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Recent Transactions</h2>
            <Link to="/transactions" className="text-purple-400 hover:text-purple-300 text-sm">
              View all
            </Link>
          </div>
          <div className="card-body">
            {recentTransactions.length > 0 ? (
              <div className="space-y-3">
                {recentTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center mr-3 ${
                        transaction.transaction_type === 'income' ? 'bg-green-500' : 'bg-red-500'
                      }`}>
                        <DollarSign className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <div className="font-medium text-white text-sm">
                          {transaction.description}
                        </div>
                        <div className="text-xs text-gray-400">
                          {formatDate(transaction.date)}
                        </div>
                      </div>
                    </div>
                    <div className={`font-medium ${
                      transaction.transaction_type === 'income' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {transaction.transaction_type === 'income' ? '+' : '-'}
                      {formatCurrency(transaction.amount)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CreditCard className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                <p className="text-gray-400">No transactions yet</p>
                <Link to="/upload" className="text-purple-400 hover:text-purple-300 text-sm">
                  Upload files to see transactions
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
