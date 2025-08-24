import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TransactionReviewModal from '../components/TransactionReviewModal';

// Mock the API
jest.mock('../services/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  __esModule: true,
  default: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

const mockTransactions = [
  {
    id: '1',
    amount: '1500.00',
    description: 'GCash Cash In',
    transaction_type: 'income',
    category: 'cash_in',
    counterparty: 'Bank Transfer',
    reference_number: 'GCH123456',
    date: '2025-08-22T10:00:00Z',
    source_platform: 'GCash'
  },
  {
    id: '2',
    amount: '250.00',
    description: 'Grocery Store Payment',
    transaction_type: 'expense',
    category: 'food',
    counterparty: 'SM Supermarket',
    reference_number: 'GCH789012',
    date: '2025-08-22T14:30:00Z',
    source_platform: 'GCash'
  }
];

const mockFileUpload = {
  id: 'test-upload-id',
  filename: 'mock_gcash_mobile.pdf',
  processing_status: 'processed',
  uploaded_at: '2025-08-22T09:00:00Z'
};

describe('TransactionReviewModal', () => {
  const mockProps = {
    uploadId: 'test-upload-id',
    isOpen: true,
    onClose: jest.fn(),
    onApprove: jest.fn(),
  };

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });

  test('renders modal when open', async () => {
    const { api } = require('../services/api');
    api.get.mockResolvedValueOnce({
      data: {
        file_upload: mockFileUpload,
        transactions: mockTransactions,
        count: 2
      }
    });

    render(<TransactionReviewModal {...mockProps} />);

    expect(screen.getByText('Review Extracted Transactions')).toBeInTheDocument();
  });

  test('loads and displays transactions', async () => {
    const { api } = require('../services/api');
    api.get.mockResolvedValueOnce({
      data: {
        file_upload: mockFileUpload,
        transactions: mockTransactions,
        count: 2
      }
    });

    render(<TransactionReviewModal {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('GCash Cash In')).toBeInTheDocument();
      expect(screen.getByText('Grocery Store Payment')).toBeInTheDocument();
    });
  });

  test('allows rejecting transactions', async () => {
    const { api } = require('../services/api');
    api.get.mockResolvedValueOnce({
      data: {
        file_upload: mockFileUpload,
        transactions: mockTransactions,
        count: 2
      }
    });

    render(<TransactionReviewModal {...mockProps} />);

    await waitFor(() => {
      const rejectButtons = screen.getAllByTitle('Reject transaction');
      fireEvent.click(rejectButtons[0]);
    });

    expect(screen.getByText('1 approved')).toBeInTheDocument();
    expect(screen.getByText('1 rejected')).toBeInTheDocument();
  });

  test('handles approval process', async () => {
    const { api } = require('../services/api');
    api.get.mockResolvedValueOnce({
      data: {
        file_upload: mockFileUpload,
        transactions: mockTransactions,
        count: 2
      }
    });

    api.post.mockResolvedValueOnce({
      data: {
        approved_count: 2,
        rejected_count: 0
      }
    });

    render(<TransactionReviewModal {...mockProps} />);

    await waitFor(() => {
      const approveButton = screen.getByText('Approve 2 Transactions');
      fireEvent.click(approveButton);
    });

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        '/api/transactions/uploads/test-upload-id/approve/',
        expect.objectContaining({
          transactions: expect.arrayContaining([
            expect.objectContaining({ id: '1' }),
            expect.objectContaining({ id: '2' })
          ]),
          rejected_transaction_ids: []
        })
      );
    });
  });
});

export default {
  mockTransactions,
  mockFileUpload
};
