'use client';

import React, { useEffect } from 'react';
import { useStore } from '@/lib/store';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const checkAuth = useStore((state) => state.checkAuth);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return <>{children}</>;
};
