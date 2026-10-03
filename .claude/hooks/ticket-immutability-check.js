#!/usr/bin/env node
'use strict';

// Blocks UPDATE/DELETE paths on append-only tables (NFR-02, NFR-05, AC-03, AC-07, AC-10).

const fs = require('fs');

const MODELS = ['TicketHistory', 'Assignment', 'TicketNote', 'TicketReply', 'SlaEvent', 'SlaPolicy', 'Notification'];
const TABLES = 'ticket_?histor(?:y|ies)|assignments?|ticket_?notes?|ticket_?repl(?:y|ies)|sla_?events?|sla_?polic(?:y|ies)|notifications?';
const REPO_FILE = /(histor|assignment|note|repl|sla_?event|sla_?polic|notification)/i;

const sqlRe = new RegExp('\\b(?:UPDATE|DELETE\\s+FROM)\\s+["\'\\x60]?(?:' + TABLES + ')\\b', 'gi');
const ormRe = new RegExp('\\b(?:update|delete)\\(\\s*(?:' + MODELS.join('|') + ')\\b', 'g');
const queryRe = new RegExp('\\.query\\(\\s*(?:' + MODELS.join('|') + ')\\s*\\)[^\\n]*\\.(?:update|delete)\\(', 'g');
const defRe = /^\s*(?:async\s+)?def\s+(?:update|delete|remove|edit|modify)\w*\(/gm;

function blank(match) {
  return match.replace(/[^\n]/g, ' ');
}

function lineOf(text, index) {
  return text.slice(0, index).split('\n').length;
}

function collect(re, text, label, out) {
  re.lastIndex = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    out.push(`line ${lineOf(text, m.index)}: ${label}: ${m[0].trim()}`);
  }
}

try {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const filePath = (input.tool_input && input.tool_input.file_path) || '';
  const norm = '/' + filePath.replace(/\\/g, '/');

  if (!filePath || !norm.endsWith('.py') || !norm.includes('/backend/src/')) {
    process.exit(0);
  }

  const raw = fs.readFileSync(filePath, 'utf8');
  const text = raw.replace(/#.*$/gm, blank);
  const problems = [];

  collect(sqlRe, text, 'raw UPDATE/DELETE on an append-only table', problems);
  collect(ormRe, text, 'ORM update/delete on an append-only model', problems);
  collect(queryRe, text, 'query update/delete on an append-only model', problems);

  const base = norm.split('/').pop();
  if (norm.includes('/repository/') && REPO_FILE.test(base)) {
    collect(defRe, text, 'update/delete method in an append-only repository', problems);
  }

  if (problems.length > 0) {
    process.stdout.write(
      `BLOCKED: append-only rule violated in ${filePath}\n` +
        problems.map((p) => `  - ${p}`).join('\n') +
        '\nFix: history, assignments, notes, replies, SLA events, SLA policy versions and notifications are insert-only (NFR-02, NFR-05). Add a new row instead of changing or deleting one.\n'
    );
    process.exit(2);
  }
} catch (_) {
  // Silent exit: stderr output shows up as a hook error in Claude Code.
}

process.exit(0);