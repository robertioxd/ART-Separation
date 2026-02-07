# **SOP-DEV-001: Desarrollo de MVP "ChromaScreen AI"**

**Proyecto:** ChromaScreen AI (SaaS de Separación de Color Textil)

**Versión:** 1.1 (Actualizado con Vectorización Híbrida y Manifest Contract)

**Fecha de Emisión:** 06/02/2026

**Responsable:** Lead Product Manager / Engineering Lead

**Estado:** Aprobado para Ejecución

## **1\. Objetivo del Procedimiento**

Desarrollar y desplegar un MVP (Producto Mínimo Viable) funcional que permita a un usuario subir una imagen rasterizada y obtener una separación de colores simulada (Sim Process) optimizada para serigrafía textil.

El sistema debe diferenciarse de la competencia entregando una solución **Híbrida (Raster \+ Vector)**, donde las imágenes fotográficas se separan en píxeles (halftones) y los trazos definidos (textos/líneas) se vectorizan automáticamente.

## **2\. Stack Tecnológico Definido**

### **Frontend (Cliente)**

* **Framework:** React.js (Vite).  
* **Motor Gráfico:** Fabric.js (para manipulación de Canvas, capas y blend modes).  
* **UI Kit:** TailwindCSS \+ Shadcn/UI.

### **Backend (API & Orquestación)**

* **Lenguaje:** Python 3.10+.  
* **API Framework:** FastAPI (Asíncrono).  
* **Cola de Tareas:** Celery.  
* **Broker:** Redis.  
* **Base de Datos:** PostgreSQL (Usuarios, Logs de Jobs).  
* **Storage:** AWS S3 (o MinIO local) para archivos temporales.

### **Motor de IA y Procesamiento (The "Black Box")**

* **Restauración:** Real-ESRGAN (Pesos pre-entrenados via realesrgan library).  
* **Visión/Clustering:** OpenCV (cv2), Scikit-learn (KMeans), NumPy.  
* **Vectorización:** Potrace (via pypotrace bindings).  
* **Manipulación de Archivos:** Pillow (Imágenes), ReportLab (Generación de PDF).

## **3\. Arquitectura del Flujo de Datos**

1. **Upload:** Cliente sube imagen \-\> API Gateway \-\> S3 (Bucket raw\_uploads).  
2. **Queue:** API genera un job\_id y envía la tarea a Celery (Redis).  
3. **Worker Processing:**  
   * Descarga imagen.  
   * Ejecuta Pipeline de IA.  
   * Genera archivos en disco temporal.  
   * Escribe manifest.json.  
   * Sube resultados a S3 (Bucket processed\_jobs).  
4. **Polling/Webhook:** Cliente consulta estado \-\> Recibe manifest.json \-\> Renderiza vista previa.

## **4\. Fases de Desarrollo (Sprints)**

### **FASE 1: Ingeniería de Datos y Pipeline de IA (Core)**

**Objetivo:** Construir el script de Python que recibe una imagen sucia y devuelve carpetas con separaciones.

#### **Paso 1.1: Restauración y Pre-procesamiento**

* **Input:** Imagen RGB (posiblemente baja resolución, ruidosa).  
* **Lógica:**  
  * Verificar resolución. Si es \< 300 DPI, aplicar **Real-ESRGAN**.  
  * Normalizar tamaño y contraste.  
* **Librería:** realesrgan.

#### **Paso 1.2: Clustering de Colores (Sim Process)**

* **Input:** Imagen restaurada \+ max\_colors (int) \+ apparel\_color (hex).  
* **Lógica:**  
  1. Convertir imagen a espacio de color **LAB** (para mejor percepción humana).  
  2. Ejecutar **K-Means Clustering** restringido a max\_colors.  
  3. **Color Mapping:** Mapear los centroides resultantes a la biblioteca de colores más cercana (ej. Pantone Solid Coated o Tintas Wilflex).  
  4. Extraer máscaras binarias para cada clúster.

#### **Paso 1.3: Lógica de Base Blanca (Underbase)**

* **Requisito Crítico:** La base blanca es fundamental para camisetas oscuras.  
* **Lógica:**  
  1. Invertir la luminancia de la imagen original compuesta.  
  2. Generar máscara de escala de grises.  
  3. **Choking (Contracción):** Aplicar cv2.erode (1-2px) a la máscara blanca. Esto evita que la tinta blanca se asome por debajo de los colores (problema de registro).

#### **Paso 1.4: Vectorización Híbrida (Potrace)**

* **Lógica:**  
  * Para canales identificados como "Negro" (Líneas/Texto) o "Base Blanca Sólida":  
  * Ejecutar potrace sobre el bitmap para generar un path SVG.  
  * *Beneficio:* Permite descargar archivos escalables para positivos de alta calidad.

### **FASE 2: Backend y Estandarización de Salida**

**Objetivo:** Empaquetar el resultado de la IA en un formato consumible por el Frontend y el Usuario Final.

#### **Paso 2.1: Estructura de Directorios del Job**

