#!/bin/bash
set -x
analyzerId=$1
fileUrl=$2
endpoint=${AI_RESOURCE_ENDPOINT}
key=${AI_RESOURCE_KEY}

echo "Analyse using ${analyzerId} : ${fileUrl}"
service_endpoint="${endpoint}/contentunderstanding/analyzers/${analyzerId}:analyze?api-version=2024-12-01-preview"
echo "Service endpoint: ${service_endpoint}"
# Trigger 
curl -i -X POST ${service_endpoint} \
  -H "Ocp-Apim-Subscription-Key: ${key}" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"${fileUrl}\"}" 
  
