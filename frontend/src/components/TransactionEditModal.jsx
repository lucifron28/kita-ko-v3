import React, { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import toast from 'react-hot-toast';

const TransactionEditModal = ({ isOpen, onClose, transaction, onSave }) => {
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    transaction_type: '',
    category: '',
    counterparty: '',
    reference_number: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (transaction) {
      setFormData({
        amount: transaction.amount || '',
        description: transaction.description || '',
        transaction_type: transaction.transaction_type || '',
        category: transaction.category || '',
        counterparty: transaction.counterparty || '',
        reference_number: transaction.reference_number || ''
      });
    }
  }, [transaction]);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await onSave(transaction.id, formData);
      toast.success('Transaction updated successfully');
      onClose();
    } catch (error) {
      console.error('Failed to update transaction:', error);
      toast.error('Failed to update transaction');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !transaction) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">Edit Transaction</h2>
              <p className="text-purple-100 mt-1">
                Modify transaction details
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
        <form onSubmit={handleSubmit} className="p-6 bg-gray-800 text-white">
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {/* Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Amount</label>
              <input
                type="number"
                step="0.01"
                value={formData.amount}
                onChange={(e) => handleChange('amount', e.target.value)}
                className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            {/* Transaction Type */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Transaction Type</label>
              <select
                value={formData.transaction_type}
                onChange={(e) => handleChange('transaction_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              >
                <option value="">Select type</option>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
                <option value="transfer_in">Transfer In</option>
                <option value="transfer_out">Transfer Out</option>
                <option value="fee">Fee</option>
                <option value="refund">Refund</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
              <select
                value={formData.category}
                onChange={(e) => handleChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Select category</option>
                {/* Income categories */}
                <optgroup label="Income">
                  <option value="salary">Salary</option>
                  <option value="freelance">Freelance Work</option>
                  <option value="business_income">Business Income</option>
                  <option value="commission">Commission</option>
                  <option value="tips">Tips</option>
                  <option value="rental_income">Rental Income</option>
                  <option value="investment_income">Investment Income</option>
                </optgroup>
                {/* Expense categories */}
                <optgroup label="Expenses">
                  <option value="food">Food & Dining</option>
                  <option value="transportation">Transportation</option>
                  <option value="utilities">Utilities</option>
                  <option value="rent">Rent</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="education">Education</option>
                  <option value="entertainment">Entertainment</option>
                  <option value="shopping">Shopping</option>
                  <option value="insurance">Insurance</option>
                </optgroup>
                {/* Transfer categories */}
                <optgroup label="Transfers">
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="ewallet_transfer">E-wallet Transfer</option>
                  <option value="cash_in">Cash In</option>
                  <option value="cash_out">Cash Out</option>
                </optgroup>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Counterparty */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Counterparty (Optional)</label>
              <input
                type="text"
                value={formData.counterparty}
                onChange={(e) => handleChange('counterparty', e.target.value)}
                className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Who was this transaction with?"
              />
            </div>

            {/* Reference Number */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Reference Number (Optional)</label>
              <input
                type="text"
                value={formData.reference_number}
                onChange={(e) => handleChange('reference_number', e.target.value)}
                className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Transaction reference number"
              />
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-600">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
              <Save className="w-4 h-4" />
              <span>Save Changes</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TransactionEditModal;
