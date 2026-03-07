#!/usr/bin/env bash

REMOTE_URL="http://${REMOTE_IP}:4000/v1"


exec interpreter \
  --api_base "${REMOTE_URL}" \
  --model "${MODEL}"
