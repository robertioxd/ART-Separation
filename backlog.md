# ChromaScreen MVP Backlog (Agile)

## Phase 1: Core Processing Engine (AI + Engineering)

### 1-Core [Upscaling]
**Feature**: Restauración de imágenes de baja resolución.
- [ ] Implementar Real-ESRGAN (x4plus) para inputs con DPI < 300.
- [ ] **Acceptance Criteria**: La imagen de salida debe tener al menos 300 DPI efectivos sin artefactos JPEG visibles.

### 2-Core [Clustering & Pantone]
**Feature**: Separación de colores base (Sim Process).
- [ ] Implementar K-Means Clustering restringido a paleta Pantone Coated.
- [ ] Generar canales de color LAB.
- [ ] **Acceptance Criteria**: Los colores resultantes deben coincidir visualmente con la guía Pantone física.

### 3-Core [Dot Gain Compensation] (NUEVO)
**Feature**: Compensación de ganancia de punto para impresión textil.
- [ ] Crear función de Curva Inversa (LUT).
- [ ] Aplicar fórmula: `Out = In - (In * Gain%)`.
- [ ] **Acceptance Criteria**: Un parche del 50% debe medir 40-45% en el archivo final (dependiendo de la ganancia estimada).

### 4-Core [Breathable Underbase] (MEJORADO)
**Feature**: Base blanca que no se siente como "plástico".
- [ ] Invertir luminancia de la imagen original.
- [ ] Aplicar Threshold de Respirabilidad (< 30% Luma en Top Colors).
- [ ] Aplicar Choke (Erosion) de 1-2px.
- [ ] **Acceptance Criteria**: Las áreas negras de la imagen original deben ser transparentes en la base blanca.

### 5-Core [Vectorization]
**Feature**: Bordes perfectos para texto y formas sólidas.
- [ ] Integrar `potrace` para canales de alto contraste (Negro).
- [ ] Generar salida SVG.
- [ ] **Acceptance Criteria**: El SVG debe ser escalable infinitamente sin pixelación.

### 6-Core [Zero-RIP Engine] (CRÍTICO)
**Feature**: Generación de tramas de semitonos (Halftones) listas para imprimir.
- [ ] Implementar conversión a Bitmap de 1-bit.
- [ ] Configurar Trama Elíptica.
- [ ] Configurar Ángulos Estándar (22.5°, 61°, 45°).
- [ ] Configurar Frecuencia (45 LPI).
- [ ] **Acceptance Criteria**: El archivo PNG/TIFF final debe abrirse en el visor de Windows mostrando puntos definidos, sin grises.

## Phase 2: Backend Infrastructure & Delivery

### 7-Infra [Docker Environment]
**Feature**: Entorno de ejecución contenerizado.
- [ ] Configurar `docker-compose.yml` (FastAPI + Worker + Redis + MinIO/S3).
- [ ] Dockerfile Backend: Python 3.10 + OpenCV + Dependencies.
- [ ] Dockerfile Worker: Ghostscript + Potrace instalados a nivel OS.
- [ ] **Acceptance Criteria**: `docker-compose up` levanta todos los servicios sin errores de dependencia.

### 8-API [Job Management]
**Feature**: Gestión de trabajos de separación.
- [ ] Endpoint `POST /jobs` (Upload).
- [ ] Endpoint `GET /jobs/{id}` (Status Polling).
- [ ] Estructura de carpetas `/temp_jobs/{id}`.
- [ ] **Acceptance Criteria**: Subir una imagen retorna un Job ID y el worker comienza a procesar.

### 9-API [Data Contract]
**Feature**: Manifest.json para el frontend.
- [ ] Generar `manifest.json` al finalizar el procesamiento.
- [ ] Incluir rutas a Bitmaps, Grayscale y Vectores.
- [ ] **Acceptance Criteria**: El JSON debe cumplir estrictamente con el esquema definido en el SOP v1.2.

## QA & Validation

- [ ] **Print Test**: Imprimir un bitmap generado y verificar la trama con lupa/cuentahílos.
- [ ] **Touch Test**: Verificar visualmente la "respirabilidad" de la base blanca.
