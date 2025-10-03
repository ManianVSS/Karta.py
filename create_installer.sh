#!/bin/bash
source .venv/bin/activate

rm -rf build/ dist/
pyinstaller --hidden-import karta.plugins.dependency_injector --hidden-import karta.plugins.kriya --hidden-import karta.plugins.gherkin --contents-directory lib -n karta main.py
#pyinstaller installer.spec
#--add-data "templates:."
cp -r features dist/karta
cp -r framework dist/karta
cp -r properties dist/karta
cp -r templates dist/karta
cp -r step_definitions dist/karta

cd dist/ || exit
tar -czvf karta.tar.gz karta
cd - || exit

