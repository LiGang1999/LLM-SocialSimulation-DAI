// frontend/src/pages/DocPage.tsx
import React from 'react';
import { Outlet, useParams } from 'react-router-dom';
import DocLayout from '@/components/DocLayout';

const DocPage: React.FC = () => {
  const params = useParams();
  return (
    <DocLayout>
      <Outlet />
    </DocLayout>
  );
};

export default DocPage;
