import React, { createContext, useContext, useState } from 'react';

const RoleContext = createContext();

export function RoleProvider({ children }) {
  const [currentRole, setCurrentRole] = useState('Investigator'); // 'Analyst' or 'Investigator'

  const isMasked = currentRole === 'Analyst';

  const maskValue = (value, type = 'text') => {
    if (!isMasked || !value) return value;

    if (type === 'name') {
      const parts = String(value).split(' ');
      return parts.map(p => p[0] + '*'.repeat(Math.max(1, p.length - 1))).join(' ');
    }
    if (type === 'phone') {
      const str = String(value);
      if (str.length > 7) {
        return str.substring(0, 6) + '*****' + str.substring(str.length - 2);
      }
      return '***-****';
    }
    if (type === 'email') {
      const parts = String(value).split('@');
      if (parts.length === 2) {
        return parts[0][0] + '***@' + parts[1];
      }
      return '***@***.com';
    }
    if (type === 'account') {
      const str = String(value);
      return str.length > 6 ? str.substring(0, 4) + '****' + str.substring(str.length - 2) : 'ACC_****';
    }
    return String(value).substring(0, 2) + '****';
  };

  return (
    <RoleContext.Provider value={{ currentRole, setCurrentRole, isMasked, maskValue }}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error('useRole must be used within a RoleProvider');
  }
  return context;
}
