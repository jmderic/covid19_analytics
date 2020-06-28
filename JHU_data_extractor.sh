#!/bin/bash -e

NAME_TOKEN=$1
# confirmed or deaths

FILE_NAME=time_series_covid19_${NAME_TOKEN}_US.csv
# time_series_covid19_confirmed_US.csv or time_series_covid19_deaths_US.csv

FILE_DIR=/home/mark/development/covid19_study/COVID-19_JohnsHopkins/csse_covid_19_data/csse_covid_19_time_series

pushd $FILE_DIR > /dev/null
git checkout master > /dev/null  2>&1
if ! git pull > /dev/null 2>&1; then
    echo "exiting on failed git pull"
    exit 1
fi
popd  > /dev/null

grep -E ",(\"Orange, California, US\"|Combined_Key)," $FILE_DIR/$FILE_NAME > results_$NAME_TOKEN.csv
