'use strict';
// Regression tests for docs-map.
//
// The frontmatter parser splits the block on newlines and then matches each
// line with `(.*)$`. In JavaScript `.` does not match `\r`, so when a document
// uses CRLF line endings the final frontmatter line keeps a trailing `\r` and
// its list item / key-value match fails silently — the entry is dropped from
// the generated manifest.
//
// Run with: node --test tools/docs-map

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const CLI = path.join(__dirname, 'index.js');

const CRLF = '\r\n';
const LF = '\n';
const CR = '\r';

// Build a document from raw lines joined with the requested line ending.
function doc(eol, lines) {
  return lines.join(eol) + eol;
}

// Write the given docs into a throwaway root and run the real CLI over it.
function generate(docs) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'docs-map-test-'));
  fs.mkdirSync(path.join(root, 'docs'), { recursive: true });
  for (const [name, content] of Object.entries(docs)) {
    fs.writeFileSync(path.join(root, 'docs', name), content);
  }
  execFileSync(process.execPath, [CLI, '--root', root, 'generate'], { stdio: 'pipe' });
  const manifest = JSON.parse(
    fs.readFileSync(path.join(root, '.qwen', 'docs-index', 'manifest.json'), 'utf8')
  );
  return { root, manifest };
}

function cleanup(root) {
  fs.rmSync(root, { recursive: true, force: true });
}

const LIST_LAST_LINES = [
  '---',
  'id: demo/alpha',
  'title: Alpha',
  'code_paths:',
  '  - core/src/Alpha/**',
  '  - core/src/Beta/**',
  '---',
  '',
  '# Alpha',
];

const SCALAR_LAST_LINES = [
  '---',
  'id: demo/beta',
  'title: Beta',
  'level: product',
  'kind: blueprint',
  '---',
  '',
  '# Beta',
];

test('LF: trailing list item and scalar are both kept (control)', () => {
  const { root, manifest } = generate({
    'alpha.md': doc(LF, LIST_LAST_LINES),
    'beta.md': doc(LF, SCALAR_LAST_LINES),
  });
  try {
    assert.deepEqual(manifest['demo/alpha'].code_paths, [
      'core/src/Alpha/**',
      'core/src/Beta/**',
    ]);
    assert.equal(manifest['demo/beta'].kind, 'blueprint');
  } finally {
    cleanup(root);
  }
});

test('CRLF: trailing list item is kept', () => {
  const { root, manifest } = generate({ 'alpha.md': doc(CRLF, LIST_LAST_LINES) });
  try {
    assert.deepEqual(manifest['demo/alpha'].code_paths, [
      'core/src/Alpha/**',
      'core/src/Beta/**',
    ]);
  } finally {
    cleanup(root);
  }
});

test('CRLF: trailing scalar field is kept', () => {
  const { root, manifest } = generate({ 'beta.md': doc(CRLF, SCALAR_LAST_LINES) });
  try {
    assert.equal(manifest['demo/beta'].kind, 'blueprint');
  } finally {
    cleanup(root);
  }
});

test('lone CR: document is parsed at all', () => {
  const { root, manifest } = generate({ 'alpha.md': doc(CR, LIST_LAST_LINES) });
  try {
    assert.deepEqual(manifest['demo/alpha'].code_paths, [
      'core/src/Alpha/**',
      'core/src/Beta/**',
    ]);
  } finally {
    cleanup(root);
  }
});
