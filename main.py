print("Iniciando el generador de 'Agujero Negro de Tráfico'...")

import os
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import random

# Carga las variables de entorno (tu clave de API) desde el archivo .env
load_dotenv()

# Configura el cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configura el motor de plantillas Jinja2
env = Environment(loader=FileSystemLoader('templates'))

# --- CONFIGURACIÓN DE LA MÁQUINA DE CONTENIDO ---

# Lista de temas semilla para la generación masiva
temas_semilla = [
    "historia de la ópera", "mejores compositores de ópera", "terminología de ópera",
    "biografía de Maria Callas", "análisis de 'La Traviata'", "óperas famosas de Mozart",
    "el papel del director de orquesta", "tipos de voces en la ópera", "vestuario en la ópera",
    "escenografía de ópera moderna", "festivales de ópera en el mundo", "cómo apreciar la ópera",
    "la ópera en el cine", "instrumentos en una orquesta de ópera", "críticas de ópera famosas"
]

def limpiar_nombre_para_url(tema):
    """Convierte un tema en un nombre de archivo seguro para URL."""
    return tema.lower().replace(' ', '-').replace(':', '').replace('?', '').replace('¿', '').replace("'", "")

def generar_articulo_denso(tema, todos_los_temas):
    """Llama a la API de OpenAI para generar un artículo largo y con enlaces internos."""
    print(f"-> Solicitando artículo denso para: '{tema}'...")
    
    # Selecciona 10 temas aleatorios para enlazar, excluyendo el actual
    temas_para_enlazar = random.sample([t for t in todos_los_temas if t != tema], min(10, len(todos_los_temas) - 1))
    
    # Crea una lista de ejemplos de enlaces para guiar a la IA
    ejemplos_enlaces = ""
    for t in temas_para_enlazar:
        url_limpia = limpiar_nombre_para_url(t)
        ejemplos_enlaces += f"- <a href='/{url_limpia}.html'>{t}</a>\n"

    prompt_usuario = (
        f"Crea un artículo informativo y detallado de 1500 palabras sobre el tema: '{tema}'.\n"
        f"El artículo debe ser de alta calidad, bien estructurado con subtítulos (H2 y H3), y diseñado para mantener al lector en el sitio.\n"
        f"MUY IMPORTANTE: Dentro del cuerpo del texto, debes incluir de forma natural y contextual enlaces a OTROS artículos. Aquí tienes la lista de artículos a los que puedes enlazar:\n"
        f"{ejemplos_enlaces}\n"
        f"Asegúrate de que los enlaces estén integrados en el texto de manera fluida. Por ejemplo, si escribes sobre 'La Traviata', podrías mencionar a 'uno de los <a href='/mejores-compositores-de-opera.html'>mejores compositores de ópera</a>, Giuseppe Verdi'.\n"
        f"El objetivo es crear una red de contenido (un 'wiki') que invite a la exploración. No incluyas las etiquetas <html> o <body>, solo el contenido HTML interno del artículo."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Actúas como un experto en SEO y un redactor de contenido para un sitio de autoridad. Tu objetivo es crear artículos largos y densos que maximicen el tiempo de permanencia del usuario y las páginas vistas, enlazando internamente a otros artículos relevantes."},
                {"role": "user", "content": prompt_usuario}
            ]
        )
        print(f"-> Contenido recibido para: '{tema}'.")
        return response.choices[0].message.content
    except Exception as e:
        print(f"!!! ERROR al contactar OpenAI: {e}")
        return None

def construir_sitio_masivo():
    """Crea todos los artículos y la página principal."""
    print("\nIniciando construcción masiva del sitio...")
    template = env.get_template('money_page.html')
    nombres_de_paginas_generadas = []

    for tema in temas_semilla:
        contenido_html = generar_articulo_denso(tema, temas_semilla)
        
        if contenido_html:
            nombre_archivo_final = f"{limpiar_nombre_para_url(tema)}.html"
            nombres_de_paginas_generadas.append(nombre_archivo_final)
            
            output = template.render(title=tema.capitalize(), content=contenido_html)
            
            with open(nombre_archivo_final, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"==> PÁGINA CREADA: '{nombre_archivo_final}'\n")
    
    # Crear la página principal (index.html) con enlaces a todas las páginas generadas
    print("-> Creando página principal (index.html)...")
    html_de_enlaces = "<ul>"
    for pagina in sorted(nombres_de_paginas_generadas):
        titulo_bonito = pagina.replace('.html', '').replace('-', ' ').capitalize()
        html_de_enlaces += f"<li><a href='/{pagina}'>{titulo_bonito}</a></li>"
    html_de_enlaces += "</ul>"
    
    output_index = template.render(title="Bienvenido a OperaGuildNova - El Archivo Definitivo de la Ópera", content=html_de_enlaces)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(output_index)
    print("==> PÁGINA CREADA: 'index.html'")


# La "chispa" que inicia todo el proceso.
if __name__ == '__main__':
    construir_sitio_masivo()
    print("\nConstrucción del 'Agujero Negro de Tráfico' finalizada.")


