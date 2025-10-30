# EasyTasker - Gestor de Tareas

## Descripción
EasyTasker es una aplicación de escritorio desarrollada con Python y CustomTkinter que permite gestionar tareas de manera sencilla e intuitiva. Cuenta con soporte para temas claros y oscuros, múltiples idiomas, notificaciones, filtros avanzados, exportación a CSV, y backup automático.

## Características principales
- Añadir, eliminar y marcar tareas como completadas.
- Filtros por búsqueda, prioridad, categoría y estado.
- Soporte multilenguaje (español e inglés).
- Tema claro/oscuridad automático y manual.
- Exportación de tareas a CSV y PDF (PDF por implementar).
- Notificaciones visuales y sonoras para tareas próximas.
- Backup automático y restauración.
- Barra de progreso de tareas completadas.

## Requisitos

- Python 3.7 o superior
- Paquetes Python:
  - customtkinter
  - plyer (opcional, para notificaciones)
  - winsound (Windows para sonidos, ya integrado)
- Para instalarlos:
pip install customtkinter plyer

text

## Uso

1. Ejecuta el archivo principal:
python easytasker.py

text
2. La ventana mostrará el título de la app, opciones para cambiar tema e idioma, buscador y lista de tareas.
3. Escribe un título para la tarea en el formulario bajo "Título", configura prioridad, categoría y fecha límite.
4. Presiona "Agregar" para añadir la tarea.
5. Puedes usar los botones para marcar como completadas, eliminar o exportar la lista.

## Estructura del proyecto
- `easytasker.py`: Código fuente principal.
- `tasks.json`: Archivo donde se guardan las tareas.
- `tasks_backup.json`: Backup automático de tareas.
- `README.md`: Este archivo de descripción.

## Cómo contribuir

Puedes clonar el repositorio, mejorar funcionalidades o agregar nuevas características. Usa `git` para el control de versiones y abre "issues" si encuentras bugs o quieres sugerir mejoras.

## Licencia

Este proyecto está bajo licencia MIT - puedes usarlo, modificarlo y distribuirlo libremente.