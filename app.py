"""ZONA LIBRE: la interfaz de la aplicación ObraSegura (grupo 10).
Lo único que debe quedar es el pie de página al final (config["pie"]).

Para verla en su computador:   streamlit run app.py"""
import re

import pandas as pd
import streamlit as st

from core import (cargar_config, cargar_metadata, cargar_modelo, cargar_resultados, etiqueta, evaluar,
                  hay_modelo, texto_razon, validar)

config = cargar_config()
st.set_page_config(page_title="ObraSegura · Cimiento Seguros", page_icon="🏗️", layout="wide")

# ---------------------------------------------------------------------------------------------
# Colores y estilo
# ---------------------------------------------------------------------------------------------
AZUL = "#16324F"
COLORES = {"Tarifa estándar": "#2E7D32", "Recargo": "#D98E04", "Garantías adicionales": "#C62828"}
FONDOS = {"Tarifa estándar": "#E8F5E9", "Recargo": "#FFF4DC", "Garantías adicionales": "#FDECEA"}
QUE_HACER = {
    "Tarifa estándar": "Se expide la póliza con la tarifa normal.",
    "Recargo": "Se expide la póliza cobrando un recargo sobre la tarifa.",
    "Garantías adicionales": "Antes de expedir, se piden garantías adicionales (contragarantía o codeudor).",
}

REBOTE = "cubic-bezier(.34, 1.56, .64, 1)"     # sale rápido, se pasa un poco y vuelve: el rebote
SUAVE = "cubic-bezier(.22, 1, .36, 1)"        # frena suave al final


def retraso(i, paso=0.09, base=0.05):
    """Estilo para que los elementos entren escalonados (uno detrás de otro)."""
    return f"animation-delay:{base + i * paso:.2f}s;"


