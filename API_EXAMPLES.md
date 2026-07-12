# 📚 Ejemplos de API - Face + Bib Detection

## Configuración actual (solo caras)

### Request
```bash
curl -X POST https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync \
  -H "Authorization: Bearer {RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "images": [
        {
          "id": "photo_001",
          "url": "https://cdn.example.com/runner1.jpg"
        }
      ]
    }
  }'
```

### Response
```json
{
  "output": {
    "results": [
      {
        "id": "photo_001",
        "faces_count": 1,
        "faces": [
          {
            "face_index": 0,
            "embedding": [0.123, -0.456, ...],
            "confidence": 0.98
          }
        ],
        "error": null
      }
    ]
  }
}
```

---

## Con detección de dorsales (NUEVO)

### 1. Solo dorsales (`mode: "bib"`)

```bash
curl -X POST https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync \
  -H "Authorization: Bearer {RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "mode": "bib",
      "images": [
        {
          "id": "race_photo_123",
          "url": "https://cdn.photosports.com/marathon/img_001.jpg"
        }
      ]
    }
  }'
```

**Response:**
```json
{
  "output": {
    "results": [
      {
        "id": "race_photo_123",
        "bibs_count": 3,
        "bibs": [
          {
            "number": "12345",
            "confidence": 0.98,
            "bbox": [[450, 320], [520, 320], [520, 380], [450, 380]]
          },
          {
            "number": "789",
            "confidence": 0.95,
            "bbox": [[650, 340], [710, 340], [710, 395], [650, 395]]
          },
          {
            "number": "42",
            "confidence": 0.89,
            "bbox": [[200, 280], [245, 280], [245, 320], [200, 320]]
          }
        ],
        "error": null
      }
    ]
  }
}
```

---

### 2. Caras + Dorsales (`mode: "both"`)

**Caso de uso**: Asociar runners con sus dorsales en una sola llamada

```bash
curl -X POST https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync \
  -H "Authorization: Bearer {RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "mode": "both",
      "images": [
        {
          "id": "finish_line_001",
          "url": "https://cdn.photosports.com/finish/img_100.jpg"
        }
      ]
    }
  }'
```

**Response:**
```json
{
  "output": {
    "results": [
      {
        "id": "finish_line_001",
        "faces_count": 2,
        "faces": [
          {
            "face_index": 0,
            "embedding": [0.123, -0.456, ...],
            "confidence": 0.99
          },
          {
            "face_index": 1,
            "embedding": [0.789, -0.234, ...],
            "confidence": 0.97
          }
        ],
        "bibs_count": 2,
        "bibs": [
          {
            "number": "12345",
            "confidence": 0.98,
            "bbox": [[450, 320], [520, 320], [520, 380], [450, 380]]
          },
          {
            "number": "67890",
            "confidence": 0.96,
            "bbox": [[750, 310], [820, 310], [820, 370], [750, 370]]
          }
        ],
        "error": null
      }
    ]
  }
}
```

---

### 3. Batch processing - Múltiples imágenes

```bash
curl -X POST https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync \
  -H "Authorization: Bearer {RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "mode": "both",
      "images": [
        {"id": "img_001", "url": "https://cdn.photosports.com/race/001.jpg"},
        {"id": "img_002", "url": "https://cdn.photosports.com/race/002.jpg"},
        {"id": "img_003", "url": "https://cdn.photosports.com/race/003.jpg"}
      ]
    }
  }'
```

---

## 🎯 Casos de uso en Lovable

### Caso 1: Indexación de carrera completa

```javascript
// En tu frontend de Lovable
const indexRacePhotos = async (photoUrls) => {
  const response = await fetch(`https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${RUNPOD_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: {
        mode: 'both',  // Detectar caras Y dorsales
        images: photoUrls.map((url, idx) => ({
          id: `photo_${idx}`,
          url
        }))
      }
    })
  });

  const data = await response.json();

  // Guardar en base de datos: face embeddings + dorsal numbers
  for (const result of data.output.results) {
    await saveToDatabase({
      photoId: result.id,
      faces: result.faces,
      bibNumbers: result.bibs.map(b => b.number)
    });
  }
};
```

### Caso 2: Búsqueda de runner por selfie

```javascript
// Usuario sube selfie → encuentra sus fotos por dorsal
const findRunnerPhotos = async (selfieBase64, bibNumber) => {
  // 1. Obtener embedding del selfie
  const selfieResponse = await fetch(`https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${RUNPOD_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: {
        mode: 'face',
        image: selfieBase64
      }
    })
  });

  const selfieData = await selfieResponse.json();
  const selfieEmbedding = selfieData.output.embedding;

  // 2. Buscar en DB: fotos con ese dorsal + similitud facial
  const candidatePhotos = await db.query(
    'SELECT * FROM race_photos WHERE bib_number = ?',
    [bibNumber]
  );

  // 3. Filtrar por similitud facial (cosine similarity)
  const matchedPhotos = candidatePhotos.filter(photo => {
    const similarity = cosineSimilarity(selfieEmbedding, photo.face_embedding);
    return similarity > 0.6;  // Threshold
  });

  return matchedPhotos;
};
```

### Caso 3: Validación de dorsal

```javascript
// Verificar que el dorsal en la foto corresponde al runner registrado
const validateBib = async (photoUrl, expectedBibNumber) => {
  const response = await fetch(`https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${RUNPOD_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: {
        mode: 'bib',
        images: [{ id: 'validation', url: photoUrl }]
      }
    })
  });

  const data = await response.json();
  const detectedBibs = data.output.results[0].bibs;

  // Verificar si el dorsal esperado está en la foto
  const bibMatch = detectedBibs.find(
    bib => bib.number === expectedBibNumber && bib.confidence > 0.7
  );

  return {
    valid: !!bibMatch,
    confidence: bibMatch?.confidence || 0,
    allDetected: detectedBibs.map(b => b.number)
  };
};
```

---

## ⚙️ Parámetros

| Parámetro | Tipo | Valores | Default | Descripción |
|-----------|------|---------|---------|-------------|
| `mode` | string | `"face"`, `"bib"`, `"both"` | `"face"` | Qué detectar |
| `images` | array | `[{id, url}]` | - | Batch de imágenes |
| `image` | string | base64 | - | Single imagen |

---

## 🚀 Performance

| Operación | Tiempo (GPU) | Notas |
|-----------|--------------|-------|
| Solo caras | ~0.5-1s | InsightFace buffalo_l |
| Solo dorsales | ~0.3-0.8s | PaddleOCR |
| Ambos | ~0.8-1.5s | Paralelo en GPU |
| Batch (10 imgs) | ~2-3s | ThreadPool con 10 workers |

---

## 📊 Estructura de bbox

Los bounding boxes de dorsales son coordenadas de 4 puntos (pueden estar rotados):

```
[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
```

Ejemplo para dibujar en canvas:
```javascript
const drawBib = (ctx, bbox, number) => {
  ctx.beginPath();
  ctx.moveTo(bbox[0][0], bbox[0][1]);
  bbox.forEach(([x, y]) => ctx.lineTo(x, y));
  ctx.closePath();
  ctx.stroke();

  // Dibujar número
  ctx.fillText(number, bbox[0][0], bbox[0][1] - 10);
};
```
