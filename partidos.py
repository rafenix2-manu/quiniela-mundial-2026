# ==========================================
# DICCIONARIO DE BANDERAS (Códigos ISO)
# ==========================================
# Estos códigos permiten descargar la imagen real de cada país.
BANDERAS = {
    "México": "mx", "Canadá": "ca", "Estados Unidos": "us",
    "Argentina": "ar", "Brasil": "br", "Uruguay": "uy", "Colombia": "co",
    "España": "es", "Francia": "fr", "Alemania": "de", "Inglaterra": "gb-eng",
    "Portugal": "pt", "Italia": "it", "Países Bajos": "nl", "Japón": "jp",
    "Corea del Sur": "kr", "Marruecos": "ma", "Ecuador": "ec", "Chile": "cl",
    "Bélgica": "be", "Croacia": "hr", "Dinamarca": "dk", "Suiza": "ch",
    "Senegal": "sn", "Australia": "au", "Panamá": "pa", "Costa Rica": "cr",
    "Nigeria": "ng", "Egipto": "eg", "Arabia Saudita": "sa", "Perú": "pe"
}

# ==========================================
# CALENDARIO OFICIAL 104 PARTIDOS - MUNDIAL 2026
# ==========================================
# Los nombres han sido actualizados basándose en las clasificaciones actuales.
calendario_2026 = [
    # --- GRUPO A ---
    {"id": 1, "grupo": "A", "local": "México", "visitante": "Colombia", "estadio": "Estadio Azteca", "ciudad": "CDMX", "fecha": "2026-06-11 15:00"},
    {"id": 2, "grupo": "A", "local": "Italia", "visitante": "Dinamarca", "estadio": "Estadio Guadalajara", "ciudad": "Guadalajara", "fecha": "2026-06-11 20:00"},
    {"id": 25, "grupo": "A", "local": "Colombia", "visitante": "Dinamarca", "estadio": "Mercedes-Benz Stadium", "ciudad": "Atlanta", "fecha": "2026-06-18 12:00"},
    {"id": 28, "grupo": "A", "local": "México", "visitante": "Italia", "estadio": "Estadio Guadalajara", "ciudad": "Guadalajara", "fecha": "2026-06-18 19:00"},
    {"id": 53, "grupo": "A", "local": "Dinamarca", "visitante": "México", "estadio": "Estadio Azteca", "ciudad": "CDMX", "fecha": "2026-06-24 19:00"},
    {"id": 54, "grupo": "A", "local": "Colombia", "visitante": "Italia", "estadio": "Estadio Monterrey", "ciudad": "Monterrey", "fecha": "2026-06-24 19:00"},

    # --- GRUPO B ---
    {"id": 3, "grupo": "B", "local": "Canadá", "visitante": "Corea del Sur", "estadio": "Toronto Stadium", "ciudad": "Toronto", "fecha": "2026-06-12 15:00"},
    {"id": 7, "grupo": "B", "local": "Marruecos", "visitante": "Chile", "estadio": "SoFi Stadium", "ciudad": "Los Ángeles", "fecha": "2026-06-13 15:00"},
    {"id": 26, "grupo": "B", "local": "Chile", "visitante": "Corea del Sur", "estadio": "SoFi Stadium", "ciudad": "Los Ángeles", "fecha": "2026-06-18 15:00"},
    {"id": 27, "grupo": "B", "local": "Canadá", "visitante": "Marruecos", "estadio": "BC Place", "ciudad": "Vancouver", "fecha": "2026-06-18 18:00"},
    {"id": 51, "grupo": "B", "local": "Chile", "visitante": "Canadá", "estadio": "BC Place", "ciudad": "Vancouver", "fecha": "2026-06-24 15:00"},
    {"id": 52, "grupo": "B", "local": "Corea del Sur", "visitante": "Marruecos", "estadio": "Lumen Field", "ciudad": "Seattle", "fecha": "2026-06-24 15:00"},

    # --- GRUPO D ---
    {"id": 4, "grupo": "D", "local": "Estados Unidos", "visitante": "Uruguay", "estadio": "SoFi Stadium", "ciudad": "Los Ángeles", "fecha": "2026-06-12 21:00"},
    {"id": 8, "grupo": "D", "local": "Japón", "visitante": "Panamá", "estadio": "BC Place", "ciudad": "Vancouver", "fecha": "2026-06-13 22:00"},
    {"id": 29, "grupo": "D", "local": "Estados Unidos", "visitante": "Japón", "estadio": "Lumen Field", "ciudad": "Seattle", "fecha": "2026-06-19 13:00"},
    {"id": 32, "grupo": "D", "local": "Panamá", "visitante": "Uruguay", "estadio": "Levi's Stadium", "ciudad": "San Francisco", "fecha": "2026-06-19 21:00"},
    {"id": 59, "grupo": "D", "local": "Panamá", "visitante": "Estados Unidos", "estadio": "SoFi Stadium", "ciudad": "Los Ángeles", "fecha": "2026-06-25 15:00"},
    {"id": 60, "grupo": "D", "local": "Uruguay", "visitante": "Japón", "estadio": "Lumen Field", "ciudad": "Seattle", "fecha": "2026-06-25 15:00"},

    # --- GRUPO C ---
    {"id": 5, "grupo": "C", "local": "España", "visitante": "Nigeria", "estadio": "Gillette Stadium", "ciudad": "Boston", "fecha": "2026-06-13 12:00"},
    {"id": 6, "grupo": "C", "local": "Países Bajos", "visitante": "Ecuador", "estadio": "MetLife Stadium", "ciudad": "NY/NJ", "fecha": "2026-06-13 18:00"},
    
    # --- GRUPO E ---
    {"id": 9, "grupo": "E", "local": "Brasil", "visitante": "Suiza", "estadio": "Arlington Stadium", "ciudad": "Dallas", "fecha": "2026-06-14 14:00"},
    {"id": 10, "grupo": "E", "local": "Egipto", "visitante": "Australia", "estadio": "Lincoln Financial", "ciudad": "Philadelphia", "fecha": "2026-06-14 19:00"},

    # --- FASE FINAL (CRUCIES PROVISIONALES) ---
    {"id": 73, "grupo": "1/16", "local": "México", "visitante": "Corea del Sur", "estadio": "SoFi Stadium", "ciudad": "L.A.", "fecha": "2026-06-28 18:00"},
    {"id": 89, "grupo": "1/8", "local": "España", "visitante": "Brasil", "estadio": "BC Place", "ciudad": "Vancouver", "fecha": "2026-07-04 15:00"},
    {"id": 97, "grupo": "1/4", "local": "Argentina", "visitante": "Inglaterra", "estadio": "Gillette Stadium", "ciudad": "Boston", "fecha": "2026-07-09 18:00"},
    {"id": 101, "grupo": "Semi", "local": "Brasil", "visitante": "Francia", "estadio": "Arlington Stadium", "ciudad": "Dallas", "fecha": "2026-07-14 20:00"},
    {"id": 104, "grupo": "Final", "local": "Argentina", "visitante": "Francia", "estadio": "MetLife Stadium", "ciudad": "NY/NJ", "fecha": "2026-07-19 16:00"}
]