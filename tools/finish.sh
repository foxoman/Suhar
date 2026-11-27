#!/bin/sh
# full pipeline: build -> validate -> docs -> Nim test -> samples -> packages
set -e
cd "$(dirname "$0")/.."
rm -rf dist
(cd src && python3 -m retrofont.build --out ../dist)
python3 tools/print_proof.py
python3 tools/validate.py
python3 tools/make_docs.py
mkdir -p nim/fonts reports/samples
cp dist/ttf/SuharNaskh-Regular.ttf dist/ttf/SuharNaskh-Bold.ttf dist/ttf/Suhar-Regular.ttf dist/ttf/Suhar-Bold.ttf dist/ttf/Suhar-Italic.ttf dist/ttf/Suhar-BoldItalic.ttf dist/ttf/SuharMono-Regular.ttf dist/ttf/SuharMono-Bold.ttf dist/ttf/SuharMono-Italic.ttf dist/ttf/SuharMono-BoldItalic.ttf nim/fonts/
if [ -n "$NIM" ] && [ -n "$RETROUI" ]; then
  (cd nim && "$NIM" c -r --hints:off --warnings:off --path:"$RETROUI/src" --path:"$RETROUI/tests" -d:useMalloc --nimcache:/tmp/nc tests/tload.nim | tail -1 > ../reports/nim-test.txt; rm -f tests/tload)
fi
python3 tools/sample_paragraphs.py reports/samples/Suhar-mixed-paragraphs.png
python3 tools/sample_editor.py reports/samples/Suhar-mono-editor.png
python3 tools/sample_languages.py reports/samples/Suhar-languages.png
python3 tools/sample_v13.py dist/ttf reports/samples/Suhar-1.3-additions.png named
python3 tools/readme_images.py
echo PIPELINE-DONE
