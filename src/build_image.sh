#!/bin/bash

IMAGE_NAME="$1"
VERSION="$2"
FULL_IMAGE_NAME="gcr.io/united-impact-363519/${IMAGE_NAME}:${VERSION}"

docker buildx build --platform linux/amd64 -t ${FULL_IMAGE_NAME} .

docker push ${FULL_IMAGE_NAME}

gcloud run deploy --image ${FULL_IMAGE_NAME} --platform managed  --project=united-impact-363519 --allow-unauthenticated

# this did not completely work due to permissions issues reading from GCS with local container
# docker run --name mycontainer gcr.io/united-impact-363519/church_service_tracker:v1.0.0
# docker exec -it mycontainer sh
# docker stop mycontainer
# docker rm mycontainer