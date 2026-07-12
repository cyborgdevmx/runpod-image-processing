# 🏃 Prueba de Detección de Dorsales

## Objetivo
Probar la detección de números de dorsal en fotos deportivas usando PaddleOCR antes de integrar a RunPod.

## 🚀 Instalación

```bash
# Instalar dependencias
pip install -r requirements_bib_test.txt
```

**Nota**: Si no tienes GPU disponible localmente, cambia `paddlepaddle-gpu` por `paddlepaddle` en requirements_bib_test.txt

## 📸 Preparar imagen de prueba

1. Consigue una foto deportiva con dorsales visibles
2. Guárdala como `test_image.jpg` en este directorio

**O** modifica el script para usar una URL directamente.

## ▶️ Ejecutar prueba

```bash
python test_bib_detection.py
```

## 📊 Salida esperada

El script:
1. Carga la imagen
2. Detecta todos los números de dorsal
3. Muestra los resultados en consola
4. Guarda `output_bib_detection.jpg` con los dorsales marcados

Ejemplo de salida:
```
🏃 Iniciando prueba de detección de dorsales...
✅ Usando imagen local: test_image.jpg
📐 Tamaño de imagen: 1920x1080
🔍 Detectando números de dorsal...

✅ Dorsales detectados: 3
============================================================

Dorsal #1:
  Número: 123
  Confianza: 98.50%
  Texto original: '123'
  Bbox: [[450, 320], [520, 320], [520, 380], [450, 380]]

Dorsal #2:
  Número: 456
  Confianza: 95.20%
  ...
```

## 🎯 Evaluación

Después de la prueba, evalúa:

✅ **Precisión**: ¿Detecta correctamente los dorsales?
✅ **Recall**: ¿Encuentra todos los dorsales en la imagen?
✅ **Falsos positivos**: ¿Detecta cosas que no son dorsales?
✅ **Velocidad**: ¿Qué tan rápido procesa?

## 📝 Casos de prueba recomendados

1. **Imagen clara, frente**: Dorsal completamente visible
2. **Múltiples atletas**: Varios dorsales en una foto
3. **Ángulo lateral**: Dorsal parcialmente visible
4. **Movimiento/blur**: Foto con motion blur
5. **Baja resolución**: Imagen comprimida/pequeña

## 🔧 Ajustes disponibles

En `test_bib_detection.py` puedes ajustar:

```python
# Confianza mínima (default: 0.5)
if confidence > 0.5:  # Cambiar a 0.7 para ser más estricto

# Longitud de dorsal esperada (default: 1-5 dígitos)
if 1 <= len(cleaned_text) <= 5:  # Ajustar según tu caso

# GPU/CPU
ocr = PaddleOCR(use_gpu=True)  # False para CPU
```

## ⚡ Próximos pasos

Si la prueba funciona bien:

1. **Opción A**: Crear endpoint separado en RunPod para dorsales
2. **Opción B**: Extender el endpoint actual para hacer caras + dorsales
3. **Opción C**: Crear pipeline híbrido que asocie caras con dorsales

## 🐛 Troubleshooting

**Error: "No module named 'paddle'"**
```bash
pip install paddlepaddle-gpu  # o paddlepaddle para CPU
```

**Error: GPU not found**
- Cambia `use_gpu=True` a `use_gpu=False` en el script
- O instala `paddlepaddle` en lugar de `paddlepaddle-gpu`

**Detecciones pobres**
- Verifica calidad de la imagen (resolución, nitidez)
- Ajusta el threshold de confianza
- Considera preprocesamiento de imagen (contraste, sharpening)
