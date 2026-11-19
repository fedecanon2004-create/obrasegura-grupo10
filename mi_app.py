"""PASO 4 de la guía: completen los datos de su aplicación.
Cambien cada texto que dice COMPLETAR. check.py no da LISTO mientras quede alguno."""

# Nombre de su herramienta, como la verá el cliente
TITULO = "ObraSegura: tarifa según el riesgo de atraso"

# Cliente del caso (la empresa que usará la app)
CLIENTE = "Cimiento Seguros"

# Qué decide el cliente con esta app, en una frase
DESCRIPCION = "Decidir si la póliza de cumplimiento de un contrato público se expide con tarifa estándar, con recargo o pidiendo garantías adicionales"

# Qué evalúa la app, con artículo: por ejemplo "un importador", "una zona", "una reseña", "un contrato"
UNIDAD = "un contrato"

# Texto que la app muestra siempre al final: atribuciones de las fuentes y advertencias
# que exigen las condiciones de uso de los datos de su caso (están en el brief)
PIE = ("Datos: SECOP II (Colombia Compra Eficiente), contratos de obra, interventoría y consultoría firmados desde 2020. "
       "La probabilidad es una estimación de riesgo hecha con lo que se sabe el día de la firma; no prueba que la entidad "
       "o el contratista hayan hecho algo mal. No se muestran nombres ni NIT de contratistas (Ley 1581 de 2012). "
       "Modelo: random forest entrenado con los contratos terminados de 2020 a 2025; se debe reentrenar cada año. "
       "Proyecto académico del curso Minería de Datos, Universidad de los Andes, grupo 10.")

# Logo o imagen del encabezado (opcional): pongan el archivo en assets/ y escriban su ruta
LOGO = "assets/logo.png"

# Interfaz: "streamlit" (app.py) o "html" (web/index.html)
INTERFAZ = "streamlit"