st.markdown(f"""
<style>
  .block-container {{padding-top: 1.6rem; max-width: 1200px;}}

  /* ---------- Entradas con rebote ---------- */
  @keyframes entrar   {{ from {{opacity: 0; transform: translateY(26px) scale(.97);}} to {{opacity: 1; transform: none;}} }}
  @keyframes crecer   {{ from {{transform: scaleX(0);}} to {{transform: scaleX(1);}} }}
  @keyframes caer     {{ 0% {{opacity: 0; transform: translateY(-30px);}} 100% {{opacity: 1; transform: none;}} }}
  @keyframes contar   {{ from {{opacity: 0; transform: translateY(12px) scale(.8);}} to {{opacity: 1; transform: none;}} }}
  .anim {{opacity: 0; animation: entrar .75s {REBOTE} both;}}

  /* ---------- Movimiento constante en reposo ---------- */
  @keyframes flotar   {{ 0%,100% {{transform: translateY(0);}} 50% {{transform: translateY(-4px);}} }}
  @keyframes latir    {{ 0%,100% {{box-shadow: 0 0 0 0 rgba(22,50,79,.35);}} 50% {{box-shadow: 0 0 0 7px rgba(22,50,79,0);}} }}
  @keyframes brillo   {{ 0% {{background-position: -200% 0;}} 100% {{background-position: 200% 0;}} }}
  @keyframes nubes    {{ from {{transform: translateX(0);}} to {{transform: translateX(-50%);}} }}
  @keyframes pluma    {{ 0%,100% {{transform: rotate(-2.5deg);}} 50% {{transform: rotate(2.5deg);}} }}
  @keyframes gancho   {{ 0%,100% {{transform: rotate(5deg);}} 50% {{transform: rotate(-5deg);}} }}
  @keyframes luz      {{ 0%,100% {{opacity: 1;}} 50% {{opacity: .15;}} }}
  @keyframes respirar {{ 0%,100% {{transform: scale(1);}} 50% {{transform: scale(1.012);}} }}

  /* ---------- Encabezado en capas (fondo, medio, frente) ---------- */
  .hero {{position: relative; overflow: hidden; border-radius: 16px; height: 250px; margin-bottom: 20px;
          background: linear-gradient(180deg, #0F2742 0%, #1D4670 60%, #2C6191 100%);
          animation: entrar .9s {REBOTE} both;}}
  .capa {{position: absolute; inset: 0; pointer-events: none;}}
  .capa svg {{position: absolute; bottom: 0; left: 0; width: 100%; height: 100%;}}
  .nubes {{width: 200%; animation: nubes 60s linear infinite;}}
  .lejos {{animation: flotar 9s ease-in-out infinite;}}
  .grua-pluma {{transform-box: fill-box; transform-origin: 0% 50%; animation: pluma 7s ease-in-out infinite;}}
  .grua-gancho {{transform-box: fill-box; transform-origin: 50% 0%; animation: gancho 3.4s ease-in-out infinite;}}
  .grua-luz {{animation: luz 1.6s ease-in-out infinite;}}
  .frente {{padding: 30px 34px; display: flex; flex-direction: column; justify-content: center; height: 100%;
            pointer-events: auto;}}
  .frente > * {{opacity: 0; animation: entrar .8s {REBOTE} both;}}
  .hero h1 {{color: white; font-size: 2.1rem; margin: 0 0 8px 0; padding: 0; max-width: 62%;
             text-shadow: 0 2px 12px rgba(0,0,0,.25);}}
  .hero p {{color: #D6E2EE; margin: 0; font-size: 1.0rem; max-width: 58%;}}
  .hero .cliente {{align-self: flex-start; background: rgba(255,255,255,.14); color: white; border-radius: 20px;
                   padding: 3px 12px; font-size: .8rem; margin-bottom: 12px; letter-spacing: .3px;
                   backdrop-filter: blur(4px);}}

  /* Paralaje: al bajar en la página cada capa se mueve a una velocidad distinta
     (navegadores con animaciones ligadas al scroll: Chrome y Edge; en los demás queda quieta) */
  @supports (animation-timeline: scroll()) {{
    @keyframes p-fondo  {{ to {{transform: translateY(70px);}} }}
    @keyframes p-medio  {{ to {{transform: translateY(35px);}} }}
    @keyframes p-frente {{ to {{transform: translateY(-25px); opacity: .25;}} }}
    .par-fondo  {{animation: p-fondo  linear both; animation-timeline: scroll(nearest); animation-range: 0 320px;}}
    .par-medio  {{animation: p-medio  linear both; animation-timeline: scroll(nearest); animation-range: 0 320px;}}
    .par-frente {{animation: p-frente linear both; animation-timeline: scroll(nearest); animation-range: 0 320px;}}
  }}

  /* ---------- Tarjetas ---------- */
  .tarjeta {{background: white; border: 1px solid #E3E8EE; border-radius: 12px; padding: 18px 20px;
             box-shadow: 0 1px 3px rgba(16,40,70,.06); height: 100%;
             transition: transform .35s {REBOTE}, box-shadow .35s {SUAVE};}}
  .tarjeta:hover {{transform: translateY(-4px); box-shadow: 0 10px 24px rgba(16,40,70,.12);}}
  .tarjeta .rotulo {{color: #5B6B7C; font-size: .82rem; text-transform: uppercase; letter-spacing: .5px;}}
  .tarjeta .numero {{font-size: 2.1rem; font-weight: 700; color: {AZUL}; line-height: 1.2; display: inline-block;
                     animation: contar .9s {REBOTE} both; animation-delay: inherit;}}
  .tarjeta .nota {{color: #6B7A89; font-size: .85rem;}}
  .decision {{border-radius: 12px; padding: 18px 20px; height: 100%;
              transition: transform .35s {REBOTE};}}
  .decision:hover {{transform: translateY(-4px);}}
  .decision .rotulo {{font-size: .82rem; text-transform: uppercase; letter-spacing: .5px; opacity: .8;}}
  .decision .titulo {{font-size: 1.8rem; font-weight: 700; line-height: 1.2; margin: 2px 0 6px 0;}}
  .decision.viva {{animation: entrar .75s {REBOTE} both, respirar 4s ease-in-out 1.2s infinite;}}

  /* Escala de probabilidad: los tramos crecen, la marca cae con rebote y luego late */
  .escala {{position: relative; height: 14px; border-radius: 7px; overflow: hidden; display: flex; margin: 14px 0 4px 0;
            transform-origin: left; animation: crecer .9s {SUAVE} .25s both;}}
  .marca {{position: absolute; top: -6px; width: 4px; height: 26px; background: {AZUL}; border-radius: 2px;
           animation: caer .8s {REBOTE} .8s both, latir 2.2s ease-in-out 1.8s infinite;}}
  .escala-cont {{position: relative; padding-top: 6px;}}
  .leyenda {{display: flex; color: #6B7A89; font-size: .78rem;}}

  /* Razones: entran una por una y su barra se llena con rebote; la barra brilla suave en reposo */
  .razon {{display: flex; align-items: center; gap: 14px; padding: 10px 0; border-bottom: 1px solid #EEF1F4;}}
  .razon:last-child {{border-bottom: none;}}
  .razon .txt {{flex: 1; color: #22313F;}}
  .razon .txt b {{color: {AZUL};}}
  .razon .pts {{min-width: 120px; text-align: right; font-weight: 600;}}
  .barrita {{height: 8px; border-radius: 4px; margin-top: 4px; transform-origin: left;
             animation: crecer .9s {REBOTE} both; animation-delay: inherit;
             background-size: 200% 100% !important;}}
  .barrita.sube {{background-image: linear-gradient(90deg, #C6282855 0%, #C6282888 50%, #C6282855 100%);}}
  .barrita.baja {{background-image: linear-gradient(90deg, #2E7D3255 0%, #2E7D3288 50%, #2E7D3255 100%);}}
  .barrita.sube, .barrita.baja {{animation: crecer .9s {REBOTE} both, brillo 3.5s linear 1.5s infinite;
                                 animation-delay: inherit, 1.5s;}}

  .aviso {{background: #F4F7FA; border-left: 4px solid {AZUL}; border-radius: 6px; padding: 12px 16px;
           color: #34495E; font-size: .92rem;}}

  /* Pestañas y bloques de Streamlit también entran escalonados */
  div[data-testid="stTabs"] button p {{font-size: 1.0rem; font-weight: 600;}}
  div[data-testid="stTabs"] button {{opacity: 0; animation: caer .6s {REBOTE} both;}}
  div[data-testid="stTabs"] button:nth-child(1) {{animation-delay: .35s;}}
  div[data-testid="stTabs"] button:nth-child(2) {{animation-delay: .43s;}}
  div[data-testid="stTabs"] button:nth-child(3) {{animation-delay: .51s;}}
  div[data-testid="stTabs"] button:nth-child(4) {{animation-delay: .59s;}}
  div[data-testid="stDataFrame"], div[data-testid="stVegaLiteChart"], div[data-testid="stForm"] {{
      animation: entrar .8s {REBOTE} .3s both;}}
  button[kind="primaryFormSubmit"] {{transition: transform .3s {REBOTE};}}
  button[kind="primaryFormSubmit"]:hover {{transform: translateY(-2px) scale(1.01);}}

  /* Si la persona pidió menos movimiento en su sistema, se respeta */
  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{animation: none !important; transition: none !important; opacity: 1 !important;}}
  }}
</style>
""", unsafe_allow_html=True)

