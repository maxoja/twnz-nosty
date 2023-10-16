THIS_DIR=`realpath $0`

rm -rf ./dist
pyinstaller --onefile --noconsole run.py
mkdir -p ./dist/src
cp ./src/* ./dist/src

DATE_STR=`date +"%Y%m%d-%H%M%S"`
zip -r ./dist/mac-$DATE_STR.zip ./dist