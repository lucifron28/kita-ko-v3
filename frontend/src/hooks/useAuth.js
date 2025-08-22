import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// Query keys
export const AUTH_QUERY_KEYS = {
  profile: ['auth', 'profile'],
  dashboard: ['auth', 'dashboard'],
};

// Get user profile
export const useProfile = () => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: AUTH_QUERY_KEYS.profile,
    queryFn: () => authAPI.getProfile(),
    enabled: isAuthenticated, // Only fetch when authenticated
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    select: (response) => response.data,
  });
};

// Get dashboard data
export const useDashboard = () => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: AUTH_QUERY_KEYS.dashboard,
    queryFn: () => authAPI.getDashboard(),
    enabled: isAuthenticated, // Only fetch when authenticated
    staleTime: 2 * 60 * 1000, // 2 minutes
    cacheTime: 5 * 60 * 1000, // 5 minutes
    select: (response) => response.data,
  });
};

// Update profile mutation
export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (profileData) => authAPI.updateProfile(profileData),
    onSuccess: (response) => {
      // Update the profile cache
      queryClient.setQueryData(AUTH_QUERY_KEYS.profile, response.data);
    },
  });
};

// Change password mutation
export const useChangePassword = () => {
  return useMutation({
    mutationFn: (passwordData) => authAPI.changePassword(passwordData),
  });
};
