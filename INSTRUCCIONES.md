# Elvi Memories - Página Web

## Estructura de Archivos

```
pagina-web-elvi/
├── index.html      # Página principal
├── styles.css      # Estilos (colores lila/blanco)
├── script.js       # Animaciones e interactividad
└── INSTRUCCIONES.md # Este archivo
```

## Cómo Ver la Página

1. Abre el archivo `index.html` en tu navegador
2. O usa un servidor local para mejor rendimiento:
   ```bash
   # Con Python instalado:
   cd pagina-web-elvi
   python -m http.server 8000
   # Luego abre: http://localhost:8000
   ```

## Secciones de la Página

| Sección | Descripción |
|---------|-------------|
| **Hero** | Imagen principal con llamado a la acción |
| **Sobre Mí** | Presentación personal con foto |
| **Portafolio** | Galería de trabajos (placeholder) |
| **Servicios** | Tarjetas de tipos de sesiones |
| **Testimonios** | Carrusel de reseñas de clientes |
| **Contacto** | Formulario + datos de contacto |

## Cómo Personalizar

### 1. Cambiar Fotos de Placeholder

En `index.html`, busca las URLs `https://via.placeholder.com/...` y reemplázalas con tus propias fotos:

```html
<!-- Cambiar en la sección de portafolio -->
<img src="ruta/a/tu/foto.jpg" alt="Sesión de Maternidad">

<!-- Cambiar foto de perfil en "Sobre Mí" -->
<img src="ruta/a/tu/foto-perfil.jpg" alt="Elvi Memories - Fotógrafa">
```

### 2. Agregar Fotos de Instagram

Para mostrar tus fotos de Instagram automáticamente, puedes:

**Opción A: Usar un widget de Instagram**
1. Ve a [embedInstagram.com](https://embedinstagram.com/) o [Lightwidget.com](https://lightwidget.com/)
2. Configura el widget con tu cuenta @elvimemories
3. Copia el código generado
4. Reemplaza la sección `instagram-placeholder` en `index.html`

**Opción B: Agregar fotos manualmente**
```html
<div class="portfolio-item">
    <img src="imagenes/tu-foto-1.jpg" alt="Descripción">
    <div class="portfolio-overlay">
        <span class="portfolio-category">Maternidad</span>
        <h3>Título de la foto</h3>
    </div>
</div>
```

### 3. Cambiar Información de Contacto

En `index.html`, busca y modifica:
- Teléfono: `+1 470 553 9163`
- Email: `elvimemories@gmail.com`
- Ubicación: `Lawrenceville, Georgia`
- Instagram: `@elvimemories`

### 4. Cambiar Colores

En `styles.css`, modifica las variables CSS al inicio:

```css
:root {
    --primary: #9B6B9E;        /* Lila principal */
    --primary-light: #C9A8C7;   /* Lila claro */
    --primary-dark: #7B4C7E;    /* Lila oscuro */
    --primary-lighter: #E8D5E5; /* Lila muy claro */
}
```

### 5. Cambiar Testimonios

Busca la sección de testimonios en `index.html` y edita el contenido:

```html
<div class="testimonial-card">
    <div class="testimonial-content">
        <div class="stars">...</div>
        <p>"Tu testimonio aquí..."</p>
    </div>
    <div class="testimonial-author">
        <img src="foto-cliente.jpg" alt="Cliente">
        <div class="author-info">
            <h4>Nombre del Cliente</h4>
            <span>Tipo de Sesión</span>
        </div>
    </div>
</div>
```

### 6. Agregar más Servicios

Copia y pega una tarjeta de servicio en `index.html`:

```html
<div class="service-card">
    <div class="service-icon">
        <img src="tu-icono.jpg" alt="Nuevo Servicio">
    </div>
    <h3>Nuevo Servicio</h3>
    <p>Descripción del servicio...</p>
    <a href="#contacto" class="service-link">
        Agendar <i class="fas fa-arrow-right"></i>
    </a>
</div>
```

## Colores Utilizados

| Color | Código | Uso |
|-------|--------|-----|
| Lila Principal | `#9B6B9E` | Botones, títulos destacados |
| Lila Claro | `#C9A8C7` | Fondos, bordes |
| Lila Oscuro | `#7B4C7E` | Hover, énfasis |
| Blanco | `#FFFFFF` | Fondos principales |
| Texto Oscuro | `#3D2E3D` | Texto principal |

## Funcionalidades

- **Responsive:** Se adapta a móviles y tablets
- **Animaciones:** Efectos suaves al hacer scroll
- **WhatsApp Flotante:** Botón para contactar directamente
- **Formulario:** Envía mensajes por WhatsApp
- **Carrusel:** Testimonios con auto-play

## Subir a Internet

### Opción 1: Netlify (Gratis)
1. Ve a [netlify.com](https://netlify.com)
2. Arrastra la carpeta `pagina-web-elvi`
3. ¡Listo! Tendrás una URL como `tu-sitio.netlify.app`

### Opción 2: GitHub Pages (Gratis)
1. Sube los archivos a un repositorio de GitHub
2. Ve a Settings > Pages
3. Selecciona la rama `main`
4. Tu sitio estará en `usuario.github.io/repositorio`

### Opción 3: Dominio Personalizado
1. Compra un dominio (ej: elvimemories.com)
2. Configura DNS en tu proveedor de hosting
3. Apunta al servidor donde alojaste la página

## Mantenimiento

### Actualizar Contenido
- Edita `index.html` para textos y estructura
- Edita `styles.css` para colores y estilos
- Edita `script.js` para comportamiento

### Agregar Nuevas Fotos
1. Crea una carpeta `imagenes/`
2. Sube tus fotos optimizadas (max 500KB)
3. Actualiza las rutas en `index.html`

## Soporte

Si necesitas ayuda para:
- Conectar con Instagram
- Agregar dominio personalizado
- Modificar diseños
- Agregar nuevas secciones

¡Contáctame y te ayudo!

---

**Creado para Elvi Memories**
*Fotografía Profesional en Lawrenceville, GA*