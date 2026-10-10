'use strict';
// Tests for docs-map CLI and graph queries.

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
function createRepo(docs) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'docs-map-test-'));
  fs.mkdirSync(path.join(root, 'docs'), { recursive: true });
  for (const [name, content] of Object.entries(docs)) {
    const filePath = path.join(root, 'docs', name);
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, content);
  }
  return root;
}

function runCli(root, args, options = {}) {
  try {
    const stdout = execFileSync(process.execPath, [CLI, '--root', root, ...args], {
      stdio: 'pipe',
      ...options,
    });
    return { status: 0, stdout: stdout.toString() };
  } catch (err) {
    return { status: err.status, stdout: err.stdout ? err.stdout.toString() : '', stderr: err.stderr ? err.stderr.toString() : '' };
  }
}

function generate(docs) {
  const root = createRepo(docs);
  const res = runCli(root, ['generate']);
  assert.equal(res.status, 0);
  const manifest = JSON.parse(
    fs.readFileSync(path.join(root, '.qwen', 'docs-index', 'manifest.json'), 'utf8')
  );
  const relations = JSON.parse(
    fs.readFileSync(path.join(root, '.qwen', 'docs-index', 'relations.json'), 'utf8')
  );
  return { root, manifest, relations };
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
    assert.deepEqual(manifest['demo/beta'].kind, 'blueprint');
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

test('generate: writes depended_on_by into relations.json', () => {
  const { root, relations } = generate({
    'a.md': `---
id: doc/a
title: Doc A
depends_on: [doc/b]
---
# Doc A`,
    'b.md': `---
id: doc/b
title: Doc B
---
# Doc B`,
  });
  try {
    assert.deepEqual(relations['doc/a'].depends_on, ['doc/b']);
    assert.deepEqual(relations['doc/b'].depended_on_by, ['doc/a']);
  } finally {
    cleanup(root);
  }
});

test('impact: natural language query seeds via keyword token and expands depends_on & flow siblings', () => {
  const root = createRepo({
    'reg.md': `---
id: auth/registration
title: Registration Rules
keywords: [registration, signup, verification]
implements: [registration]
depends_on: [security/token-policy]
affects: [notifications/email]
code_paths: [packages/auth/**]
test_paths: [packages/auth/test/**]
---
# Reg`,
    'sec.md': `---
id: security/token-policy
title: Token Policy
code_paths: [packages/security/**]
---
# Sec`,
    'notif.md': `---
id: notifications/email
title: Email
code_paths: [packages/notifications/**]
---
# Notif`,
    'profile.md': `---
id: users/profile
title: Profile
implements: [registration]
code_paths: [packages/users/**]
---
# Profile`,
  });
  try {
    const res = runCli(root, ['impact', 'change verification expiry to 24h']);
    assert.equal(res.status, 0);
    // seeds should have found auth/registration
    assert.match(res.stdout, /auth\/registration/);
    // frontier should have expanded to security/token-policy (depends_on)
    assert.match(res.stdout, /security\/token-policy/);
    // frontier should have expanded to notifications/email (affects)
    assert.match(res.stdout, /notifications\/email/);
    // frontier should have expanded to users/profile (sibling implementer of registration flow)
    assert.match(res.stdout, /users\/profile/);
    // code surface should include packages/security/** and packages/auth/**
    assert.match(res.stdout, /packages\/auth\/\*\*/);
    assert.match(res.stdout, /packages\/security\/\*\*/);
  } finally {
    cleanup(root);
  }
});

test('code: safely handles missing argument and matches paths', () => {
  const root = createRepo({
    'doc.md': `---
id: doc/a
code_paths: [packages/auth/src/**]
---
# Doc`,
  });
  try {
    // With missing path argument: should not throw TypeError
    const resEmpty = runCli(root, ['code']);
    assert.equal(resEmpty.status, 0);
    assert.match(resEmpty.stdout, /\(no path specified\)/);

    // With matching path argument
    const resMatch = runCli(root, ['code', 'packages/auth/src/index.ts']);
    assert.equal(resMatch.status, 0);
    assert.match(resMatch.stdout, /doc\/a/);
  } finally {
    cleanup(root);
  }
});

test('related: prints forward and reverse edges including depends_on', () => {
  const root = createRepo({
    'a.md': `---
id: doc/a
depends_on: [doc/b]
---
# A`,
    'b.md': `---
id: doc/b
---
# B`,
  });
  try {
    const res = runCli(root, ['related', 'doc/a']);
    assert.equal(res.status, 0);
    assert.match(res.stdout, /doc\/a/);
    assert.match(res.stdout, /-> doc\/b/);
  } finally {
    cleanup(root);
  }
});

test('validate: catches broken references, reverse edge drift, and missing ids', () => {
  const root = createRepo({
    'bad-ref.md': `---
id: doc/bad
references: [doc/nonexistent]
affected_by: [doc/other]
---
# Bad`,
    'no-id.md': `---
title: Missing ID
---
# No ID`,
  });
  try {
    const res = runCli(root, ['validate']);
    assert.equal(res.status, 1);
    assert.match(res.stdout, /ERROR broken references: doc\/bad -> doc\/nonexistent/);
    assert.match(res.stdout, /ERROR reverse-edge drift: doc\/bad authors affected_by/);
    assert.match(res.stdout, /ERROR missing id: docs\/no-id\.md/);
  } finally {
    cleanup(root);
  }
});

test('CLI supports --root=<dir> syntax', () => {
  const root = createRepo({
    'a.md': `---
id: doc/a
title: Alpha Doc
---
# A`,
  });
  try {
    const stdout = execFileSync(process.execPath, [CLI, `--root=${root}`, 'search', 'Alpha'], {
      stdio: 'pipe',
    }).toString();
    assert.match(stdout, /doc\/a/);
  } finally {
    cleanup(root);
  }
});

test('parseFrontmatter: strips unquoted inline comments cleanly', () => {
  const root = createRepo({
    'a.md': `---
id: doc/a # the primary doc
title: Doc A # title comment
keywords:
  - auth # authentication
references: [doc/b # inline ref]
---
# A`,
    'b.md': `---
id: doc/b
---
# B`,
  });
  try {
    const res = runCli(root, ['doc', 'doc/a']);
    assert.equal(res.status, 0);
    const parsed = JSON.parse(res.stdout);
    assert.equal(parsed.id, 'doc/a');
    assert.equal(parsed.title, 'Doc A');
    assert.deepEqual(parsed.keywords, ['auth']);
    assert.deepEqual(parsed.references, ['doc/b']);
  } finally {
    cleanup(root);
  }
});

test('flow: resolves interchangeably with or without flow: prefix', () => {
  const root = createRepo({
    'reg.md': `---
id: auth/registration
implements: [flow:registration]
---
# Reg`,
  });
  try {
    const resWithout = runCli(root, ['flow', 'registration']);
    assert.equal(resWithout.status, 0);
    assert.match(resWithout.stdout, /auth\/registration/);

    const resWith = runCli(root, ['flow', 'flow:registration']);
    assert.equal(resWith.status, 0);
    assert.match(resWith.stdout, /auth\/registration/);
  } finally {
    cleanup(root);
  }
});

test('impact: expands implementers when seed is a flow document', () => {
  const root = createRepo({
    '007-flows/reg.md': `---
id: flow:registration
title: Registration Flow
flows: [registration]
---
# Flow`,
    'auth/reg.md': `---
id: auth/registration
implements: [flow:registration]
code_paths: [packages/auth/**]
---
# Auth Reg`,
  });
  try {
    const res = runCli(root, ['impact', 'registration']);
    assert.equal(res.status, 0);
    assert.match(res.stdout, /auth\/registration/);
    assert.match(res.stdout, /packages\/auth\/\*\*/);
  } finally {
    cleanup(root);
  }
});

test('code: matches paths with ./ prefix and matches test_paths', () => {
  const root = createRepo({
    'doc.md': `---
id: doc/auth
code_paths: [packages/auth/src/**]
test_paths: [packages/auth/test/**]
---
# Auth`,
  });
  try {
    const resDotSlash = runCli(root, ['code', './packages/auth/src/index.ts']);
    assert.equal(resDotSlash.status, 0);
    assert.match(resDotSlash.stdout, /doc\/auth/);

    const resTest = runCli(root, ['code', 'packages/auth/test/unit.test.ts']);
    assert.equal(resTest.status, 0);
    assert.match(resTest.stdout, /doc\/auth/);
  } finally {
    cleanup(root);
  }
});
