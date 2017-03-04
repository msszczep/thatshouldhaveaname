export MYPROJECT="CHANGEME"
rm -rf $MYPROJECT
mkdir $MYPROJECT
cd $MYPROJECT
echo "$MYPROJECT directory created..."
echo ""
virtualenv venv
. venv/bin/activate
echo "$MYPROJECT virtualenv created and activated..."
echo ""
cp ../thatshouldhaveaname/requirements.txt .
cp ../thatshouldhaveaname/schema.sql .
cp ../thatshouldhaveaname/thatshouldhaveaname.py .
#cp ../tshan_template/thatshouldhaveaname.db .
cp -R ../thatshouldhaveaname/static .
cp -R ../thatshouldhaveaname/templates .
echo "$MYPROJECT source files copied..."
echo ""
venv/bin/pip install -r requirements.txt
echo "$MYPROJECT requirements loaded..."
echo ""
export FLASK_APP=thatshouldhaveaname.py
export FLASK_DEBUG=1
sqlite3 thathshouldhaveaname.db < schema.sql
flask initdb
echo "db initiated..."
echo ""
flask run
