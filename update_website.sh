#!/bin/bash -xe

# add any argv[1], e.g., "stage-only", to avoid updating the live
# website

echo "Start update_website $@: `date '+%Y%m%d_%H%M%S'`"

SCRIPT_DIR=$(dirname $(readlink -e $0))
SPHINX_DIR=/home/mark/development/sphinx_work/sphinx_covid

cd $SCRIPT_DIR
find . -name ".git" -prune -o -type f -name "*~" -exec rm -f {} \;

pipenv run ./covid19_analytics/covid19 get_data -w ../covid19_runtime_data -R ~/development/covid19_study/COVID-19_JohnsHopkins -d ~/development/covid19_study/covid19_analytics/locations.json

pipenv run ./covid19_analytics/covid19 create_plots -w ../covid19_runtime_data -j

cd $SPHINX_DIR

pipenv run ./auto_update.py ~/development/covid19_study/covid19_runtime_data

./build_and_ship.sh $@

echo "Done update_website $@: `date '+%Y%m%d_%H%M%S'`"