# Encabezado en tres capas. Fondo: nubes y ciudad lejana. Medio: edificio en obra y grúa. Frente: textos.
CIUDAD = "".join(f'<rect x="{x}" y="{250 - h}" width="{w}" height="{h}" rx="2"/>' for x, w, h in [
    (0, 60, 70), (55, 40, 110), (100, 70, 85), (175, 35, 130), (215, 80, 75), (300, 45, 120), (350, 60, 90),
    (415, 30, 145), (450, 75, 80), (530, 50, 115), (585, 65, 95), (655, 40, 135), (700, 85, 70), (790, 45, 125),
    (840, 60, 100), (905, 35, 150), (945, 70, 85), (1020, 50, 120), (1075, 65, 90), (1145, 55, 110)])
NUBE = '<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{q}" fill="white" opacity=".07"/>'
NUBES = "".join(NUBE.format(x=x, y=y, r=r, q=r * .35) for x, y, r in [
    (90, 50, 70), (330, 35, 55), (560, 60, 80), (820, 40, 60), (1050, 55, 75),
    (1290, 50, 70), (1530, 35, 55), (1760, 60, 80), (2020, 40, 60), (2250, 55, 75)])
PISOS = "".join(f'<rect x="842" y="{250 - 24 * (i + 1)}" width="150" height="20" fill="#3D6E9C" opacity=".55"/>'
                f'<rect x="842" y="{250 - 24 * (i + 1) + 20}" width="150" height="4" fill="#9BB9D6" opacity=".5"/>'
                for i in range(5))
VIGAS = "".join(f'<line x1="{x}" y1="130" x2="{x}" y2="250" stroke="#9BB9D6" stroke-width="3" opacity=".45"/>'
                for x in (842, 892, 942, 992))

