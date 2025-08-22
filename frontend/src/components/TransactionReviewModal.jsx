import React, { useState, useEffect } from 'react';
import {
  X,
  Check,
  Trash2,
  Edit3,
  DollarSign,
  Calendar,
  Tag,
  User,
  AlertCircle,
  Eye,
  EyeOff
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';

const TransactionReviewModal = ({ uploadId, isOpen, onClose, onApprove }) => {
  const [loading, setLoading] = useState(false);
  const [fileUpload, setFileUpload] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [rejectedTransactions, setRejectedTransactions] = useState(new Set());
  const [showAllFields, setShowAllFields] = useState(false);

  useEffect(() => {
    if (isOpen && uploadId) {
      fetchTransactions();
    }
  }, [isOpen, uploadId]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/transactions/uploads/${uploadId}/transactions/`);
      setFileUpload(response.data.file_upload);
      setTransactions(response.data.transactions);
    } catch (error) {
      toast.error('Failed to load extracted transactions');
      console.error('Error fetching transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-PH', {
      style: 'currency',
      currency: 'PHP'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-PH', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTransactionTypeColor = (type) => {
    const colors = {
      'income': 'text-green-600 bg-green-50',
      'expense': 'text-red-600 bg-red-50',
      'transfer_in': 'text-blue-600 bg-blue-50',
      'transfer_out': 'text-orange-600 bg-orange-50',
      'fee': 'text-purple-600 bg-purple-50',
      'refund': 'text-teal-600 bg-teal-50',
      'other': 'text-gray-600 bg-gray-50'
    };
    return colors[type] || colors['other'];
  };

  const handleRejectTransaction = (transactionId) => {
    setRejectedTransactions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(transactionId)) {
        newSet.delete(transactionId);
      } else {
        newSet.add(transactionId);
      }
      return newSet;
    });
  };

  const handleEditTransaction = (transaction) => {
    setEditingTransaction({
      id: transaction.id,
      amount: transaction.amount,
      description: transaction.description,
      transaction_type: transaction.transaction_type,
      category: transaction.category,
      counterparty: transaction.counterparty || ''
    });
  };

  const saveTransactionEdit = () => {
    setTransactions(prev => prev.map(t => 
      t.id === editingTransaction.id ? { ...t, ...editingTransaction } : t
    ));
    setEditingTransaction(null);
  };

  const handleApprove = async () => {
    try {
      setLoading(true);
      
      // Prepare approved transactions (exclude rejected ones)
      const approvedTransactions = transactions
        .filter(t => !rejectedTransactions.has(t.id))
        .map(t => ({
          id: t.id,
          amount: t.amount,
          description: t.description,
          transaction_type: t.transaction_type,
          category: t.category,
          counterparty: t.counterparty
        }));

      const payload = {
        transactions: approvedTransactions,
        rejected_transaction_ids: Array.from(rejectedTransactions)
      };

      const response = await api.post(`/transactions/uploads/${uploadId}/approve/`, payload);
      
      toast.success(`${response.data.approved_count} transactions approved successfully!`);
      if (response.data.rejected_count > 0) {
        toast.info(`${response.data.rejected_count} transactions rejected`);
      }
      
      onApprove();
      onClose();
    } catch (error) {
      toast.error('Failed to approve transactions');
      console.error('Error approving transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Review Extracted Transactions</h2>
              {fileUpload && (
                <p className="text-purple-100 mt-1">
                  From: {fileUpload.filename} • {transactions.length} transactions found
                </p>
              )}
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 bg-gray-800 text-white">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
              <span className="ml-3 text-gray-300">Loading transactions...</span>
            </div>
          ) : (
            <>
              {/* Controls */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setShowAllFields(!showAllFields)}
                    className="flex items-center space-x-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                  >
                    {showAllFields ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    <span className="text-sm">{showAllFields ? 'Hide Details' : 'Show All Details'}</span>
                  </button>
                </div>
                
                <div className="text-sm text-gray-300">
                  <span className="text-green-400 font-medium">
                    {transactions.length - rejectedTransactions.size} approved
                  </span>
                  {rejectedTransactions.size > 0 && (
                    <span className="text-red-400 font-medium ml-3">
                      {rejectedTransactions.size} rejected
                    </span>
                  )}
                </div>
              </div>

              {/* Transactions List */}
              <div className="max-h-96 overflow-y-auto space-y-4">
                {transactions.map((transaction) => {
                  const isRejected = rejectedTransactions.has(transaction.id);
                  const isEditing = editingTransaction && editingTransaction.id === transaction.id;
                  
                  return (
                    <div
                      key={transaction.id}
                      className={`border rounded-lg p-4 transition-all ${
                        isRejected 
                          ? 'bg-red-50 border-red-200 opacity-75' 
                          : 'bg-white border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          {isEditing ? (
                            <div className="space-y-3">
                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
                                  <input
                                    type="number"
                                    step="0.01"
                                    value={editingTransaction.amount}
                                    onChange={(e) => setEditingTransaction(prev => ({
                                      ...prev,
                                      amount: e.target.value
                                    }))}
                                    className="w-full px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                                  <select
                                    value={editingTransaction.transaction_type}
                                    onChange={(e) => setEditingTransaction(prev => ({
                                      ...prev,
                                      transaction_type: e.target.value
                                    }))}
                                    className="w-full px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                  >
                                    <option value="income">Income</option>
                                    <option value="expense">Expense</option>
                                    <option value="transfer_in">Transfer In</option>
                                    <option value="transfer_out">Transfer Out</option>
                                    <option value="fee">Fee</option>
                                    <option value="refund">Refund</option>
                                    <option value="other">Other</option>
                                  </select>
                                </div>
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                <textarea
                                  value={editingTransaction.description}
                                  onChange={(e) => setEditingTransaction(prev => ({
                                    ...prev,
                                    description: e.target.value
                                  }))}
                                  rows="2"
                                  className="w-full px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                              </div>
                              <div className="flex space-x-2">
                                <button
                                  onClick={saveTransactionEdit}
                                  className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                                >
                                  Save
                                </button>
                                <button
                                  onClick={() => setEditingTransaction(null)}
                                  className="px-3 py-1 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTransactionTypeColor(transaction.transaction_type)}`}>
                                    {transaction.transaction_type.replace('_', ' ')}
                                  </span>
                                  <span className="font-semibold text-lg">
                                    {formatCurrency(transaction.amount)}
                                  </span>
                                </div>
                                <div className="text-sm text-gray-500">
                                  {formatDate(transaction.date)}
                                </div>
                              </div>
                              
                              <p className="text-gray-900 font-medium">{transaction.description}</p>
                              
                              {showAllFields && (
                                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 pt-2 border-t border-gray-100">
                                  {transaction.category && (
                                    <div className="flex items-center space-x-2">
                                      <Tag className="w-4 h-4" />
                                      <span>{transaction.category.replace('_', ' ')}</span>
                                    </div>
                                  )}
                                  {transaction.counterparty && (
                                    <div className="flex items-center space-x-2">
                                      <User className="w-4 h-4" />
                                      <span>{transaction.counterparty}</span>
                                    </div>
                                  )}
                                  {transaction.reference_number && (
                                    <div className="flex items-center space-x-2">
                                      <AlertCircle className="w-4 h-4" />
                                      <span>Ref: {transaction.reference_number}</span>
                                    </div>
                                  )}
                                  <div className="flex items-center space-x-2">
                                    <DollarSign className="w-4 h-4" />
                                    <span>{transaction.source_platform || 'Unknown'}</span>
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Action buttons */}
                        <div className="flex items-center space-x-2 ml-4">
                          {!isEditing && (
                            <button
                              onClick={() => handleEditTransaction(transaction)}
                              disabled={isRejected}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                              title="Edit transaction"
                            >
                              <Edit3 className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleRejectTransaction(transaction.id)}
                            className={`p-2 rounded-lg transition-colors ${
                              isRejected
                                ? 'text-green-600 hover:bg-green-50'
                                : 'text-red-600 hover:bg-red-50'
                            }`}
                            title={isRejected ? 'Restore transaction' : 'Reject transaction'}
                          >
                            {isRejected ? <Check className="w-4 h-4" /> : <Trash2 className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  Review and modify the extracted transactions. You can edit details, reject incorrect transactions, and then approve the final set.
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={onClose}
                    disabled={loading}
                    className="px-6 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleApprove}
                    disabled={loading || transactions.length - rejectedTransactions.size === 0}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
                  >
                    {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
                    <span>
                      Approve {transactions.length - rejectedTransactions.size} Transaction{transactions.length - rejectedTransactions.size !== 1 ? 's' : ''}
                    </span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TransactionReviewModal;
