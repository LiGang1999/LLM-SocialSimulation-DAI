// frontend/vite-plugin-docs.ts

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import type { Plugin } from 'vite';

// Helper function to convert markdown heading to a URL-friendly slug
const slugify = (text: string): string =>
  text
    .toLowerCase()
    .replace(/\s+/g, '-') // Replace spaces with -
    .replace(/[^\w-]+/g, ''); // Remove all non-word chars

interface DocTreeItem {
  type: 'folder' | 'file';
  name: string;
  path: string;
  children?: DocTreeItem[];
  title?: string;
  url?: string;
}

/**
 * Custom Vite Plugin to handle documentation needs.
 */
export default function customDocPlugin(): Plugin {
  const virtualModuleId = 'virtual:docs-tree';
  const resolvedVirtualModuleId = '\0' + virtualModuleId;

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

    // --- Part 1: Virtual Module for Folder Hierarchy ---
    resolveId(id) {
      if (id === virtualModuleId) {
        return resolvedVirtualModuleId;
      }
    },
    load(id) {
      if (id === resolvedVirtualModuleId) {
        // Scan the directory and create the tree object
        const tree = getDirectoryTree(docRoot);
        // Expose the tree as the default export of our virtual module
        return `export default ${JSON.stringify(tree)};`;
      }
    },

    // --- Part 2: MDX Transformation to Inject Headings ---
    transform(code, id) {
      // We only care about .mdx files
      if (!id.endsWith('.mdx')) {
        return null;
      }

      // This is a simple regex-based approach. For more complex needs,
      // you could use a full AST parser like 'unified' here.
      const headingRegex = /^(##|###|####)\s+(.*)/gm;
      const headings: { level: number; title: string; id: string }[] = [];
      let match;

      while ((match = headingRegex.exec(code)) !== null) {
        const level = match[1].length; // ## -> 2, ### -> 3
        const title = match[2].trim();
        headings.push({
          level: level,
          title: title,
          id: slugify(title), // Create a slug for the anchor link
        });
      }

      // If we found headings, append an export statement to the MDX file
      if (headings.length > 0) {
        const exportStatement = `\nexport const headings = ${JSON.stringify(headings)};`;
        return {
          code: code + exportStatement,
          map: null, // No source map changes in this simple case
        };
      }

      return null;
    },
  };
}
