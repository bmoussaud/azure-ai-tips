#!/bin/bash
set -x
analyzerId=$1
analyzerConfig=$2
endpoint=${AI_RESOURCE_ENDPOINT}
key=${AI_RESOURCE_KEY}

echo "List analyzers"
mktmpfile=$(mktemp)


# Usage:
# ./create_analyzer.sh <analyzerId> <analyzerConfig>
# For example, to create an analyzer with the configuration in the file "analyzer-config.json":
# ./create_analyzer.sh content-understanding/custom_video_analyser.json
# Create an analyzer
curl -X GET "${endpoint}/contentunderstanding/analyzers?api-version=2024-12-01-preview" -H "Ocp-Apim-Subscription-Key: ${key}" --output ${mktmpfile}
cat ${mktmpfile} |jq
