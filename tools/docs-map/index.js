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

let rootArg = process.cwd();
for (let i = 0; i < process.argv.length; i++) {
  const a = process.argv[i];
  if (a === '--root' && i + 1 < process.argv.length) {
    rootArg = process.argv[i + 1];
  } else if (a.startsWith('--root=')) {
    rootArg = a.slice('--root='.length);
  }
}

const ROOT = path.resolve(rootArg);
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

function stripComment(s) {
  s = s.trim();
  if (!s) return '';
  if (s.startsWith('#')) return '';
  if (s.startsWith('"')) {
    const end = s.indexOf('"', 1);
    if (end !== -1) {
      const after = s.slice(end + 1);
      if (after.includes('#')) return s.slice(0, end + 1).trim();
      return s;
    }
  }
  if (s.startsWith("'")) {
    const end = s.indexOf("'", 1);
    if (end !== -1) {
      const after = s.slice(end + 1);
      if (after.includes('#')) return s.slice(0, end + 1).trim();
      return s;
    }
  }
  if (s.startsWith('[')) {
    const end = s.lastIndexOf(']');
    if (end !== -1) {
      const after = s.slice(end + 1);
      if (after.includes('#')) return s.slice(0, end + 1).trim();
      return s;
    }
  }
  const cIdx = s.indexOf(' #');
  if (cIdx !== -1) return s.slice(0, cIdx).trim();
  return s;
}

// Minimal, dependency-free frontmatter parser (top-level scalars + inline lists).
function parseFrontmatter(text) {
  const src = text.replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n');
  if (!src.startsWith('---')) return {};
  const end = src.indexOf('\n---', 3);
  if (end === -1) return {};
  const fm = src.slice(3, end).split('\n');
  const out = {};
  let key = null;
  for (let line of fm) {
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const listItem = line.match(/^\s+-\s+(.*)$/);
    if (listItem && key) {
      out[key].push(strip(listItem[1]));
      continue;
    }
    const kv = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!kv) continue;
    key = kv[1];
    const val = stripComment(kv[2]);
    if (val === '' || val === '[]') { out[key] = []; continue; }
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
  s = stripComment(s);
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
  const rootCandidates = ['AGENT.md', 'NEED_CLARIFICATION.md', 'NEED_CLEARIFICATION.md'];
  for (const rc of rootCandidates) {
    const rp = path.join(ROOT, rc);
    if (fs.existsSync(rp) && !files.includes(rp)) files.push(rp);
  }

  const docs = {};
  const missingIds = [];
  const reverseEdgeViolations = [];
  const FORBIDDEN_REVERSE_EDGES = ['affected_by', 'referenced_by', 'implemented_by', 'depended_on_by'];

  for (const f of files) {
    let text = '';
    try { text = fs.readFileSync(f, 'utf8'); } catch { continue; }
    const fm = parseFrontmatter(text);
    const id = fm.id;
    if (!id) {
      if (f.startsWith(DOCS)) {
        missingIds.push(path.relative(ROOT, f).split(path.sep).join('/'));
      }
      continue;
    }

    for (const rev of FORBIDDEN_REVERSE_EDGES) {
      if (fm[rev] !== undefined) {
        reverseEdgeViolations.push({ id, field: rev, file: f });
      }
    }

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
  const rel = { references: {}, affects: {}, implements: {}, depends_on: {} };
  for (const d of Object.values(docs)) {
    for (const t of d.references) push(rel.references, t, d.id);
    for (const t of d.affects) push(rel.affects, t, d.id);
    for (const t of d.depends_on) push(rel.depends_on, t, d.id);
    for (const t of d.implements) {
      push(rel.implements, t, d.id);
      const cleanT = t.replace(/^flow:/, '');
      if (cleanT !== t) push(rel.implements, cleanT, d.id);
      else push(rel.implements, 'flow:' + cleanT, d.id);
    }
  }
  return { docs, rel, missingIds, reverseEdgeViolations };
}

function push(obj, k, v) {
  obj[k] = obj[k] || [];
  if (!obj[k].includes(v)) obj[k].push(v);
}

// ---------- commands ----------
const rawArgs = process.argv.slice(2);
const positional = [];
for (let i = 0; i < rawArgs.length; i++) {
  if (rawArgs[i] === '--root') { i++; continue; }
  if (rawArgs[i].startsWith('--')) continue;
  positional.push(rawArgs[i]);
}

const cmd = positional[0];
const arg = positional[1];

const STOP_WORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
  'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
  'will', 'with', 'change', 'update', 'modify', 'make', 'so', 'after', 'instead',
  'should', 'do', 'does', 'did', 'or', 'than'
]);

