// frontend/src/pages/DocPage.tsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import DocLayout from '@/components/DocLayout';

const DocPage: React.FC = () => {
  return (
    <DocLayout>
      <Outlet />
    </DocLayout>
  );
};

export default DocPage;
