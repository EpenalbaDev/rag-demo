"""Genera 3 PDFs ficticios para la demo RAG de Grupo Altamira S.A."""
from fpdf import FPDF
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def make_pdf(filename, title, sections):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Grupo Altamira S.A. - Documento Confidencial", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(w=pdf.epw, h=10, text=heading)
        pdf.set_font("Helvetica", "", 10)
        for line in body.strip().split("\n"):
            text = line.strip()
            if text:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=6, text=text)
            else:
                pdf.ln(3)
        pdf.ln(4)

    path = os.path.join(OUTPUT_DIR, filename)
    pdf.output(path)
    print(f"Generado: {path}")


# ── PDF 1: Reporte Anual 2023 ──────────────────────────────────
make_pdf("reporte_anual_2023.pdf", "Reporte Anual 2023", [
    ("Resumen Ejecutivo", """
Grupo Altamira S.A. cerro el ano fiscal 2023 con resultados historicos que consolidan su posicion
como lider en soluciones tecnologicas empresariales en la region centroamericana.

Los ingresos totales alcanzaron $4.2 millones de dolares, representando un crecimiento del 18%
respecto al ano 2022 ($3.56M). Este crecimiento fue impulsado principalmente por la fuerte
demanda de nuestro Software ERP Empresarial y los servicios de consultoria de implementacion.

El EBITDA alcanzo $890,000 dolares, con un margen EBITDA del 21.2%, mejorando respecto al
19.8% del ano anterior. La utilidad neta fue de $520,000 dolares, con un margen neto del 12.4%.
"""),
    ("Desempeno por Segmento", """
Segmento Retail: Contribuyo con el 60% de los ingresos totales ($2.52M). Este segmento mostro
un crecimiento del 22% impulsado por la adopcion de soluciones ERP por parte de PYMEs panamenas.
Los clientes clave incluyen Farmacia San Judas, Distribuidora El Volcan y Restaurantes La Plaza.

Segmento Corporativo: Represento el 40% de los ingresos ($1.68M). Aunque el crecimiento fue
mas moderado (12%), los margenes son significativamente mas altos. Clientes principales:
Banco Regional S.A., Seguros del Istmo, Grupo Torre Alta S.A. y Supermercados Riba Smith.

El ticket promedio del segmento corporativo es de $15,200, comparado con $4,800 en el segmento retail.
"""),
    ("Indicadores Financieros Clave", """
Ingresos Totales: $4,200,000 (+18% vs 2022)
Costo de Ventas: $2,310,000 (55% de ingresos)
Utilidad Bruta: $1,890,000 (margen bruto 45%)
Gastos Operativos: $1,000,000
EBITDA: $890,000 (margen 21.2%)
Depreciacion y Amortizacion: $120,000
Utilidad Operativa (EBIT): $770,000
Gastos Financieros: $85,000
Utilidad antes de Impuestos: $685,000
Impuestos: $165,000
Utilidad Neta: $520,000 (margen neto 12.4%)

Numero de clientes activos: 15
Tasa de retencion de clientes: 92%
Ingreso promedio por cliente: $280,000
"""),
    ("Expansion Regional", """
En el cuarto trimestre de 2023, Grupo Altamira S.A. inicio operaciones en Colombia a traves
de su primer cliente internacional, Importadora Los Andes, con sede en Bogota. Esta expansion
marca el inicio de la estrategia de internacionalizacion de la compania.

Adicionalmente, se cerro un acuerdo con Servicios Globales CR en Costa Rica, estableciendo
presencia en tres paises de la region. La meta para 2024 es alcanzar el 15% de ingresos
provenientes de operaciones internacionales.

Mercados objetivo para 2024-2025: Guatemala, El Salvador y Republica Dominicana.
"""),
    ("Perspectivas 2024", """
Para el ano fiscal 2024, la empresa proyecta:
- Ingresos de $5.0M a $5.3M (crecimiento del 19-26%)
- Margen EBITDA objetivo del 23-25%
- Lanzamiento del Modulo de Inteligencia Artificial para ERP
- Expansion del equipo de ventas en Colombia y Costa Rica
- Inversion de $400,000 en I+D para nuevos productos
- Meta de 22 clientes activos al cierre del ano

El principal riesgo identificado es la dependencia del mercado panameno (85% de ingresos)
y la competencia creciente de soluciones SaaS internacionales.
"""),
])


