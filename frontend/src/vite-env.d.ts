/// <reference types="vite/client" />

declare module 'virtual:docs-tree' {
  const tree: {
    type: 'folder' | 'file';
    name: string;
    path: string;
    children?: any[];
    title?: string;
    url?: string;
  }[];
  export default tree;
}

declare module 'virtual:docs-routes' {
  import type { LazyExoticComponent } from 'react';
  const routes: {
    path: string;
    Component: LazyExoticComponent<() => JSX.Element>;
  }[];
  export default routes;
}
