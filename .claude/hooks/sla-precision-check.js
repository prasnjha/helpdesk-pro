#!/usr/bin/env node
'use strict';

// Blocks floating-point arithmetic in SLA code (NFR-01, metric M3).

const fs = require('fs');

function blank(match) {
  return match.replace(/[^\n]/g, ' ');
}

function lineOf(text, index) {
  return text.slice(0, index).split('\n').length;
}

const RULES = [
  [/\b[Ff]loat\b/g, 'float type'],
  [/(?<![\w.])\d+\.\d*(?:[eE][+-]?\d+)?(?![\w.])|(?<![\w.])\.\d+(?![\w.])/g, 'float literal'],
  [/\b\d+[eE][+-]?\d+\b/g, 'exponent literal'],
  [/(?<!\/)\/(?!\/)/g, 'true division "/" (use "//")'],
  [/\bround\(/g, 'round()'],
  [/\.total_seconds\(/g, '.total_seconds() returns a float (use "// timedelta(minutes=1)")'],
];

try {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const filePath = (input.tool_input && input.tool_input.file_path) || '';
  const norm = '/' + filePath.replace(/\\/g, '/');
  const base = norm.split('/').pop();

  if (!filePath || !norm.endsWith('.py') || !norm.includes('/backend/src/')) {
    process.exit(0);
  }

  const inScope = norm.includes('/domain/') || /sla|clock|escalat|timer|breach/i.test(base);
  if (!inScope) {
    process.exit(0);
  }

  const raw = fs.readFileSync(filePath, 'utf8');
  const code = raw
    .replace(/("""|''')[\s\S]*?\1/g, blank)
    .replace(/"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'/g, blank)
    .replace(/#.*$/gm, blank);

  const problems = [];
  for (const [re, label] of RULES) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(code)) !== null) {
      problems.push(`line ${lineOf(code, m.index)}: ${label}: ${m[0].trim()}`);
    }
  }

  if (problems.length > 0) {
    process.stdout.write(
      `BLOCKED: floating-point arithmetic in SLA code (${filePath})\n` +
        problems.map((p) => `  - ${p}`).join('\n') +
        '\nFix: SLA values are integer minutes only (NFR-01). Use integer math, for example (end - start) // timedelta(minutes=1).\n'
    );
    process.exit(2);
  }
} catch (_) {
  // Silent exit: stderr output shows up as a hook error in Claude Code.
}

process.exit(0);