# ── PDF 2: Estados Financieros Q3 ──────────────────────────────
make_pdf("estados_financieros_Q3.pdf", "Estados Financieros Q3 2023", [
    ("Balance General al 30 de Septiembre de 2023", """
ACTIVOS
Activos Corrientes:
  Efectivo y equivalentes: $1,200,000
  Cuentas por cobrar: $980,000
  Inventarios: $340,000
  Gastos prepagados: $85,000
  Total Activos Corrientes: $2,605,000

Activos No Corrientes:
  Propiedad, planta y equipo (neto): $3,800,000
  Activos intangibles (software): $1,200,000
  Inversiones a largo plazo: $350,000
  Otros activos: $145,000
  Total Activos No Corrientes: $5,495,000

TOTAL ACTIVOS: $8,100,000

PASIVOS
Pasivos Corrientes:
  Cuentas por pagar: $620,000
  Deuda a corto plazo: $450,000
  Obligaciones laborales: $280,000
  Impuestos por pagar: $190,000
  Total Pasivos Corrientes: $1,540,000

Pasivos No Corrientes:
  Deuda a largo plazo: $1,200,000
  Provisiones: $310,000
  Otros pasivos: $150,000
  Total Pasivos No Corrientes: $1,660,000

TOTAL PASIVOS: $3,200,000

PATRIMONIO
  Capital social: $2,000,000
  Reservas: $800,000
  Utilidades retenidas: $1,580,000
  Utilidad del periodo: $520,000
  Total Patrimonio: $4,900,000

TOTAL PASIVOS + PATRIMONIO: $8,100,000
"""),
    ("Estado de Resultados Q3 2023 (Julio - Septiembre)", """
Ingresos por ventas: $1,100,000
Costo de ventas: ($650,000)
Utilidad Bruta: $450,000

Gastos de operacion:
  Gastos de administracion: ($120,000)
  Gastos de ventas: ($95,000)
  Depreciacion y amortizacion: ($30,000)
  Total gastos operativos: ($245,000)

Utilidad Operativa: $205,000

Otros ingresos (gastos):
  Ingresos financieros: $8,000
  Gastos financieros: ($22,000)
  Otros: ($11,000)

Utilidad antes de impuestos: $180,000
Impuesto sobre la renta: ($43,200)
Utilidad Neta Q3: $136,800

Utilidad Neta Acumulada (Ene-Sep): $420,000
"""),
    ("Ratios Financieros", """
Liquidez:
  Razon corriente: 1.69 (Activos corrientes / Pasivos corrientes)
  Prueba acida: 1.47

Endeudamiento:
  Ratio deuda/equity: 0.65 (Total Pasivos / Patrimonio)
  Ratio deuda/activos: 0.40
  Cobertura de intereses: 9.3x

Rentabilidad:
  Margen bruto: 40.9%
  Margen operativo: 18.6%
  Margen neto: 12.4%
  ROE (anualizado): 10.6%
  ROA (anualizado): 6.4%

Eficiencia:
  Rotacion de cuentas por cobrar: 45 dias
  Rotacion de inventarios: 28 dias
  Ciclo de conversion de efectivo: 52 dias
"""),
    ("Flujo de Caja Q3 2023", """
Flujo de Caja Operativo:
  Utilidad neta: $136,800
  Depreciacion y amortizacion: $30,000
  Cambios en capital de trabajo: ($45,000)
  Flujo neto operativo: $121,800

Flujo de Caja de Inversion:
  Compra de equipo: ($85,000)
  Desarrollo de software: ($60,000)
  Flujo neto de inversion: ($145,000)

Flujo de Caja de Financiamiento:
  Pago de deuda: ($50,000)
  Flujo neto de financiamiento: ($50,000)

Variacion neta de efectivo Q3: ($73,200)
Efectivo al inicio del Q3: $1,273,200
Efectivo al final del Q3: $1,200,000
"""),
    ("Notas a los Estados Financieros", """
Nota 1: Las cuentas por cobrar incluyen $285,000 en facturas vencidas de mas de 30 dias.
Los principales deudores son Clinica Santa Fe ($4,500 vencida 92 dias), Distribuidora
El Volcan ($4,500 vencida 62 dias) y Seguros del Istmo ($3,600 vencida 77 dias).

Nota 2: La deuda a largo plazo corresponde a un prestamo bancario con Banco Nacional de
Panama al 7.5% anual, con vencimiento en diciembre 2026. Se realizan pagos trimestrales
de $50,000 mas intereses.

Nota 3: Se registro una provision de $310,000 para contingencias legales relacionadas con
una disputa contractual con un ex-proveedor de servicios de mantenimiento.

Nota 4: Los activos intangibles incluyen $800,000 en desarrollo del Software ERP v3.0
y $400,000 en licencias adquiridas.
"""),
])


