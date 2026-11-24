# tools

`gen.py` draws the SVG ornaments (columns, ivy, pediment) and writes them to `src/drawings/generated.ts`.
Regenerate after editing `gen.py` (the determinism test fails otherwise):

    python3 tools/gen.py --ts src/drawings/generated.ts

`python3 tools/gen.py <out.html> tools/template.html` still builds the standalone mockup page.
