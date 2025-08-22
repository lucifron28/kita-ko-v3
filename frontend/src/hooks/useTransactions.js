import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsAPI } from '../services/api';
import toast from 'react-hot-toast';

// Query keys
export const TRANSACTIONS_QUERY_KEYS = {
  transactions: (params) => ['transactions', params],
  transaction: (id) => ['transactions', id],
};

// Fetch transactions with pagination
export const useTransactions = (params = {}) => {
  return useQuery({
    queryKey: TRANSACTIONS_QUERY_KEYS.transactions(params),
    queryFn: () => transactionsAPI.getTransactions(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
    cacheTime: 5 * 60 * 1000, // 5 minutes
    select: (response) => response.data,
  });
};

// Get single transaction
export const useTransaction = (id) => {
  return useQuery({
    queryKey: TRANSACTIONS_QUERY_KEYS.transaction(id),
    queryFn: () => transactionsAPI.getTransaction(id),
    enabled: !!id,
    select: (response) => response.data,
  });
};

// Update transaction mutation
export const useUpdateTransaction = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => transactionsAPI.updateTransaction(id, data),
    onSuccess: (response, variables) => {
      // Update the transaction in cache
      queryClient.setQueryData(
        TRANSACTIONS_QUERY_KEYS.transaction(variables.id),
        response.data
      );
      
      // Invalidate transactions list to refetch
      queryClient.invalidateQueries({
        queryKey: ['transactions']
      });
      
      toast.success('Transaction updated successfully!');
    },
    onError: (error) => {
      console.error('Failed to update transaction:', error);
      toast.error('Failed to update transaction');
    },
  });
};

// Delete transaction mutation
export const useDeleteTransaction = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id) => transactionsAPI.deleteTransaction(id),
    onSuccess: (_, id) => {
      // Remove the transaction from cache
      queryClient.removeQueries({
        queryKey: TRANSACTIONS_QUERY_KEYS.transaction(id)
      });
      
      // Invalidate transactions list to refetch
      queryClient.invalidateQueries({
        queryKey: ['transactions']
      });
      
      toast.success('Transaction deleted successfully!');
    },
    onError: (error) => {
      console.error('Failed to delete transaction:', error);
      toast.error('Failed to delete transaction');
    },
  });
};
