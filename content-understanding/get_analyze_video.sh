#!/bin/bash
# Usage:
# ./get_analyze_video.sh <analyzerId> <resultId>
# For example, to get the result of the analyzer with id "content-understanding-custom-video-analyser" and result id "result-1":
# ./get_analyze_video.sh content-understanding-custom-video-analyser result-1

set -x
analyzerId=$1
resultId=$2
endpoint=${AI_RESOURCE_ENDPOINT}
key=${AI_RESOURCE_KEY}

echo "Get the result of ${analyzerId}/${resultId}"
mkdir -p results

curl  -X GET "${endpoint}/contentunderstanding/analyzers/${analyzerId}/results/${resultId}?api-version=2024-12-01-preview" -H "Ocp-Apim-Subscription-Key: ${key}" --output results/${resultId}.json
cat results/${resultId}.json |jq
