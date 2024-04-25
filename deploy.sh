#!/bin/sh
docker build -t jakimpact/niab-webapp ./webapp/.
docker push jakimpact/niab-webapp

docker build -t jakimpact/niab-cron ./scrapper/.
docker push jakimpact/niab-cron

az container create --resource-group RG_LAVALLEEQ --file deploy.yaml