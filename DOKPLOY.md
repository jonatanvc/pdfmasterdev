# Guía de Despliegue — Telegram PDF Bot

## Requisitos previos

- Servidor con Docker y Docker Compose instalados (o Dokploy)
- Un bot de Telegram creado vía [@BotFather](https://t.me/BotFather)
- Base de datos PostgreSQL (este proyecto usa **Neon** — neon.tech)

---

## 1. Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

| Variable | Obligatoria | Descripción |
|---|---|---|
| `TELEGRAM_TOKEN` | ✅ Sí | Token del bot obtenido de @BotFather |
| `DATABASE_URL` | ✅ Sí | URL de conexión PostgreSQL. Ejemplo Neon: `postgresql://user:pass@host/db?sslmode=require` |
| `ADMIN_TELEGRAM_ID` | ✅ Sí | Tu ID numérico de Telegram (puedes obtenerlo con @userinfobot) |
| `GOOGLE_FONTS_TOKEN` | ❌ No | API key de Google Fonts. Sin ella, `/text` usa fuente por defecto |
| `GA_API_SECRET` | ❌ No | Secret de Google Analytics 4. Sin ella, no se envían analytics |
| `GA_MEASUREMENT_ID` | ❌ No | ID de medición de GA4. Requiere `GA_API_SECRET` también |
| `SENTRY_DSN` | ❌ No | DSN de Sentry para monitoreo de errores |

### Ejemplo de `.env` mínimo:

```env
TELEGRAM_TOKEN=123456:ABCdefGhIjKlMnOpQrStUvWxYz
DATABASE_URL=postgresql://neondb_owner:tu_password@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require
ADMIN_TELEGRAM_ID=12345678
```

---

## 2. Base de datos — Neon PostgreSQL

Este bot usa **Neon** (neon.tech) como base de datos PostgreSQL serverless en la nube.

### Configuración:
1. Crea una cuenta en [neon.tech](https://neon.tech)
2. Crea un proyecto nuevo
3. Copia la **connection string** con el endpoint **pooler** (`-pooler` en el hostname)
4. Usa la URL **sin** el parámetro `channel_binding` (no compatible con psycopg2)
5. Pega la URL en `DATABASE_URL` de tu `.env`

> **Importante**: Usa siempre el endpoint **pooler** de Neon (hostname con `-pooler`).
> Esto gestiona las conexiones eficientemente y evita límites de conexión.

Las tablas se crean automáticamente al iniciar el bot por primera vez.

---

## 3. Despliegue

### Opción A — Docker Compose (servidor propio o VPS):

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/telegram-pdf-bot.git
cd telegram-pdf-bot

# Crear y editar el archivo de entorno
cp .env.example .env
nano .env  # configurar con tus valores reales

# Construir y levantar
docker compose up -d --build

# Ver logs en tiempo real
docker compose logs -f bot
```

### Opción B — Dokploy:

1. **Crear proyecto**: Dashboard de Dokploy → "New Project" → nombre: `telegram-pdf-bot`
2. **Añadir servicio**: Tipo "Docker Compose" → apuntar al repositorio Git
3. **Variables de entorno**: En la pestaña "Environment", añadir todas las variables de la tabla
4. **Deploy**: Dokploy detectará el `docker-compose.yml` y desplegará el bot

### Opción C — Solo Dockerfile (sin Docker Compose):

```bash
# Construir la imagen
docker build -t telegram-pdf-bot .

# Ejecutar con variables de entorno
docker run -d --name pdf-bot \
  --env-file .env \
  --restart unless-stopped \
  telegram-pdf-bot
```

---

## 4. Modo de operación

El bot opera en **modo polling**: consulta periódicamente los servidores de Telegram para recibir actualizaciones.

- No necesitas dominio ni certificado SSL
- No necesitas abrir puertos
- Funciona detrás de NAT/firewall sin configuración adicional
- Ideal tanto para desarrollo local como para producción en VPS

---

## 5. Funcionalidades del bot

| Función | Cómo usarla |
|---|---|
| **Convertir documentos a PDF** | Envía un archivo .doc, .docx, .ppt, .pptx o .odt |
| **Comprimir PDF** | Envía un PDF → botón "Compress" |
| **Fusionar PDFs** | Comando `/merge` → envía los archivos |
| **Dividir PDF** | Envía un PDF → botón "Split" |
| **Rotar PDF** | Envía un PDF → botón "Rotate" |
| **Recortar PDF** | Envía un PDF → botón "Crop" |
| **Encriptar/Desencriptar** | Envía un PDF → botón "Encrypt"/"Decrypt" |
| **Extraer texto/imágenes** | Envía un PDF → botón correspondiente |
| **Convertir imagen a PDF** | Envía una imagen al bot |
| **PDF desde texto** | Comando `/text` |
| **Marca de agua** | Comando `/watermark` |
| **Comparar PDFs** | Comando `/compare` |
| **PDF desde web** | Envía un enlace URL |
| **Cambiar idioma** | Comando `/help` → botón "Set Language 🌎" |

---

## 6. Arquitectura

```
┌─────────────────┐     ┌──────────────────────────────┐
│                 │     │  Telegram PDF Bot (Python)    │
│  Telegram API   │◄───►│  - python-telegram-bot 22.6   │
│                 │     │  - LibreOffice (doc→pdf)      │
└─────────────────┘     │  - Ghostscript, OCRmyPDF     │
                        │  - Modo: Polling              │
                        └───────────┬──────────────────┘
                                    │  SSL
                        ┌───────────▼──────────────────┐
                        │  Neon PostgreSQL (Serverless)  │
                        │  - Usuarios y preferencias    │
                        │  - Endpoint pooler            │
                        └──────────────────────────────┘
```

---

## 7. Mantenimiento

```bash
# Ver estado del contenedor
docker compose ps

# Reiniciar el bot
docker compose restart bot

# Actualizar a nueva versión
git pull
docker compose up -d --build

# Ver logs
docker compose logs -f bot --tail 100
```

### Backup de Neon:
Los backups se gestionan automáticamente desde el dashboard de Neon
(neon.tech → tu proyecto → Backups). Neon ofrece Point-in-Time Recovery.
