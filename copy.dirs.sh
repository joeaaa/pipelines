#!/bin/sh

./gradlew dist

TEST_DIR=../data/testfiles/docker-services
if [ ! -d ${TEST_DIR} ]; then
        echo "Creating docker-services dir (${TEST_DIR})"
        mkdir -p ${TEST_DIR} || exit 1
fi

DEPLOY_DIR=../docker/deploy/data/docker-services
if [ ! -d ${DEPLOY_DIR} ]; then
        echo "Creating docker-services dir (${DEPLOY_DIR})"
        mkdir -p ${DEPLOY_DIR} || exit 1
fi

rm -rf ${TEST_DIR}/pipelines ${TEST_DIR}/nextflow
cp -r build/dist/pipelines ${TEST_DIR}
cp -r build/dist/nextflow ${TEST_DIR}
echo "Files copied to ${TEST_DIR}"

rm -rf ${DEPLOY_DIR}/pipelines ${DEPLOY_DIR}/nextflow
cp -r build/dist/pipelines ${DEPLOY_DIR}
cp -r build/dist/nextflow ${DEPLOY_DIR}
echo "Files copied to ${DEPLOY_DIR}"
