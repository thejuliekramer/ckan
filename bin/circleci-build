#!/bin/sh
set -e

echo "This is circleci-build.sh..."

echo "-----------------------------------------------------------------"
echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install solr-jetty libcommons-fileupload-java libpq-dev postgresql postgresql-contrib

echo "-----------------------------------------------------------------"
echo "Installing CKAN and its dependencies..."

if [ $CKANVERSION == '2.8' ]
then
	git checkout 2.8
elif [ $CKANVERSION == '2.3' ]
then
	git checkout release-v2.3
elif [ $CKANVERSION == 'inventory' ]
then
	sudo apt-get install swig
	pip install testrepository
	git checkout inventory
elif [ $CKANVERSION == 'datagov' ]
then
	git checkout datagov
fi

echo "-----------------------------------------------------------------"
echo "Installing Python dependencies..."

pip install setuptools -U

python setup.py develop
# TODO remove after upgrading to CKAN 2.8
cp ./ckan/public/base/css/main.css ./ckan/public/base/css/main.debug.css
pip install wheel
pip install -r requirements.txt
pip install -r dev-requirements.txt

cd ..
echo "-----------------------------------------------------------------"
echo "Setting up Solr..."
# solr is multicore for tests on ckan master now, but it's easier to run tests
# on Travis single-core still.
# see https://github.com/ckan/ckan/issues/2972
sed -i -e 's/solr_url.*/solr_url = http:\/\/127.0.0.1:8983\/solr/' ckan/test-core.ini
printf "NO_START=0\nJETTY_HOST=127.0.0.1\nJETTY_PORT=8983\nJAVA_HOME=$JAVA_HOME" | sudo tee /etc/default/jetty
sudo cp ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
sudo service jetty restart

echo "-----------------------------------------------------------------"
echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'
sudo -u postgres psql -c 'CREATE DATABASE datastore_test WITH OWNER ckan_default;'

echo "-----------------------------------------------------------------"
echo "Initialising the database..."
cd ckan
paster db init -c test-core.ini