El Worker debe organizar los archivos resultantes de la siguiente manera antes de subirlos a S3:

/temp\_jobs/{job\_id}/  
├── manifest.json                \<-- ARCHIVO CRÍTICO (Ver Paso 2.2)  
├── preview\_composite.jpg        \<-- Imagen RGB optimizada para web (Thumbnail)  
├── /separations\_raster/         \<-- Para quemado en malla estándar (Sim Process)  
│   ├── 01\_Underbase.png         (PNG-8 con transparencia o Grayscale)  
│   ├── 02\_Pantone\_186C.png  
│   ├── 03\_Pantone\_286C.png  
│   └── 04\_Highlight\_White.png  
└── /separations\_vector/         \<-- Para corte o alta definición  
    ├── 01\_Underbase.svg  
    └── 03\_Black\_Outline.svg     (Solo si aplica vectorización)

#### **Paso 2.2: El Contrato de Datos (manifest.json)**

El Backend **NO** envía imágenes procesadas al frontend para renderizar. Envía este JSON. El Frontend usa este JSON para saber qué pedir y cómo dibujarlo.

{  
  "job\_id": "550e8400-e29b-41d4-a716-446655440000",  
  "status": "completed",  
  "input\_file": "tiger\_design.png",  
  "bg\_color": "\#000000",  
  "print\_order": \["Underbase", "Flash", "Red", "Blue", "Highlight"\],  
  "separations": \[  
    {  
      "index": 1,  
      "name": "Underbase White",  
      "type": "Underbase",  
      "hex\_preview": "\#E0E0E0",  
      "pantone\_ref": null,  
      "mesh\_recommendation": 156,  
      "angle": 22.5,  
      "files": {  
        "raster": "https://s3.../jobs/{id}/separations\_raster/01\_Underbase.png",  
        "vector": "https://s3.../jobs/{id}/separations\_vector/01\_Underbase.svg"  
      },  
      "visible": true  
    },  
    {  
      "index": 2,  
      "name": "Red 032 C",  
      "type": "Spot",  
      "hex\_preview": "\#EF3340",  
      "pantone\_ref": "PANTONE 186 C",  
      "mesh\_recommendation": 230,  
      "angle": 52.5,  
      "files": {  
        "raster": "https://s3.../jobs/{id}/separations\_raster/02\_Red.png",  
        "vector": null  
      },  
      "visible": true  
    }  
  \]  
}

#### **Paso 2.3: Generación de Descargables (ZIP)**

* El sistema debe generar un ZIP que contenga la estructura de carpetas anterior.  
* **Opcional (Pro):** Generar un PDF multipágina usando ReportLab donde cada página es un canal en Negro 100% e incluye **Marcas de Registro** (Cruces en las esquinas) y etiqueta con el nombre del color.

### **FASE 3: Frontend y Experiencia de Usuario**

**Objetivo:** Visualizador interactivo.

#### **Paso 3.1: Canvas de Previsualización**

* Utilizar **Fabric.js**.  
* Dibujar un rectángulo de fondo con el color de la camiseta (bg\_color del manifest).  
* Iterar sobre el array separations del manifest.  
* Por cada separación, cargar la imagen files.raster.  
* **CRÍTICO:** Aplicar un tinte (Tint) usando el hex\_preview y establecer el modo de mezcla (blend mode) en MULTIPLY (para simular tintas translúcidas) o NORMAL (para tintas opacas como el Plastisol base).

#### **Paso 3.2: Controles de Usuario**

* **Ocultar/Mostrar:** Toggle para apagar capas (ej. ver cómo queda sin la base blanca).  
* **Unir Colores (Merge):** Si el usuario arrastra el "Rojo Fuego" sobre el "Rojo Ladrillo", el Frontend envía una petición al API para fusionar esos canales y regenerar el manifest.

## **5\. Criterios de Aceptación (QA)**

Antes de pasar a producción, el MVP debe aprobar estos casos de prueba:

1. **Prueba de "Basura de Entrada":**  
   * Subir un JPG de 72 DPI pixelado.  
   * *Resultado:* El sistema aplica Real-ESRGAN y devuelve bordes suaves en la separación.  
2. **Prueba de Camiseta Negra:**  
   * Subir un diseño colorido.  
   * *Resultado:* El canal 1 debe ser una Base Blanca invertida y contraída (choked).  
3. **Prueba de Vectorización:**  
   * Subir un logo con texto negro.  
   * *Resultado:* La carpeta /separations\_vector debe contener el SVG del texto, perfectamente escalable.  
4. **Prueba de Registro:**  
   * Descargar el PDF final.  
   * *Resultado:* Las marcas de registro (cruces) en la Página 1 deben alinear perfectamente con las de la Página 4 al superponerlas.

## **6\. Comandos de Despliegue Rápido**

El equipo debe entregar un docker-compose.yml que permita levantar el entorno localmente con:

\# Levantar servicios (API, Worker, Redis, DB, Frontend)  
docker-compose up \--build

\# Verificar logs del worker de IA  
docker-compose logs \-f celery\_worker  