function match(q) {
  if (!q) return [];
  const rawQ = q.trim().toLowerCase();
  const tokens = rawQ.split(/[^a-z0-9_-]+/).filter((t) => t.length > 1 && !STOP_WORDS.has(t));

  const hits = [];
  for (const d of Object.values(model.docs)) {
    const hay = [d.id, d.title, ...d.keywords, ...d.domains, ...d.flows].join(' ').toLowerCase();
    if (hay.includes(rawQ)) {
      hits.push(d.id);
      continue;
    }
    if (tokens.length > 0) {
      let matched = false;
      for (const t of tokens) {
        if (d.keywords.some((k) => k.toLowerCase().includes(t)) ||
            d.domains.some((dm) => dm.toLowerCase().includes(t)) ||
            d.flows.some((f) => f.toLowerCase().includes(t)) ||
            d.id.toLowerCase().includes(t) ||
            d.title.toLowerCase().includes(t)) {
          matched = true;
          break;
        }
      }
      if (matched) hits.push(d.id);
    }
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
      r.depends_on.forEach((e) => edges.add(e));
      r.implements.forEach((e) => edges.add(e));
    }
    (model.rel.affects[id] || []).forEach((e) => edges.add(e));
    (model.rel.references[id] || []).forEach((e) => edges.add(e));
    (model.rel.depends_on[id] || []).forEach((e) => edges.add(e));
    console.log('  ' + id);
    if (!edges.size) console.log('    (no edges)');
    for (const e of edges) console.log('    -> ' + e);
  }
}

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
      implemented_by: [...new Set([
        ...(model.rel.implements[id] || []),
        ...(model.rel.implements['flow:' + id] || []),
      ])],
      depended_on_by: model.rel.depends_on[id] || [],
    };
  }
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2));
  fs.writeFileSync(path.join(OUT, 'relations.json'), JSON.stringify(relations, null, 2));
  console.log('wrote ' + path.join('.qwen', 'docs-index', 'manifest.json'));
  console.log('wrote ' + path.join('.qwen', 'docs-index', 'relations.json'));
  console.log('docs: ' + Object.keys(manifest).length);
}

const model = (cmd && ['generate', 'search', 'flow', 'doc', 'related', 'code', 'impact', 'validate'].includes(cmd))
  ? load()
  : null;

switch (cmd) {
  case 'generate': generate(); break;
  case 'search': printMatches(arg); break;
  case 'flow': {
    const cleanFlow = arg ? arg.replace(/^flow:/, '') : '';
    const impl = [
      ...(model.rel.implements[arg] || []),
      ...(model.rel.implements[cleanFlow] || []),
      ...(model.rel.implements['flow:' + cleanFlow] || [])
    ];
    const uniqueImpl = [...new Set(impl)];
    console.log('FLOW ' + arg);
    console.log('IMPLEMENTED_BY');
    if (!uniqueImpl.length) console.log('  (none)');
    for (const i of uniqueImpl) console.log('  ' + i);
    const { code, tests } = codeAndTests(uniqueImpl);
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
    if (!arg) {
      console.log('RELATIONS');
      console.log('  (no id specified)');
      break;
    }
    const d = model.docs[arg];
    const forward = d ? [...d.affects, ...d.references, ...d.depends_on, ...d.implements] : [];
    const reverse = [
      ...(model.rel.affects[arg] || []),
      ...(model.rel.references[arg] || []),
      ...(model.rel.depends_on[arg] || []),
      ...(model.rel.implements[arg] || []),
    ];
    const ids = [arg, ...forward, ...reverse];
    printRelations([...new Set(ids)]);
    break;
  }
  case 'code': {
    console.log('DOCS');
    if (!arg) {
      console.log('  (no path specified)');
      break;
    }
    const cleanArg = arg.replace(/^\.\//, '').replace(/^\//, '');
    for (const d of Object.values(model.docs)) {
      const allPaths = [...d.code_paths, ...d.test_paths];
      if (allPaths.some((c) => cleanArg.startsWith(c.replace(/\/\*\*$/, '')) || c.includes(cleanArg))) {
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
        // Forward: affects, references, depends_on
        for (const e of [...d.affects, ...d.references, ...d.depends_on]) {
          if (!frontier.has(e) && model.docs[e]) { frontier.add(e); grew = true; }
        }
        // Flow implements: expand upward to flow, and outward to sibling implementers
        for (const f of d.implements) {
          if (!frontier.has(f) && model.docs[f]) { frontier.add(f); grew = true; }
          const cleanF = f.replace(/^flow:/, '');
          const siblings = [
            ...(model.rel.implements[f] || []),
            ...(model.rel.implements[cleanF] || []),
            ...(model.rel.implements['flow:' + cleanF] || [])
          ];
          for (const s of siblings) {
            if (!frontier.has(s) && model.docs[s]) { frontier.add(s); grew = true; }
          }
        }
        // If d is itself a flow doc or lists flows in d.flows, expand its implementers
        const relatedFlows = [
          id,
          id.replace(/^flow:/, ''),
          ...(d.flows || []),
          ...(d.flows || []).map((fl) => 'flow:' + fl)
        ];
        for (const fl of relatedFlows) {
          const impls = model.rel.implements[fl] || [];
          for (const imp of impls) {
            if (!frontier.has(imp) && model.docs[imp]) { frontier.add(imp); grew = true; }
          }
        }
        // Reverse edges: affected_by, depended_on_by
        for (const e of [...(model.rel.affects[id] || []), ...(model.rel.depends_on[id] || [])]) {
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
    for (const file of model.missingIds) {
      console.log('ERROR missing id: ' + file);
      errors++;
    }
    for (const v of model.reverseEdgeViolations) {
      console.log('ERROR reverse-edge drift: ' + v.id + ' authors ' + v.field);
      errors++;
    }
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