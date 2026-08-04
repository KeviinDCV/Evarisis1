---
workflow: general-video
flow: companion
storyboard: yes
message: "El dato oncológico del HUV deja de estar encerrado en PDFs: se consulta, se analiza y se puede verificar contra el informe original"
destination: presentation
aspect: 1920x1080
language: es
audience: "profesionales sanitarios y de gestión del HUV"
length: 3m30s
angle: showcase
---

## Intent

Vídeo explicativo de ONCONOVA — Gestor Oncológico del Hospital Universitario del
Valle — para proyectar ante una sala de profesionales. Debe explicar qué hace la
aplicación, **cómo es su flujo de funcionamiento**, enseñar los datos y recorrer
la estructura del informe estadístico en PDF.

Tono profesional e institucional, no publicitario: la audiencia son clínicos y
gestores, no compradores. La credibilidad pesa más que el impacto — el vídeo
debe sonar a herramienta clínica seria, no a demo de producto.

Narración con voz natural, en español.

## Assets

- `~/Documents/ONCONOVA Cirugía Oncológica/Exportaciones Base de datos/Informes estadísticos/Informe_estadistico_ONCONOVA.pdf`
  — el informe estadístico real, 5 páginas. Es material AGREGADO y anónimo:
  se puede mostrar tal cual. Fuente de la escena 7.

## Customizations

- **Pantallas recreadas en HTML con identidades ficticias.** Decisión del
  usuario. La estructura, el número de columnas y la volumetría son las reales;
  los nombres y cédulas, inventados. Ninguna captura de la app real entra en el
  vídeo.
- Voz de narración por síntesis (TTS) en español — se ofrecerán 2–3 voces
  antes de generar el audio definitivo.

## Notes

- **Ley 1581 (Habeas Data).** Ningún dato identificable de paciente puede
  aparecer en pantalla. Las cifras agregadas (2.076 casos, 67,1 % malignos,
  22.547 estudios…) NO identifican a nadie y sí se muestran.
- Las cifras en pantalla son las verificadas en la auditoría de la V6.9.91:
  765 PDFs · 22.547 estudios · 2.076 IHQ · 18.271 pacientes · 67,1 % malignos ·
  2.034 de 2.076 diagnósticos comprobados literalmente contra su PDF.
- No es una grabación de pantalla: HyperFrames renderiza desde HTML. Las
  pantallas son reconstrucciones fieles, decisión asumida por el usuario.
- Paleta tomada del propio producto (navy `#2d3e5e`) para que el vídeo y la
  aplicación se reconozcan como lo mismo.
