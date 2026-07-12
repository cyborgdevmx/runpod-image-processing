"""
Script de prueba para detección de números de dorsal usando PaddleOCR
Esto es un prototipo para evaluar la viabilidad antes de integrarlo a RunPod
"""

import cv2
import numpy as np
from paddleocr import PaddleOCR
import requests
from io import BytesIO

# Inicializar PaddleOCR (solo necesita hacerse una vez)
# use_angle_cls=True ayuda con texto rotado (dorsales en movimiento)
# lang='en' porque los dorsales son números
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True, show_log=False)


def download_image(url):
    """Descarga imagen desde URL"""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        img_array = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error descargando imagen: {e}")
        return None


def detect_bib_numbers(image):
    """
    Detecta números de dorsal en una imagen

    Returns:
        List[dict]: Lista de dorsales detectados con:
            - number: string del número detectado
            - confidence: confianza de la detección (0-1)
            - bbox: coordenadas [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    """
    # PaddleOCR devuelve: [[[bbox], (text, confidence)], ...]
    result = ocr.ocr(image, cls=True)

    if not result or not result[0]:
        return []

    bib_numbers = []

    for detection in result[0]:
        bbox, (text, confidence) = detection

        # Filtrar solo números (dorsales típicamente son numéricos)
        # Remover espacios y caracteres no numéricos
        cleaned_text = ''.join(filter(str.isdigit, text))

        # Solo considerar si:
        # 1. Tiene al menos un dígito
        # 2. Confianza > 0.5
        # 3. Longitud razonable para un dorsal (1-5 dígitos típicamente)
        if cleaned_text and confidence > 0.5 and 1 <= len(cleaned_text) <= 5:
            bib_numbers.append({
                "number": cleaned_text,
                "confidence": float(confidence),
                "bbox": bbox,
                "raw_text": text  # texto original antes de limpiar
            })

    # Ordenar por confianza (mayor primero)
    bib_numbers.sort(key=lambda x: x['confidence'], reverse=True)

    return bib_numbers


def visualize_detections(image, detections):
    """
    Dibuja los dorsales detectados en la imagen (para debugging)
    """
    img_copy = image.copy()

    for det in detections:
        bbox = np.array(det['bbox'], dtype=np.int32)
        number = det['number']
        confidence = det['confidence']

        # Dibujar bounding box
        cv2.polylines(img_copy, [bbox], True, (0, 255, 0), 2)

        # Dibujar texto
        text = f"#{number} ({confidence:.2f})"
        cv2.putText(img_copy, text, tuple(bbox[0]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    return img_copy


# ============================================
# PRUEBAS
# ============================================

if __name__ == "__main__":
    print("🏃 Iniciando prueba de detección de dorsales...")

    # Opción 1: Desde archivo local
    # img = cv2.imread("path/to/your/image.jpg")

    # Opción 2: Desde URL (ejemplo)
    # Puedes usar una imagen de prueba de internet o tu propio storage
    test_url = "https://example.com/sports-photo.jpg"  # Reemplaza con tu URL

    print(f"📥 Descargando imagen de prueba...")
    # Para pruebas rápidas, usaremos una imagen local si existe
    import os
    if os.path.exists("test_image.jpg"):
        img = cv2.imread("test_image.jpg")
        print("✅ Usando imagen local: test_image.jpg")
    else:
        print("⚠️  No se encontró test_image.jpg")
        print("   Coloca una imagen de prueba en el directorio actual como 'test_image.jpg'")
        print("   O modifica el script para usar una URL")
        exit(1)

    if img is None:
        print("❌ Error cargando imagen")
        exit(1)

    print(f"📐 Tamaño de imagen: {img.shape[1]}x{img.shape[0]}")

    # Detectar dorsales
    print("🔍 Detectando números de dorsal...")
    detections = detect_bib_numbers(img)

    print(f"\n✅ Dorsales detectados: {len(detections)}")
    print("=" * 60)

    for i, det in enumerate(detections, 1):
        print(f"\nDorsal #{i}:")
        print(f"  Número: {det['number']}")
        print(f"  Confianza: {det['confidence']:.2%}")
        print(f"  Texto original: '{det['raw_text']}'")
        print(f"  Bbox: {det['bbox']}")

    # Guardar imagen con detecciones visualizadas
    if detections:
        img_with_boxes = visualize_detections(img, detections)
        cv2.imwrite("output_bib_detection.jpg", img_with_boxes)
        print(f"\n💾 Imagen con detecciones guardada en: output_bib_detection.jpg")

    print("\n" + "=" * 60)
    print("🎯 Prueba completada!")
