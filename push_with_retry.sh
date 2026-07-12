#!/bin/bash

# Script para hacer push a Docker Hub con reintentos automáticos
# Uso: ./push_with_retry.sh

IMAGE="om1001/runpod-face-processing:gpu-enabled"
MAX_ATTEMPTS=10
ATTEMPT=1

echo "🚀 Iniciando push de $IMAGE con reintentos automáticos..."
echo ""

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "📦 Intento $ATTEMPT de $MAX_ATTEMPTS..."

    if docker push "$IMAGE"; then
        echo "✅ Push completado exitosamente!"
        exit 0
    else
        EXIT_CODE=$?
        echo "❌ Push falló con código $EXIT_CODE"

        if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
            WAIT_TIME=$((ATTEMPT * 5))
            echo "⏳ Esperando ${WAIT_TIME}s antes de reintentar..."
            sleep $WAIT_TIME
        fi
    fi

    ATTEMPT=$((ATTEMPT + 1))
done

echo "💥 Push falló después de $MAX_ATTEMPTS intentos"
exit 1
