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
    "Los 10 mejores binoculares para ver ópera: Guía de compra 2025",
    "¿Vale la pena pagar por los asientos más caros en la ópera? Análisis de costo-beneficio",
    "Guía definitiva de los mejores teatros de ópera del mundo para planificar un viaje cultural",
    "Las 5 grabaciones de 'El Anillo del Nibelungo' de Wagner que todo coleccionista debe tener",
    "Libros sobre ópera para principiantes: ¿cuáles son esenciales para empezar?",
    "¿Qué es exactamente un 'leitmotiv' y cómo cambió la música para siempre?",
    "La ciencia detrás de la voz de un cantante de ópera: ¿cómo producen ese volumen?",
    "¿Por qué se abuchea en la ópera? El código no escrito del público",
    "Análisis de las 'arias de locura': La psicología de los personajes femeninos en la ópera",
    "¿Los cantantes de ópera usan micrófonos? La verdad sobre la amplificación en el teatro",
    "Maria Callas vs. Renata Tebaldi: El análisis definitivo de la rivalidad más grande de la ópera",
    "Ópera vs. Musical: ¿Cuáles son las diferencias técnicas y artísticas clave?",
    "Tenor vs. Barítono: ¿Qué tipo de voz es más difícil de dominar y por qué?",
    "Verdi vs. Wagner: Dos estilos que definieron el futuro de la ópera",
    "Producciones modernas vs. tradicionales: ¿Innovación o sacrilegio en la ópera?",
    "Cómo leer el argumento de una ópera (sinopsis) sin arruinarte las sorpresas",
    "Glosario de términos de ópera: de 'Aria' a 'Zarzuela' explicado para todos",
    "Guía para la primera vez en la ópera: 10 cosas que debes saber antes de ir",
    "¿Cuánto dura una ópera promedio y cómo prepararse para una función larga?",
    "Protocolo de aplausos en la ópera: ¿Cuándo es correcto aplaudir?",
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


