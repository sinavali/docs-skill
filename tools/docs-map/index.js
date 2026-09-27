#!/usr/bin/env node
/**
 * docs-map — generate and query the documentation graph.
 *
 * Source of truth: YAML frontmatter in Markdown files under docs/
 * Derived cache:   .qwen/docs-index (manifest.json, relations.json)
 *
 * No database. No network. Node stdlib only.
 *
 * Usage:
 *   docs-map generate [--root .]
 *   docs-map search "<query>"
 *   docs-map flow <flow>
 *   docs-map doc <id>
 *   docs-map related <id>
 *   docs-map code <path>
 *   docs-map impact "<request>"
 *   docs-map validate
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = process.argv.includes('--root')
  ? process.argv[process.argv.indexOf('--root') + 1]
  : process.cwd();
const DOCS = path.join(ROOT, 'docs');
const OUT = path.join(ROOT, '.qwen', 'docs-index');
const EXCLUDE = ['node_modules', '.git', 'dist', 'build', '.cache', 'coverage'];

// ---------- discovery ----------
function walk(dir, acc) {
  if (!fs.existsSync(dir)) return acc;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (EXCLUDE.includes(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, acc);
    else if (e.name.endsWith('.md')) acc.push(p);
  }
  return acc;
}

// Minimal, dependency-free frontmatter parser (top-level scalars + inline lists).
function parseFrontmatter(text) {
  if (!text.startsWith('---')) return {};
  const end = text.indexOf('\n---', 3);
  if (end === -1) return {};
  const fm = text.slice(3, end).split(/\r?\n/);
  const out = {};
  let key = null;
  for (let line of fm) {
    if (!line.trim()) continue;
    const listItem = line.match(/^\s+-\s+(.*)$/);
    if (listItem && key) {
      out[key].push(strip(listItem[1]));
      continue;
    }
    const kv = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (!kv) continue;
    key = kv[1];
    const val = kv[2].trim();
    if (val === '') { out[key] = []; continue; }
    if (val.startsWith('[') && val.endsWith(']')) {
      out[key] = val.slice(1, -1).split(',').map((s) => strip(s.trim())).filter(Boolean);
      key = null;
    } else {
      out[key] = strip(val);
      key = null;
    }
  }
  return out;
}
function strip(s) {
  s = s.trim();
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    return s.slice(1, -1);
  }
  return s;
}
function asArray(v) {
  if (v === undefined || v === null) return [];
  return Array.isArray(v) ? v : [v];
}

// ---------- model ----------
function load() {
  const files = walk(DOCS, []);
  const docs = {};
  for (const f of files) {
    let text = '';
    try { text = fs.readFileSync(f, 'utf8'); } catch { continue; }
    const fm = parseFrontmatter(text);
    const id = fm.id;
    if (!id) continue;
    docs[id] = {
      id,
      path: path.relative(ROOT, f).split(path.sep).join('/'),
      title: fm.title || '',
      level: fm.level || '',
      kind: fm.kind || '',
      domains: asArray(fm.domains),
      flows: asArray(fm.flows),
      keywords: asArray(fm.keywords),
      references: asArray(fm.references),
      affects: asArray(fm.affects),
      implements: asArray(fm.implements),
      depends_on: asArray(fm.depends_on),
      code_paths: asArray(fm.code_paths),
      test_paths: asArray(fm.test_paths),
      file: fm.file || undefined,
    };
  }
  // derived reverse edges
  const rel = { references: {}, affects: {}, implements: {} };
  for (const d of Object.values(docs)) {
    for (const t of d.references) push(rel.references, t, d.id);
    for (const t of d.affects) push(rel.affects, t, d.id);
    for (const t of d.implements) push(rel.implements, t, d.id);
  }
  return { docs, rel };
}
function push(obj, k, v) { (obj[k] = obj[k] || []).push(v); }

// ---------- commands ----------
// positional args = process.argv minus flags and their values
const rawArgs = process.argv.slice(2);
const positional = [];
for (let i = 0; i < rawArgs.length; i++) {
  if (rawArgs[i] === '--root') { i++; continue; }
  if (rawArgs[i].startsWith('--')) continue;
  positional.push(rawArgs[i]);
}
const cmd = positional[0];
const arg = positional[1];
const model = load();

function generate() {
  fs.mkdirSync(OUT, { recursive: true });
  const manifest = {};
  for (const d of Object.values(model.docs)) manifest[d.id] = d;
  const relations = {};
  for (const id of Object.keys(model.docs)) {
    const d = model.docs[id];
    relations[id] = {
      references: d.references,
      affects: d.affects,
      implements: d.implements,
      depends_on: d.depends_on,
      referenced_by: model.rel.references[id] || [],
      affected_by: model.rel.affects[id] || [],
      implemented_by: model.rel.implements[id] || [],
    };
  }
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2));
  fs.writeFileSync(path.join(OUT, 'relations.json'), JSON.stringify(relations, null, 2));
  console.log('wrote ' + path.join('.qwen', 'docs-index', 'manifest.json'));
  console.log('wrote ' + path.join('.qwen', 'docs-index', 'relations.json'));
  console.log('docs: ' + Object.keys(manifest).length);
}

function match(q) {
  q = (q || '').toLowerCase();
  const hits = [];
  for (const d of Object.values(model.docs)) {
    const hay = [d.id, d.title, ...d.keywords, ...d.domains, ...d.flows].join(' ').toLowerCase();
    if (hay.includes(q)) hits.push(d.id);
  }
  return hits;
}

function printMatches(q) {
  const hits = match(q);
  console.log('MATCHES');
  if (!hits.length) console.log('  (none)');
  for (const h of hits) console.log('  ' + h);
  return hits;
}

function codeAndTests(ids) {
  const code = new Set(), tests = new Set();
  for (const id of ids) {
    const d = model.docs[id];
    if (!d) continue;
    d.code_paths.forEach((c) => code.add(c));
    d.test_paths.forEach((t) => tests.add(t));
  }
  return { code, tests };
}

function printRelations(ids) {
  console.log('RELATIONS');
  for (const id of ids) {
    const r = model.docs[id] ? model.docs[id] : null;
    const edges = new Set();
    if (r) {
      r.affects.forEach((e) => edges.add(e));
      r.references.forEach((e) => edges.add(e));
      r.implements.forEach((e) => edges.add(e));
    }
    (model.rel.affects[id] || []).forEach((e) => edges.add(e));
    (model.rel.references[id] || []).forEach((e) => edges.add(e));
    console.log('  ' + id);
    if (!edges.size) console.log('    (no edges)');
    for (const e of edges) console.log('    -> ' + e);
  }
}

switch (cmd) {
  case 'generate': generate(); break;
  case 'search': printMatches(arg); break;
  case 'flow': {
    const impl = model.rel.implements[arg] || [];
    console.log('FLOW ' + arg);
    console.log('IMPLEMENTED_BY');
    if (!impl.length) console.log('  (none)');
    for (const i of impl) console.log('  ' + i);
    const { code, tests } = codeAndTests(impl);
    console.log('CODE'); [...code].forEach((c) => console.log('  ' + c));
    console.log('TESTS'); [...tests].forEach((t) => console.log('  ' + t));
    break;
  }
  case 'doc': {
    const d = model.docs[arg];
    if (!d) { console.log('not found: ' + arg); break; }
    console.log(JSON.stringify(d, null, 2));
    break;
  }
  case 'related': {
    const ids = [arg, ...(model.rel.affects[arg] || []), ...(model.rel.references[arg] || [])];
    printRelations([...new Set(ids)]);
    break;
  }
  case 'code': {
    console.log('DOCS');
    for (const d of Object.values(model.docs)) {
      if (d.code_paths.some((c) => arg.startsWith(c.replace(/\/\*\*$/, '')) || c.includes(arg))) {
        console.log('  ' + d.id);
      }
    }
    break;
  }
  case 'impact': {
    const seeds = match(arg);
    printMatches(arg);
    const frontier = new Set(seeds);
    let grew = true;
    while (grew) {
      grew = false;
      for (const id of [...frontier]) {
        const d = model.docs[id];
        if (!d) continue;
        for (const e of [...d.affects, ...d.references, ...d.implements]) {
          if (!frontier.has(e) && model.docs[e]) { frontier.add(e); grew = true; }
        }
        for (const e of [...(model.rel.affects[id] || [])]) {
          if (!frontier.has(e) && model.docs[e]) { frontier.add(e); grew = true; }
        }
      }
    }
    console.log('');
    printRelations([...frontier]);
    const { code, tests } = codeAndTests([...frontier]);
    console.log('CODE'); if (!code.size) console.log('  (none)'); [...code].forEach((c) => console.log('  ' + c));
    console.log('TESTS'); if (!tests.size) console.log('  (none)'); [...tests].forEach((t) => console.log('  ' + t));
    break;
  }
  case 'validate': {
    let errors = 0;
    for (const d of Object.values(model.docs)) {
      for (const e of d.references) if (!model.docs[e]) { console.log('ERROR broken references: ' + d.id + ' -> ' + e); errors++; }
      for (const e of d.affects) if (!model.docs[e]) { console.log('ERROR broken affects: ' + d.id + ' -> ' + e); errors++; }
      for (const e of d.depends_on) if (!model.docs[e]) { console.log('ERROR broken depends_on: ' + d.id + ' -> ' + e); errors++; }
    }
    console.log(errors ? errors + ' error(s)' : 'graph ok');
    process.exit(errors ? 1 : 0);
  }
  default:
    console.log('docs-map: generate | search | flow | doc | related | code | impact | validate');
}