import { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Edit, 
  Trash2,
  CreditCard,
  TrendingUp,
  TrendingDown,
  Calendar,
  DollarSign,
  Bot,
  RefreshCw
} from 'lucide-react';
import { transactionAPI, aiAPI, formatCurrency, formatDate } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import TransactionDetailModal from '../../components/TransactionDetailModal';
import TransactionEditModal from '../../components/TransactionEditModal';
import toast from 'react-hot-toast';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    type: '',
    category: '',
    source: '',
    date_from: '',
    date_to: '',
  });
  const [selectedTransactions, setSelectedTransactions] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [aiProcessing, setAiProcessing] = useState(false);
  const [detailModal, setDetailModal] = useState({ isOpen: false, transaction: null });
  const [editModal, setEditModal] = useState({ isOpen: false, transaction: null });
  const [pagination, setPagination] = useState({
    page: 1,
    totalPages: 1,
    totalCount: 0,
  });

  useEffect(() => {
    fetchTransactions();
  }, [filters, pagination.page]);

  // Refresh transactions when component mounts (ensures fresh data after approvals)
  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const params = {
        ...filters,
        page: pagination.page,
      };
      
      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (!params[key]) delete params[key];
      });

      const response = await transactionAPI.getTransactions(params);
      setTransactions(response.data.results || response.data);
      
      if (response.data.count) {
        setPagination(prev => ({
          ...prev,
          totalCount: response.data.count,
          totalPages: Math.ceil(response.data.count / 20),
        }));
      }
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      toast.error('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleSelectTransaction = (transactionId) => {
    setSelectedTransactions(prev => {
      if (prev.includes(transactionId)) {
        return prev.filter(id => id !== transactionId);
      } else {
        return [...prev, transactionId];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedTransactions.length === transactions.length) {
      setSelectedTransactions([]);
    } else {
      setSelectedTransactions(transactions.map(t => t.id));
    }
  };

  const handleAICategorization = async () => {
    if (selectedTransactions.length === 0) {
      toast.error('Please select transactions to categorize');
      return;
    }

    setAiProcessing(true);
    try {
      const response = await aiAPI.categorizeTransactions({
        transaction_ids: selectedTransactions,
      });

      toast.success(`Successfully categorized ${response.data.categorized_count} transactions`);
      fetchTransactions();
      setSelectedTransactions([]);
    } catch (error) {
      console.error('AI categorization failed:', error);
      toast.error('Failed to categorize transactions');
    } finally {
      setAiProcessing(false);
    }
  };

  const handleViewTransaction = (transaction) => {
    setDetailModal({ isOpen: true, transaction });
  };

  const handleEditTransaction = (transaction) => {
    setEditModal({ isOpen: true, transaction });
  };

  const handleSaveTransaction = async (transactionId, updatedData) => {
    await transactionAPI.updateTransaction(transactionId, updatedData);
    fetchTransactions(); // Refresh the list
  };

  const handleDeleteTransaction = async (transaction) => {
    if (window.confirm(`Are you sure you want to delete this transaction: ${transaction.description}?`)) {
      try {
        await transactionAPI.deleteTransaction(transaction.id);
        toast.success('Transaction deleted successfully');
        fetchTransactions(); // Refresh the list
      } catch (error) {
        console.error('Failed to delete transaction:', error);
        toast.error('Failed to delete transaction');
      }
    }
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'income':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'expense':
        return <TrendingDown className="w-4 h-4 text-red-400" />;
      default:
        return <CreditCard className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTransactionTypeColor = (type) => {
    switch (type) {
      case 'income':
        return 'text-green-400';
      case 'expense':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  if (loading && transactions.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Transactions</h1>
          <p className="text-gray-400 mt-1">
            Manage and categorize your financial transactions
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          <button
            onClick={() => fetchTransactions()}
            disabled={loading}
            className="btn-secondary inline-flex items-center"
            title="Refresh transactions"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          
          {selectedTransactions.length > 0 && (
            <button
              onClick={handleAICategorization}
              disabled={aiProcessing}
              className="btn-primary inline-flex items-center"
            >
              {aiProcessing ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <Bot className="w-4 h-4 mr-2" />
                  AI Categorize ({selectedTransactions.length})
                </>
              )}
            </button>
          )}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary inline-flex items-center"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 text-sm text-gray-300">
        <div className="flex items-start space-x-3">
          <div className="text-purple-400 mt-0.5">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <p className="font-medium text-white">📊 All Your Transactions</p>
            <p className="mt-1">
              This shows all your financial transactions, including those extracted from uploaded files. 
              Transactions appear here immediately after file processing, even before you confirm them in the review step.
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="card">
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="form-label">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search transactions..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    className="input-field-with-icon"
                  />
                </div>
              </div>

              <div>
                <label className="form-label">Type</label>
                <select
                  value={filters.type}
                  onChange={(e) => handleFilterChange('type', e.target.value)}
                  className="input-field"
                >
                  <option value="">All Types</option>
                  <option value="income">Income</option>
                  <option value="expense">Expense</option>
                  <option value="transfer_in">Transfer In</option>
                  <option value="transfer_out">Transfer Out</option>
                </select>
              </div>

              <div>
                <label className="form-label">Source</label>
                <select
                  value={filters.source}
                  onChange={(e) => handleFilterChange('source', e.target.value)}
                  className="input-field"
                >
                  <option value="">All Sources</option>
                  <option value="gcash">GCash</option>
                  <option value="paymaya">PayMaya</option>
                  <option value="bpi">BPI</option>
                  <option value="bdo">BDO</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="form-label">Date From</label>
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) => handleFilterChange('date_from', e.target.value)}
                  className="input-field"
                />
              </div>

              <div>
                <label className="form-label">Date To</label>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) => handleFilterChange('date_to', e.target.value)}
                  className="input-field"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => {
                    setFilters({
                      search: '',
                      type: '',
                      category: '',
                      source: '',
                      date_from: '',
                      date_to: '',
                    });
                  }}
                  className="btn-secondary w-full"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Transactions Table */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={selectedTransactions.length === transactions.length && transactions.length > 0}
              onChange={handleSelectAll}
              className="mr-3"
            />
            <h2 className="text-lg font-semibold text-white">
              Transactions ({pagination.totalCount || transactions.length})
            </h2>
          </div>
          {selectedTransactions.length > 0 && (
            <div className="text-sm text-gray-400">
              {selectedTransactions.length} selected
            </div>
          )}
        </div>
        <div className="table-container">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">
                  <input
                    type="checkbox"
                    checked={selectedTransactions.length === transactions.length && transactions.length > 0}
                    onChange={handleSelectAll}
                  />
                </th>
                <th className="table-header-cell">Date</th>
                <th className="table-header-cell">Description</th>
                <th className="table-header-cell">Type</th>
                <th className="table-header-cell">Category</th>
                <th className="table-header-cell">Amount</th>
                <th className="table-header-cell">Source</th>
                <th className="table-header-cell">AI</th>
                <th className="table-header-cell">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {transactions.map((transaction) => (
                <tr key={transaction.id} className="table-row">
                  <td className="table-cell">
                    <input
                      type="checkbox"
                      checked={selectedTransactions.includes(transaction.id)}
                      onChange={() => handleSelectTransaction(transaction.id)}
                    />
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                      {formatDate(transaction.date)}
                    </div>
                  </td>
                  <td className="table-cell">
                    <div className="max-w-xs truncate" title={transaction.description}>
                      {transaction.description}
                    </div>
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center">
                      {getTransactionIcon(transaction.transaction_type)}
                      <span className={`ml-2 capitalize ${getTransactionTypeColor(transaction.transaction_type)}`}>
                        {transaction.transaction_type}
                      </span>
                    </div>
                  </td>
                  <td className="table-cell">
                    <span className="badge badge-info capitalize">
                      {transaction.category || 'Uncategorized'}
                    </span>
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center">
                      <DollarSign className="w-4 h-4 text-gray-400 mr-1" />
                      <span className={getTransactionTypeColor(transaction.transaction_type)}>
                        {formatCurrency(transaction.amount)}
                      </span>
                    </div>
                  </td>
                  <td className="table-cell">
                    <span className="text-gray-400 capitalize">
                      {transaction.source_platform || 'Unknown'}
                    </span>
                  </td>
                  <td className="table-cell">
                    {transaction.ai_categorized ? (
                      <div className="flex items-center">
                        <Bot className="w-4 h-4 text-green-400 mr-1" />
                        <span className="text-green-400 text-xs">
                          {transaction.ai_confidence}
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-500 text-xs">Manual</span>
                    )}
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleViewTransaction(transaction)}
                        className="p-1 text-gray-400 hover:text-blue-400 transition-colors"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleEditTransaction(transaction)}
                        className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
                        title="Edit"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteTransaction(transaction)}
                        className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination.totalPages > 1 && (
          <div className="card-footer flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Showing {((pagination.page - 1) * 20) + 1} to {Math.min(pagination.page * 20, pagination.totalCount)} of {pagination.totalCount} transactions
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={pagination.page === 1}
                className="btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={pagination.page === pagination.totalPages}
                className="btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Empty State */}
      {!loading && transactions.length === 0 && (
        <div className="card">
          <div className="card-body text-center py-12">
            <CreditCard className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No transactions found</h3>
            <p className="text-gray-400 mb-4">
              Upload some financial documents to see your transactions here.
            </p>
            <button
              onClick={() => window.location.href = '/upload'}
              className="btn-primary"
            >
              Upload Files
            </button>
          </div>
        </div>
      )}

      {/* Transaction Detail Modal */}
      <TransactionDetailModal
        isOpen={detailModal.isOpen}
        onClose={() => setDetailModal({ isOpen: false, transaction: null })}
        transaction={detailModal.transaction}
      />

      {/* Transaction Edit Modal */}
      <TransactionEditModal
        isOpen={editModal.isOpen}
        onClose={() => setEditModal({ isOpen: false, transaction: null })}
        transaction={editModal.transaction}
        onSave={handleSaveTransaction}
      />
    </div>
  );
};

export default Transactions;
