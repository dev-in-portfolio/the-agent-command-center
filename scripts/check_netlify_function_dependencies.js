const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const packageJsonPath = path.join(root, 'package.json');
const functionsDir = path.join(root, 'netlify', 'functions');

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function walkJsFiles(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkJsFiles(fullPath, files);
      continue;
    }
    if (entry.isFile() && entry.name.endsWith('.js')) {
      files.push(fullPath);
    }
  }
  return files;
}

const pkg = readJson(packageJsonPath);
if (!pkg.dependencies || !pkg.dependencies['@supabase/supabase-js']) {
  throw new Error('Missing @supabase/supabase-js dependency in root package.json');
}

require.resolve('@supabase/supabase-js');

const supabaseImportFiles = [];
for (const filePath of walkJsFiles(functionsDir)) {
  const content = fs.readFileSync(filePath, 'utf8');
  if (content.includes("@supabase/supabase-js") || content.includes('@supabase/supabase-js')) {
    supabaseImportFiles.push(path.relative(root, filePath));
  }
}

if (supabaseImportFiles.length === 0) {
  throw new Error('No Netlify function imports found for @supabase/supabase-js');
}

console.log('NETLIFY_FUNCTION_DEPENDENCY_JS_CHECK_PASS');
