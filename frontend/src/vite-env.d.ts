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