# ── PDF 3: Contratos Proveedores ────────────────────────────────
make_pdf("contratos_proveedores.pdf", "Contratos con Proveedores", [
    ("Resumen de Contratos Vigentes", """
Grupo Altamira S.A. mantiene contratos activos con tres proveedores principales que son
esenciales para la operacion del negocio. A continuacion se presenta el detalle de cada
contrato, incluyendo terminos, montos y condiciones especiales.

Monto total anual comprometido en contratos: $337,000
Vigencia promedio: 18 meses
Proximo vencimiento: LogiPanama S.A. (Junio 2024)
"""),
    ("Contrato 001 - TechSupply Corp", """
Proveedor: TechSupply Corp (Miami, Florida, USA)
Tipo de contrato: Suministro de hardware y licencias de software
Numero de contrato: GA-PROV-2023-001
Fecha de inicio: 1 de enero de 2023
Fecha de vencimiento: 31 de diciembre de 2024
Monto anual: $240,000 dolares

Alcance del contrato:
- Suministro de servidores Dell PowerEdge para clientes corporativos
- Licencias Microsoft 365 al por mayor (precio preferencial)
- Equipos de red Cisco para implementaciones
- Soporte tecnico de nivel 2 en hardware

Condiciones de pago: 50% al pedido, 50% contra entrega
Tiempo de entrega: 15 dias habiles desde la orden de compra
Garantia: 3 anos en servidores, 1 ano en equipos de red

Clausula de penalidad: En caso de incumplimiento en tiempos de entrega, se aplicara una
penalidad del 15% sobre el valor del pedido afectado. Si el retraso supera los 30 dias,
Grupo Altamira puede rescindir el contrato sin penalidad.

Clausula de exclusividad: TechSupply es el proveedor exclusivo de hardware Dell para
Grupo Altamira en Panama y Centroamerica.

Renovacion: Se renueva automaticamente por periodos de 12 meses a menos que alguna de
las partes notifique por escrito con 90 dias de anticipacion.
"""),
    ("Contrato 002 - LogiPanama S.A.", """
Proveedor: LogiPanama S.A. (Ciudad de Panama, Panama)
Tipo de contrato: Servicios de logistica y distribucion
Numero de contrato: GA-PROV-2023-002
Fecha de inicio: 1 de julio de 2023
Fecha de vencimiento: 30 de junio de 2024
Monto anual: $85,000 dolares

Alcance del contrato:
- Transporte y entrega de equipos a clientes en zona del Pacifico
- Almacenaje temporal en bodega de 200m2 en Albrook
- Manejo de inventario con sistema de tracking en tiempo real
- Servicio de entrega express (24 horas) dentro de Ciudad de Panama

Condiciones de pago: Mensual, a 30 dias factura
Cobertura geografica: Zona Pacifico de Panama (Ciudad de Panama, Panama Oeste, Cocle)

Clausula de exclusividad: LogiPanama es el proveedor exclusivo de servicios logisticos
para la zona del Pacifico. Grupo Altamira no puede contratar servicios de distribucion
con competidores en esta zona durante la vigencia del contrato.

SLA de entrega:
- Entregas en Ciudad de Panama: 24 horas habiles (99% cumplimiento requerido)
- Entregas en Panama Oeste: 48 horas habiles
- Entregas en Cocle: 72 horas habiles

Penalidad por incumplimiento de SLA: Descuento del 5% en la factura mensual por cada
punto porcentual por debajo del SLA acordado.

Seguro: LogiPanama cubre hasta $50,000 por evento en caso de dano o perdida de mercancia.
"""),
    ("Contrato 003 - OficinaMax", """
Proveedor: OficinaMax (Ciudad de Panama, Panama)
Tipo de contrato: Suministro de insumos de oficina y mobiliario
Numero de contrato: GA-PROV-2022-003
Fecha de inicio: 1 de marzo de 2022
Fecha de vencimiento: Renovacion automatica anual
Monto anual: $12,000 dolares

Alcance del contrato:
- Suministro mensual de papeleria y utiles de oficina
- Mobiliario de oficina bajo pedido
- Suministros de impresion (toner, papel, mantenimiento)
- Articulos de limpieza para oficinas

Condiciones de pago: Mensual, a 15 dias factura
Descuento por volumen: 10% en pedidos superiores a $2,000

Renovacion: Automatica cada 12 meses. Cualquier parte puede cancelar con 30 dias
de aviso previo.

Este es el contrato de menor cuantia pero de alta frecuencia de uso. El promedio
mensual de consumo es de $1,000 con picos en enero (inicio de ano) y julio.

No incluye clausulas de exclusividad ni penalidades especiales.
"""),
    ("Calendario de Vencimientos y Renovaciones", """
Febrero 2024: Revision anual de precios con TechSupply Corp
Marzo 2024: Renovacion automatica OficinaMax (Ano 3)
Junio 2024: Vencimiento contrato LogiPanama S.A. (decision de renovacion requerida)
Octubre 2024: Evaluacion de desempeno de proveedores (anual)
Diciembre 2024: Vencimiento contrato TechSupply Corp

Presupuesto total de contratos para 2024: $350,000 (aumento del 3.9% vs 2023)
Principales riesgos: fluctuacion del dolar, tiempos de entrega internacionales.
"""),
])

print("\n3 PDFs generados exitosamente en:", OUTPUT_DIR)
