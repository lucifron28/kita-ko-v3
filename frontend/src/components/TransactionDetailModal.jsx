import React from 'react';
import { X, Calendar, DollarSign, Tag, User, FileText, CreditCard } from 'lucide-react';
import { formatCurrency, formatDate } from '../services/api';

const TransactionDetailModal = ({ isOpen, onClose, transaction }) => {
  if (!isOpen || !transaction) return null;

  const getTransactionTypeColor = (type) => {
    switch (type) {
      case 'income':
        return 'bg-green-100 text-green-800';
      case 'expense':
        return 'bg-red-100 text-red-800';
      case 'transfer_in':
        return 'bg-blue-100 text-blue-800';
      case 'transfer_out':
        return 'bg-orange-100 text-orange-800';
      case 'fee':
        return 'bg-purple-100 text-purple-800';
      case 'refund':
        return 'bg-teal-100 text-teal-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'food':
        return 'bg-yellow-100 text-yellow-800';
      case 'transportation':
        return 'bg-blue-100 text-blue-800';
      case 'utilities':
        return 'bg-orange-100 text-orange-800';
      case 'healthcare':
        return 'bg-red-100 text-red-800';
      case 'entertainment':
        return 'bg-purple-100 text-purple-800';
      case 'shopping':
        return 'bg-pink-100 text-pink-800';
      case 'salary':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">Transaction Details</h2>
              <p className="text-purple-100 mt-1">
                {formatDate(transaction.date)}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-300 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 bg-gray-800 text-white max-h-96 overflow-y-auto">
          <div className="space-y-6">
            {/* Amount and Type */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <DollarSign className="w-8 h-8 text-green-400" />
                <div>
                  <p className="text-2xl font-bold text-white">
                    {formatCurrency(transaction.amount)}
                  </p>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTransactionTypeColor(transaction.transaction_type)}`}>
                    {transaction.transaction_type.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-gray-400">
                <FileText className="w-4 h-4" />
                <span className="text-sm font-medium">Description</span>
              </div>
              <p className="text-white font-medium">{transaction.description}</p>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Category */}
              {transaction.category && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-gray-400">
                    <Tag className="w-4 h-4" />
                    <span className="text-sm font-medium">Category</span>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(transaction.category)}`}>
                    {transaction.category.replace('_', ' ')}
                  </span>
                </div>
              )}

              {/* Date */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-gray-400">
                  <Calendar className="w-4 h-4" />
                  <span className="text-sm font-medium">Date</span>
                </div>
                <p className="text-white">{formatDate(transaction.date)}</p>
              </div>

              {/* Counterparty */}
              {transaction.counterparty && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-gray-400">
                    <User className="w-4 h-4" />
                    <span className="text-sm font-medium">Counterparty</span>
                  </div>
                  <p className="text-white">{transaction.counterparty}</p>
                </div>
              )}

              {/* Source Platform */}
              {transaction.source_platform && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-gray-400">
                    <CreditCard className="w-4 h-4" />
                    <span className="text-sm font-medium">Source</span>
                  </div>
                  <p className="text-white">{transaction.source_platform}</p>
                </div>
              )}

              {/* Reference Number */}
              {transaction.reference_number && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-gray-400">
                    <FileText className="w-4 h-4" />
                    <span className="text-sm font-medium">Reference</span>
                  </div>
                  <p className="text-white font-mono text-sm">{transaction.reference_number}</p>
                </div>
              )}
            </div>

            {/* AI Information */}
            {transaction.ai_categorized && (
              <div className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-2 text-purple-400 mb-2">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
                  </svg>
                  <span className="text-sm font-medium">AI Analysis</span>
                </div>
                <p className="text-gray-300 text-sm">
                  Confidence: <span className="capitalize">{transaction.ai_confidence}</span>
                </p>
                {transaction.ai_reasoning && (
                  <p className="text-gray-300 text-sm mt-1">{transaction.ai_reasoning}</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-700 px-6 py-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default TransactionDetailModal;
