// frontend/vite-plugin-docs.ts

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import type { Plugin } from 'vite';


interface DocTreeItem {
  type: 'folder' | 'file';
  name: string;
  path: string;
  children?: DocTreeItem[];
  title?: string;
  url?: string;
}

let cachedDocTree: DocTreeItem[] = [];

/**
 * Custom Vite Plugin to handle documentation needs.
 */
export default function customDocPlugin(): Plugin {
  const virtualModuleId = 'socialsim-docs-tree';
  const resolvedVirtualModuleId = '\0' + virtualModuleId;

  const virtualRoutesModuleId = 'socialsim-docs-routes';
  const resolvedVirtualRoutesModuleId = '\0' + virtualRoutesModuleId;

  // Define the root directory for documentation
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const docRoot = path.resolve(__dirname, 'src/doc');

  /**
   * Helper function to recursively scan a directory and build a tree structure.
   */
  function getDirectoryTree(dirPath: string): DocTreeItem[] {
    const items = fs.readdirSync(dirPath);
    const tree: DocTreeItem[] = [];

    for (const item of items) {
      const fullPath = path.join(dirPath, item);
      const stat = fs.statSync(fullPath);
      // Create a URL-friendly path relative to the doc root
      const relativePath = path.relative(docRoot, fullPath).replace(/\\/g, '/');
      const url = `/doc/${relativePath.replace(/\.mdx$/, '')}`;

      if (stat.isDirectory()) {
        tree.push({
          type: 'folder',
          name: item,
          path: relativePath,
          children: getDirectoryTree(fullPath),
        });
      } else if (item.endsWith('.mdx')) {
        // Simple frontmatter parsing to get a title
        const fileContent = fs.readFileSync(fullPath, 'utf-8');
        const titleMatch = fileContent.match(/^#\s+(.*)/m);
        const title = titleMatch ? titleMatch[1] : path.basename(item, '.mdx');

        tree.push({
          type: 'file',
          name: item,
          path: relativePath,
          title: title,
          url: url
        });
      }
    }
    // Sort items so folders come first
    return tree.sort((a, b) => {
        if (a.type === 'folder' && b.type === 'file') return -1;
        if (a.type === 'file' && b.type === 'folder') return 1;
        return a.name.localeCompare(b.name);
    });
  }

  return {
    // The name of the plugin
    name: 'vite-plugin-custom-docs',

    buildStart() {
      cachedDocTree = getDirectoryTree(docRoot);
    },

    // --- Part 1: Virtual Module for Folder Hierarchy ---
    resolveId(id) {
      if (id === virtualModuleId) {
        return resolvedVirtualModuleId;
      }
      if (id === virtualRoutesModuleId) {
        return resolvedVirtualRoutesModuleId;
      }
    },
    load(id) {
      if (id === resolvedVirtualModuleId) {
        return `export default ${JSON.stringify(cachedDocTree)};`;
      }
      if (id === resolvedVirtualRoutesModuleId) {
        const files = cachedDocTree.flatMap(item => (item.type === 'file' ? [item] : item.children) ?? [])
          .filter((item): item is DocTreeItem & { type: 'file' } => !!item && item.type === 'file');

        const routeImports = files.map(file => {
          const componentPath = `/src/doc/${file.path}`;
          const routePath = file.path.replace(/\.mdx$/, '');
          return `{
            path: '${routePath}',
            Component: lazy(() => import('${componentPath}'))
          }`;
        }).join(',\n');

        return `
          import { lazy } from 'react';
          const docRoutes = [${routeImports}];
          export default docRoutes;
        `;
      }
    },

    handleHotUpdate({ file, server }) {
      if (file.startsWith(docRoot + path.sep)) {
        const newTree = getDirectoryTree(docRoot);
        if (JSON.stringify(newTree) !== JSON.stringify(cachedDocTree)) {
          cachedDocTree = newTree;
          const { moduleGraph } = server;
          const module = moduleGraph.getModuleById(resolvedVirtualModuleId);
          if (module) {
            moduleGraph.invalidateModule(module);
          }
          const routesModule = moduleGraph.getModuleById(resolvedVirtualRoutesModuleId);
          if (routesModule) {
            moduleGraph.invalidateModule(routesModule);
          }
          server.ws.send({
            type: 'full-reload',
            path: '*'
          });
        }
      }
    },
  };
}
