// frontend/src/components/DocLayout.tsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import docTree from 'socialsim-docs-tree';
import { Navbar } from './Navbar';
import './DocLayout.css'; // Import custom styles

interface DocTreeItem {
  type: 'folder' | 'file';
  name: string;
  path: string;
  children?: DocTreeItem[];
  title?: string;
  url?: string;
}

const hasAnyFiles = (item: DocTreeItem): boolean => {
  if (item.type === 'file') {
    return true;
  }
  if (item.type === 'folder' && item.children) {
    return item.children.some(hasAnyFiles);
  }
  return false;
};

const renderTree = (items: DocTreeItem[], currentPath: string) => {
  return (
    <ul className="space-y-2">
      {items.map((item) => {
        if (item.type === 'folder' && !hasAnyFiles(item)) {
          return null;
        }
        return (
          <li key={item.path}>
            {item.type === 'folder' ? (
              <div>
                <span className="font-semibold text-gray-500">{item.name}</span>
                {item.children && renderTree(item.children, currentPath)}
              </div>
            ) : (
              <Link
                to={item.url!}
                className={`block p-2 rounded-md text-gray-700 ${
                  currentPath === item.url ? 'bg-blue-100 text-blue-700 font-semibold' : 'hover:bg-gray-100'
                }`}
              >
                {item.title}
              </Link>
            )}
          </li>
        );
      })}
    </ul>
  );
};

const DocLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <div className="flex flex-col h-screen bg-white">
      <Navbar className="border-b bg-white" />
      <div className="flex flex-1 overflow-hidden">
        <aside className="w-64 bg-gray-50 border-r p-4 overflow-y-auto">
          <h2 className="text-lg font-bold mb-4 text-gray-800">文档目录</h2>
          <nav>{renderTree(docTree, currentPath)}</nav>
        </aside>
        <main className="flex-1 p-8 md:p-12 overflow-y-auto">
          <div className="prose max-w-4xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
};

export default DocLayout;