st.markdown(f"""
<div class="hero">
  <div class="capa par-fondo">
    <svg viewBox="0 0 1200 250" preserveAspectRatio="xMidYMax slice">
      <g class="nubes">{NUBES}</g>
      <g class="lejos" fill="#2A5785" opacity=".55">{CIUDAD}</g>
    </svg>
  </div>
  <div class="capa par-medio">
    <svg viewBox="0 0 1200 250" preserveAspectRatio="xMidYMax slice">
      {PISOS}{VIGAS}
      <g stroke="#F2B233" stroke-width="4" fill="none">
        <line x1="1060" y1="250" x2="1060" y2="40"/>
        <line x1="1075" y1="250" x2="1075" y2="40"/>
        {"".join(f'<line x1="1060" y1="{y}" x2="1075" y2="{y - 18}"/>' for y in range(240, 50, -24))}
      </g>
      <g class="grua-pluma">
        <rect x="1067" y="34" width="10" height="8" fill="#F2B233"/>
        <line x1="1067" y1="40" x2="820" y2="40" stroke="#F2B233" stroke-width="5"/>
        <line x1="1067" y1="40" x2="1150" y2="40" stroke="#F2B233" stroke-width="5"/>
        <rect x="1130" y="40" width="22" height="16" fill="#C98A12"/>
        <line x1="1068" y1="14" x2="830" y2="40" stroke="#F2B233" stroke-width="1.5"/>
        <line x1="1068" y1="14" x2="1150" y2="40" stroke="#F2B233" stroke-width="1.5"/>
        <line x1="1068" y1="14" x2="1068" y2="40" stroke="#F2B233" stroke-width="3"/>
        <circle class="grua-luz" cx="1068" cy="12" r="3.5" fill="#FF5A4E"/>
        <g class="grua-gancho">
          <line x1="900" y1="40" x2="900" y2="118" stroke="#D6E2EE" stroke-width="1.5"/>
          <rect x="878" y="118" width="44" height="9" rx="2" fill="#F2B233"/>
        </g>
      </g>
    </svg>
  </div>
  <div class="capa frente par-frente">
    <span class="cliente" style="{retraso(1)}">{config['cliente']}</span>
    <h1 style="{retraso(2)}">{config['titulo']}</h1>
    <p style="{retraso(3)}">{config['descripcion']}.</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------------------------
# Mientras no exporten su modelo, la app muestra la guía en lugar de fallar
# ---------------------------------------------------------------------------------------------
if not hay_modelo():
    st.info("Todavía no hay modelo en la carpeta model/. Sigan la guía del README.")
    st.divider()
    st.caption(config["pie"])
    st.stop()


@st.cache_resource
def recursos():
    return cargar_metadata(), cargar_modelo(), cargar_resultados()


meta, modelo, resultados = recursos()
evento = meta["evento"]
umbrales = meta["umbrales"]
decisiones = meta["decisiones"]


# ---------------------------------------------------------------------------------------------
# Formato
# ---------------------------------------------------------------------------------------------
def miles(x):
    return f"{x:,.0f}".replace(",", ".")


def pct(x, dec=0):
    return f"{x * 100:.{dec}f} %".replace(".", ",")


def valor_bonito(nombre_etiqueta, valor):
    """Muestra tasas como porcentaje y conteos con punto de miles."""
    texto = str(valor).strip()
    try:
        if "," in texto or re.fullmatch(r"-?\d{1,3}(\.\d{3})+", texto):
            numero = float(texto.replace(".", "").replace(",", "."))
        else:
            numero = float(texto)
    except ValueError:
        return texto
    if "Atrasos previos" in nombre_etiqueta or "(%)" in nombre_etiqueta or "suele agregar" in nombre_etiqueta:
        return pct(numero)
    if nombre_etiqueta in ("Valor", "Valor por día"):
        return "$" + miles(numero)
    if numero.is_integer():
        return miles(numero)
    return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


PATRON = re.compile(r"^(.*) = (.*) (sube|baja)(?: la probabilidad de \S+)? ([\d.]+) (?:pts|puntos)$")


def leer_razon(r):
    """Convierte una razón (texto del radar o dict del formulario) en (variable, valor, sentido, puntos)."""
    if isinstance(r, dict):
        return r["etiqueta"], valor_bonito(r["etiqueta"], r["valor"]), r["sentido"], abs(r["efecto"]) * 100
    m = PATRON.match(str(r).strip())
    if not m:
        return None
    nombre, valor, sentido, puntos = m.groups()
    return nombre, valor_bonito(nombre, valor), sentido, float(puntos)


def escala_html(probabilidad=None):
    limites = [0.0] + umbrales + [1.0]
    anchos = [(limites[i + 1] - limites[i]) * 100 for i in range(len(decisiones))]
    tramos = "".join(f'<div style="width:{a}%; background:{COLORES.get(d, "#999")}; opacity:.85"></div>'
                     for a, d in zip(anchos, decisiones))
    leyenda = "".join(f'<span style="width:{a}%; text-align:center">{d}</span>' for a, d in zip(anchos, decisiones))
    marca = ("" if probabilidad is None else
             f'<div class="marca" style="left:calc({probabilidad * 100}% - 2px)"></div>')
    return (f'<div class="escala-cont"><div class="escala">{tramos}</div>{marca}</div>'
            f'<div class="leyenda">{leyenda}</div>')


def mostrar_resultado(probabilidad, decision, razones):
    color, fondo = COLORES.get(decision, AZUL), FONDOS.get(decision, "#F4F7FA")
    c1, c2 = st.columns([1, 1.3])
    with c1:
        st.markdown(f"""
        <div class="tarjeta anim" style="{retraso(0)}">
          <div class="rotulo">Probabilidad de {evento}</div>
          <div class="numero">{probabilidad * 100:.0f} %</div>
          <div class="nota">Más de 20 % de días adicionales sobre el plazo pactado</div>
          {escala_html(probabilidad)}
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="decision anim viva" style="background:{fondo}; border:1px solid {color}33; {retraso(1)}">
          <div class="rotulo" style="color:{color}">Recomendación</div>
          <div class="titulo" style="color:{color}">{decision}</div>
          <div style="color:#34495E">{QUE_HACER.get(decision, "")}</div>
        </div>""", unsafe_allow_html=True)

    leidas = [x for x in (leer_razon(r) for r in razones) if x]
    st.write("")
    st.markdown("#### Por qué")
    if not leidas:
        st.caption("Con estos datos ninguna variable mueve mucho la probabilidad frente a un contrato típico.")
        return
    tope = max(p for *_, p in leidas) or 1
    filas = ""
    for i, (nombre, valor, sentido, puntos) in enumerate(leidas):
        col = "#C62828" if sentido == "sube" else "#2E7D32"
        flecha = "▲" if sentido == "sube" else "▼"
        filas += f"""
        <div class="razon anim" style="{retraso(i, 0.12, 0.45)}">
          <div class="txt"><b>{nombre}:</b> {valor}
            <div class="barrita {sentido}" style="width:{puntos / tope * 100:.0f}%"></div></div>
          <div class="pts" style="color:{col}">{flecha} {sentido} {puntos:.1f} pts</div>
        </div>"""
    st.markdown(f'<div class="tarjeta anim" style="{retraso(2)}">{filas}</div>', unsafe_allow_html=True)
    st.caption("Puntos de probabilidad frente a un contrato típico. Muestran de qué depende la predicción, "
               "no qué pasaría si algo cambiara.")


# ---------------------------------------------------------------------------------------------
# Pestaña 1: evaluar un contrato
# ---------------------------------------------------------------------------------------------
GRUPOS = {
    "El contrato": ["tipo_de_contrato", "tipo_obra", "modalidad_de_contratacion", "valor_del_contrato",
                    "duracion_pactada_dias", "pct_anticipo", "dias_firma_inicio", "puede_prorrogarse",
                    "firma_diciembre", "departamento"],
    "La entidad": ["sector", "orden", "entidad_centralizada", "ent_n_firmados_prev", "ent_n_previos_obs",
                   "ent_tasa_atraso_prev", "ent_ratio_medio_prev"],
    "El contratista": ["es_consorcio_ut", "es_pyme", "en_rues", "edad_proveedor_anios", "ciiu_seccion",
                       "prov_n_firmados_prev", "prov_n_previos_obs", "prov_tasa_atraso_prev", "prov_ratio_medio_prev"],
}
SI_NO = {"puede_prorrogarse", "firma_diciembre", "es_consorcio_ut", "en_rues"}
CALCULADAS = {"valor_por_dia", "prov_sin_historia", "ent_sin_historia", "perfil_contratista"}


def campo(col, valores):
    nombre, texto = col["nombre"], etiqueta(meta, col["nombre"])
    if nombre in SI_NO:
        si = st.selectbox(texto, ["Sí", "No"], index=0 if float(col["referencia"]) >= .5 else 1, key=nombre)
        valores[nombre] = 1.0 if si == "Sí" else 0.0
    elif col["tipo"] == "numérica":
        ref = float(col["referencia"])
        if "tasa" in nombre:
            valores[nombre] = st.slider(texto + " (%)", 0, 100, int(round(ref * 100)), key=nombre) / 100
        elif "ratio" in nombre:
            valores[nombre] = st.slider(texto + " (% del plazo)", 0, 200, int(round(ref * 100)), key=nombre) / 100
        elif any(k in nombre for k in ("_n_", "dias", "duracion", "edad", "valor")):
            valores[nombre] = float(st.number_input(texto, value=int(round(ref)), step=1, key=nombre))
        else:
            valores[nombre] = st.number_input(texto, value=ref, key=nombre)
    else:
        opciones = col.get("categorias") or [""]
        valores[nombre] = st.selectbox(texto, opciones, key=nombre)


def formulario_nuevo():
    por_nombre = {c["nombre"]: c for c in meta["columnas"]}
    usados = set()
    valores = {}
    with st.form("nuevo"):
        for titulo, nombres in GRUPOS.items():
            st.markdown(f"**{titulo}**")
            cols = st.columns(3)
            presentes = [n for n in nombres if n in por_nombre]
            for i, n in enumerate(presentes):
                with cols[i % 3]:
                    campo(por_nombre[n], valores)
                usados.add(n)
        resto = [c for c in meta["columnas"] if c["nombre"] not in usados and c["nombre"] not in CALCULADAS]
        if resto:
            with st.expander("Otros datos (si no los conocen, dejen el valor típico)"):
                cols = st.columns(3)
                for i, c in enumerate(resto):
                    with cols[i % 3]:
                        campo(c, valores)
        enviado = st.form_submit_button("Evaluar contrato", type="primary", width="stretch")
    if not enviado:
        return

    # Variables que salen de otras: no se le piden al usuario
    plazo = max(valores.get("duracion_pactada_dias", 1) or 1, 1)
    if "valor_por_dia" in por_nombre:
        valores["valor_por_dia"] = valores.get("valor_del_contrato", 0) / plazo
    if "ent_sin_historia" in por_nombre:
        valores["ent_sin_historia"] = float(valores.get("ent_n_previos_obs", 1) == 0)
    if "prov_sin_historia" in por_nombre:
        valores["prov_sin_historia"] = float(valores.get("prov_n_previos_obs", 1) == 0)
    if "perfil_contratista" in por_nombre:
        if valores.get("prov_n_firmados_prev", 1) == 0:
            perfil = "Nuevo"
        elif valores.get("prov_n_previos_obs", 1) == 0:
            perfil = "Con experiencia, sin historia"
        elif valores.get("prov_tasa_atraso_prev", 1) == 0:
            perfil = "Con historia, sin atrasos"
        else:
            perfil = "Con historia y atrasos"
        valores["perfil_contratista"] = perfil
    for c in meta["columnas"]:
        valores.setdefault(c["nombre"], c.get("referencia"))

    datos, errores, avisos = validar(pd.DataFrame([valores]), meta)
    for e in errores:
        st.error(e)
    for a in avisos:
        st.warning(a)
    if not errores:
        r = evaluar(modelo, meta, datos)[0]
        mostrar_resultado(r["probabilidad"], r["decision"], r["razones"])


def buscar_en_lista():
    col_id = meta.get("columna_id")
    if resultados is None or not col_id or col_id not in resultados.columns:
        st.info("No hay tabla de resultados para buscar.")
        return
    c1, c2 = st.columns(2)
    escrito = c1.text_input("Número del contrato en SECOP II", placeholder="Ej. CO1.PCCNTR.8236925").strip()
    ordenados = resultados.sort_values("probabilidad", ascending=False)
    elegido = c2.selectbox("O escojan uno del radar (del más riesgoso al menos riesgoso)",
                           ordenados[col_id].astype(str), disabled=bool(escrito))
    if escrito:
        encontrados = resultados[resultados[col_id].astype(str).str.upper() == escrito.upper()]
        if encontrados.empty:
            st.warning("Ese contrato no está en el radar de contratos en ejecución. "
                       "Pueden evaluarlo con la opción «Escribir los datos de un contrato nuevo».")
            return
        fila = encontrados.iloc[0]
    else:
        fila = resultados[resultados[col_id].astype(str) == elegido].iloc[0]

    puesto = int((resultados["probabilidad"] > fila["probabilidad"]).sum()) + 1
    detalles = [f"<b>{etiqueta(meta, c)}:</b> {fila[c]}" for c in
                ["nombre_entidad", "departamento", "tipo_de_contrato", "modalidad_de_contratacion"]
                if c in resultados.columns]
    st.markdown(f'<div class="aviso">{" &nbsp;·&nbsp; ".join(detalles)} &nbsp;·&nbsp; '
                f'<b>Puesto en el radar:</b> {miles(puesto)} de {miles(len(resultados))}</div>',
                unsafe_allow_html=True)
    st.write("")
    razones = [r for r in str(fila.get("razones", "")).split(" · ") if r and r != "nan"]
    mostrar_resultado(float(fila["probabilidad"]), fila["decision"], razones)


# ---------------------------------------------------------------------------------------------
# Pestaña 2: radar
# ---------------------------------------------------------------------------------------------
def tarjeta(rotulo, numero, nota="", color=AZUL, orden=0):
    return (f'<div class="tarjeta anim" style="{retraso(orden)}"><div class="rotulo">{rotulo}</div>'
            f'<div class="numero" style="color:{color}">{numero}</div><div class="nota">{nota}</div></div>')


def vista_lista():
    if resultados is None:
        st.info("No hay tabla de resultados.")
        return
    radar = resultados.sort_values("probabilidad", ascending=False).reset_index(drop=True)
    radar.insert(0, "Puesto", range(1, len(radar) + 1))

    with st.container(border=True):
        st.markdown("**Filtros**")
        solo_mil = st.toggle("Ver solo los 1.000 que conviene revisar primero", value=True)
        if solo_mil:
            radar = radar.head(1000)
        c1, c2, c3 = st.columns(3)
        for columna, lugar in [("departamento", c1), ("tipo_de_contrato", c2), ("nombre_entidad", c3)]:
            if columna in radar.columns:
                opciones = sorted(radar[columna].dropna().astype(str).unique())
                elegidos = lugar.multiselect(etiqueta(meta, columna), opciones, placeholder="Todos")
                if elegidos:
                    radar = radar[radar[columna].astype(str).isin(elegidos)]
        elegidas = st.pills("Recomendación", decisiones, selection_mode="multi", default=decisiones)
        radar = radar[radar["decision"].isin(elegidas or [])]

    conteo = radar["decision"].value_counts()
    cols = st.columns(4)
    cols[0].markdown(tarjeta("Contratos", miles(len(radar)), f"probabilidad media {pct(radar['probabilidad'].mean()) if len(radar) else '-'}", orden=0),
                     unsafe_allow_html=True)
    for i, (lugar, d) in enumerate(zip(cols[1:], decisiones), start=1):
        n = int(conteo.get(d, 0))
        lugar.markdown(tarjeta(d, miles(n), f"{pct(n / len(radar)) if len(radar) else '-'} de la lista",
                               COLORES.get(d, AZUL), orden=i), unsafe_allow_html=True)
    st.write("")

    if len(radar) and "departamento" in radar.columns:
        with st.expander("¿Dónde se concentran? Departamentos con más contratos en la lista", expanded=False):
            top = (radar.groupby("departamento")["decision"].value_counts().unstack(fill_value=0)
                   .reindex(columns=decisiones, fill_value=0))
            top = top.loc[top.sum(axis=1).sort_values(ascending=False).index[:10]]
            st.bar_chart(top, horizontal=True, color=[COLORES[d] for d in decisiones], height=360)

    mostrar = radar.drop(columns=[c for c in ["razones"] if c in radar.columns])
    mostrar = mostrar.rename(columns={c: etiqueta(meta, c) for c in mostrar.columns})
    mostrar = mostrar.rename(columns={"probabilidad": f"Probabilidad de {evento}", "decision": "Recomendación"})
    st.dataframe(
        mostrar, width="stretch", hide_index=True, height=480,
        column_config={
            f"Probabilidad de {evento}": st.column_config.ProgressColumn(
                f"Probabilidad de {evento}", min_value=0.0, max_value=1.0, format="percent"),
            "Puesto": st.column_config.NumberColumn("Puesto", width="small"),
        })
    st.download_button("⬇️ Descargar esta lista (CSV)", radar.to_csv(index=False).encode("utf-8"),
                       file_name="radar_obrasegura.csv", mime="text/csv")


# ---------------------------------------------------------------------------------------------
# Pestaña 3: cuánto vale el modelo
# ---------------------------------------------------------------------------------------------
def vista_valor():
    m = meta["metricas"]
    ahorro = m["costo_regla"] - m["costo_modelo"]
    c1, c2, c3 = st.columns(3)
    c1.markdown(tarjeta("Costo con el modelo", miles(m["costo_modelo"]), "por cada 1.000 contratos"), unsafe_allow_html=True)
    c2.markdown(tarjeta("Costo con la regla simple", miles(m["costo_regla"]), "por cada 1.000 contratos", "#6B7A89", orden=1),
                unsafe_allow_html=True)
    c3.markdown(tarjeta("Ahorro frente a la regla", miles(ahorro),
                        f"{ahorro / m['costo_regla'] * 100:.0f} % menos costo".replace(".", ","), "#2E7D32", orden=2),
                unsafe_allow_html=True)
    st.caption(f"Costos {m['unidad_costo']}, medidos en los contratos de 2024 y 2025, que el modelo no vio al entrenar.")
    st.markdown(f'<div class="aviso"><b>Regla simple con la que se compara:</b> {m["regla_simple"]}.</div>',
                unsafe_allow_html=True)
    st.write("")

    clave_atrasos = next((k for k in m if k.startswith("Atrasos encontrados")), None)
    if clave_atrasos:
        numeros = [int(x) for x in re.findall(r"\d+", str(m[clave_atrasos]).replace(".", ""))[:3]]
        if len(numeros) == 3:
            st.markdown("#### Si la Directora de Indemnizaciones revisa 1.000 contratos, ¿cuántos atrasos encuentra?")
            import altair as alt
            graf = pd.DataFrame({"Forma de escoger": ["Con el modelo", "Con la regla", "Al azar"],
                                 "Atrasos encontrados": numeros, "color": [AZUL, "#8A9AAB", "#C9D3DD"]})
            base = alt.Chart(graf).encode(
                y=alt.Y("Forma de escoger:N", sort=None, title=None, axis=alt.Axis(labelFontSize=13)),
                x=alt.X("Atrasos encontrados:Q", title="Atrasos encontrados entre 1.000 contratos revisados"))
            barras = base.mark_bar(cornerRadiusEnd=6, height=34).encode(color=alt.Color("color:N", scale=None))
            textos = base.mark_text(align="left", dx=6, fontSize=14, fontWeight="bold").encode(text="Atrasos encontrados:Q")
            st.altair_chart((barras + textos).properties(height=180), width="stretch")
            st.caption(f"El modelo encuentra {numeros[0] - numeros[1]} atrasos más que la regla y "
                       f"{numeros[0] - numeros[2]} más que escoger al azar.")

    otras = {k: v for k, v in m.items() if k not in ("costo_modelo", "costo_regla", "regla_simple", "unidad_costo",
                                                    "intervalo_diferencia", clave_atrasos, "Cuándo no usarlo")}
    if otras:
        st.markdown("#### Datos clave")
        cols = st.columns(len(otras))
        for i, (lugar, (k, v)) in enumerate(zip(cols, otras.items())):
            lugar.markdown(f'<div class="tarjeta anim" style="{retraso(i, base=.5)}"><div class="rotulo">{k}</div>'
                           f'<div style="font-size:1.05rem; color:{AZUL}; margin-top:6px">{v}</div></div>',
                           unsafe_allow_html=True)
    if "Cuándo no usarlo" in m:
        st.write("")
        st.warning(f"**Cuándo no usarlo.** {m['Cuándo no usarlo']}.")


# ---------------------------------------------------------------------------------------------
# Pestaña 4: cómo decide
# ---------------------------------------------------------------------------------------------
def vista_regla():
    limites = [0.0] + umbrales + [1.0]
    cols = st.columns(len(decisiones))
    for i, (lugar, d) in enumerate(zip(cols, decisiones)):
        lugar.markdown(f"""
        <div class="decision anim" style="background:{FONDOS.get(d)}; border:1px solid {COLORES.get(d)}33; {retraso(i)}">
          <div class="rotulo" style="color:{COLORES.get(d)}">Probabilidad de {pct(limites[i])} a {pct(limites[i + 1])}</div>
          <div class="titulo" style="color:{COLORES.get(d)}; font-size:1.4rem">{d}</div>
          <div style="color:#34495E">{QUE_HACER.get(d, "")}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown(f'<div style="max-width:100%">{escala_html()}</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("#### Por qué esos cortes")
    st.markdown(
        "Dejar con tarifa estándar un contrato que después se atrasa le cuesta a Cimiento **5 veces más** que "
        "cobrarle recargo a uno que no se atrasa. Por eso conviene el recargo apenas la probabilidad pasa de "
        "**1 en 6** (más o menos 17 %): a partir de ahí, lo que se espera perder por no cobrar es mayor que lo que "
        "se arriesga cobrando de más. Las garantías adicionales se piden al grupo de mayor riesgo.")
    st.markdown("#### Qué usa el modelo")
    st.markdown(
        "Un random forest que mira lo que se sabe el día de la firma: el tipo y valor del contrato, su plazo frente "
        "a contratos parecidos, el historial de atrasos de la entidad y el perfil del contratista. "
        "No usa nombres ni NIT de contratistas.")
    st.caption(f"Modelo entrenado con {miles(meta['n_entrenamiento'])} contratos; exportado el "
               f"{meta['fecha_exportacion'][:10]}.")


# ---------------------------------------------------------------------------------------------
# Cuerpo de la app
# ---------------------------------------------------------------------------------------------
pestanas = st.tabs(["🔎 Evaluar un contrato", "📡 Radar de contratos en ejecución",
                    "💰 Cuánto vale el modelo", "⚖️ Cómo decide"])
with pestanas[0]:
    modo = st.segmented_control("¿Qué quieren hacer?", ["Buscar un contrato del radar",
                                                        "Escribir los datos de un contrato nuevo"],
                                default="Buscar un contrato del radar")
    if modo == "Escribir los datos de un contrato nuevo":
        formulario_nuevo()
    else:
        buscar_en_lista()
with pestanas[1]:
    vista_lista()
with pestanas[2]:
    vista_valor()
with pestanas[3]:
    vista_regla()


# Pie de página: debe quedar (atribuciones y advertencias del caso, en mi_app.py)
st.divider()
st.caption(config["pie"])
