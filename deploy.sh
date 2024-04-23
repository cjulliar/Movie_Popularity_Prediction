#!/bin/sh
docker build -t jakimpact/niab-webapp ./webapp/.
docker push jakimpact/niab-webapp

az container create --resource-group RG_LAVALLEEQ --file deploy.yaml