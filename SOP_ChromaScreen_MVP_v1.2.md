# **SOP-DEV-001: Desarrollo de MVP "ChromaScreen AI"**

**Proyecto:** ChromaScreen AI (SaaS de Separación de Color Textil)

**Versión:** 1.2 (Industrial Grade \- Incluye Ripping y Compensación Física)

**Fecha de Emisión:** 06/02/2026

**Responsable:** Lead Product Manager / Engineering Lead

**Estado:** Aprobado para Ejecución

## **1\. Objetivo del Procedimiento**

Desarrollar y desplegar un MVP funcional que permita a un usuario subir una imagen rasterizada y obtener una separación de colores simulada (Sim Process) lista para producción.

**Diferencial Competitivo:**

El sistema entrega una solución **"Zero-RIP"**: Además de los canales estándar, genera archivos **Bitmapped (pre-tramados)** listos para imprimir en impresoras inkjet estándar sin necesidad de software externo costoso.

## **2\. Stack Tecnológico**

### **Frontend (Cliente)**

* **Framework:** React.js (Vite).  
* **Motor Gráfico:** Fabric.js (Preview con simulación de mezcla de tintas).  
* **UI Kit:** TailwindCSS \+ Shadcn/UI.

### **Backend (API & Orquestación)**

* **Lenguaje:** Python 3.10+.  
* **API Framework:** FastAPI.  
* **Cola:** Celery \+ Redis.  
* **Storage:** AWS S3.

### **Motor de Procesamiento (The "Black Box")**

* **Restauración:** Real-ESRGAN.  
* **Visión:** OpenCV, Scikit-learn, NumPy.  
* **Ripping (NUEVO):** Pillow (PIL) para Dithering o Ghostscript (via subprocess) para tramas AM reales (elípticas).  
* **Vectorización:** Potrace.

## **3\. Arquitectura del Flujo de Datos**

1. **Upload:** Cliente sube imagen \-\> S3.  
2. **Worker Processing:**  
   * Restauración (Upscaling).  
   * Separación (Clustering).  
   * **Compensación de Ganancia** (NUEVO).  
   * **Generación de Tramas/RIP** (NUEVO).  
   * Vectorización (Híbrida).  
3. **Delivery:** JSON Manifest \+ ZIP con carpetas organizadas.

## **4\. Fases de Desarrollo (Sprints)**

### **FASE 1: Ingeniería de Datos y Pipeline de IA (Core)**

#### **Paso 1.1: Restauración (Upscaling)**

* Si resolución \< 300 DPI \-\> Ejecutar Real-ESRGAN.

#### **Paso 1.2: Clustering con Compensación Física (MEJORADO)**

* **Input:** Imagen LAB.  
* **Proceso:**  
  1. K-Means Clustering (restringido a paleta Pantone).  
  2. **Dot Gain Compensation (LUT):** Antes de generar el canal final, aplicar una curva inversa.  
     * *Regla:* Valor\_Salida \= Valor\_Entrada \- (Valor\_Entrada \* %\_Ganancia\_Estimada).  
     * *Ejemplo:* Si el píxel es 50% gris y la ganancia es 20%, bajar el píxel a 40% gris.

#### **Paso 1.3: Base Blanca Inteligente (Breathable Underbase) (MEJORADO)**

* **Problema:** Evitar el efecto "parche de plástico" (Bulletproof).  
* **Lógica:**  
  1. Invertir luminancia.  
  2. **Threshold de Respirabilidad:** Si el color superior (Top Color) tiene una luminosidad \< 30% (ej. Azul Marino, Negro, Marrón), sustraer información de la base blanca.  
  3. Aplicar cv2.erode (Choke) de 1-2px para evitar rebose.

#### **Paso 1.4: Vectorización Híbrida**

* Vectorizar canales de alto contraste (Negro / Texto) usando Potrace para bordes perfectos.

#### **Paso 1.5: Motor de Ripping (Halftoning) (NUEVO)**

* **Objetivo:** Generar archivos que NO necesitan software RIP externo.  
* **Acción:** Convertir los canales Grayscale a **Bitmaps de 1-bit** (Puntos puros blanco/negro).  
* **Configuración por defecto:**  
  * **Forma:** Elíptica (mejor para degradados).  
  * **Frecuencia (LPI):** 45 LPI (Estándar textil).  
  * **Ángulos:**  
    * Base Blanca: 22.5°  
    * Colores Top: 61° (o variable para evitar Moiré).  
    * Negro: 45°

### **FASE 2: Backend y Estandarización de Salida**

#### **Paso 2.1: Estructura de Directorios del Job**

El entregable final debe tener esta estructura profesional:

/temp\_jobs/{job\_id}/  
├── manifest.json  
├── preview.jpg  
├── /01\_RIP\_Ready\_Bitmaps/       \<-- ¡NUEVO\! Listos para imprimir (1-bit TIFF/PNG)  
│   ├── 01\_Underbase\_45lpi.png  
│   ├── 02\_Red\_45lpi.png  
│   └── ...  
├── /02\_Raw\_Grayscale/           \<-- Para usuarios con su propio RIP (PNG 8-bit)  
│   ├── 01\_Underbase\_Gray.png  
│   └── ...  
└── /03\_Vectors/                 \<-- Para corte o alta definición (SVG/PDF)  
    └── 05\_Black\_Outline.svg

#### **Paso 2.2: Contrato de Datos (manifest.json)**

{  
  "job\_id": "xyz",  
  "print\_order": \["Underbase", "Red", "Black"\],  
  "separations": \[  
    {  
      "name": "Underbase",  
      "type": "Underbase",  
      "files": {  
        "ripped": "/01\_RIP\_Ready\_Bitmaps/01\_Underbase\_45lpi.png",  
        "grayscale": "/02\_Raw\_Grayscale/01\_Underbase\_Gray.png",  
        "vector": "/03\_Vectors/01\_Underbase.svg"  
      },  
      "settings": { "lpi": 45, "angle": 22.5, "dot\_shape": "ellipse" }  
    }  
  \]  
}

### **FASE 3: Frontend y Visualización**

#### **Paso 3.1: Preview Realista**

* Usar los archivos grayscale para la previsualización en pantalla (el navegador renderiza mal los bitmaps de 1-bit al escalarlos).  
* Aplicar simulación de color con modo Multiply.

## **5\. Criterios de Aceptación (QA)**

1. **Prueba "Sin RIP":** Imprimir el archivo de la carpeta /01\_RIP\_Ready\_Bitmaps directamente desde el visor de imágenes de Windows/Mac. Debe salir con tramas de puntos visibles y limpios.  
2. **Prueba de Tacto (Virtual):** La base blanca generada no debe ser un bloque sólido rectangular; debe tener huecos donde hay sombras negras.  
3. **Prueba de Ganancia:** La imagen en pantalla (Preview) debe verse ligeramente más "pálida" que el original, anticipando que en la prensa la tinta se oscurecerá al expandirse.

## **6\. Despliegue**

\# Docker Compose debe incluir Ghostscript si se usa para el Ripping  
RUN apt-get update && apt-get install \-y ghostscript potrace  
