import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

test('generated.ts is deterministic and up to date', () => {
  const out = join(mkdtempSync(join(tmpdir(), 'draw-')), 'generated.ts');
  execFileSync('python3', ['tools/gen.py', '--ts', out]);
  assert.equal(readFileSync(out, 'utf8'), readFileSync('src/drawings/generated.ts', 'utf8'));
});
