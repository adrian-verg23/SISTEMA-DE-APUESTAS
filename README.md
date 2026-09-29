 Plataforma de Apuestas en Línea: Gestión de Datos y ETL para Power BI

**Programa:** Bootcamp de Análisis de Datos — "Quiero Ser Digital (QFSD)" Phase II

**Organización:** Corporación MAKAIA | **Proyecto:** Proyecto Integrador

---

📌 1. Descripción del Proyecto

Este proyecto consiste en el diseño, implementación, población y pipeline de extracción (ETL) de una base de datos relacional en **PostgreSQL** para una plataforma de apuestas deportivas en línea.

El sistema administra la operación completa de la plataforma, modelando desde la autenticación de usuarios y eventos deportivos hasta el registro de apuestas, variaciones de cuotas y transacciones financieras. Toda la información es extraída a formato **CSV** mediante un script automatizado en **Python** para su posterior modelado relacional y análisis analítico en **Power BI**.

---

🎯 2. Objetivos del Proyecto

* **Diseño del Modelo Relacional:** Construir un esquema de base de datos normalizado (13 tablas) con integridad referencial estricta y restricciones de negocio (`CHECK constraints`).
* **Implementación & Poblamiento:** Desplegar el DDL en PostgreSQL y poblar las tablas garantizando coherencia en dependencias jerárquicas.
* **Automatización ETL (Python):** Desarrollar un script en Python (`export_to_csv.py`) para extraer las 13 tablas relacionales a archivos CSV optimizados para herramientas BI.
* **Sincronización & Trabajo Colaborativo:** Gestionar el control de versiones mediante Git/GitHub y empaquetado seguro (`.zip`) para distribución del equipo.
* **Modelado en Power BI:** Establecer relaciones 1:N entre dimensiones y tablas transaccionales para análisis visual de KPIs.

---

🏗️ 3. Arquitectura y Modelo de Datos (13 Tablas)

El modelo de datos relacional se divide en 3 grandes bloques funcionales:

```
                      ┌──────────────────────┐
                      │        users         │
                      └──────────┬───────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
┌────────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  payment_methods   │ │    bet_tickets    │ │  financial_trans. │
└─────────┬──────────┘ └─────────┬─────────┘ └───────────────────┘
          │                      │
          └──────────────────────┴────────────────┐
                                                  ▼
                                      (Transacciones / Pagos)

```

### 📋 Detalle del Esquema Relacional:

1. **`users`**: Datos del usuario, saldo disponible, estado KYC y registro.
2. **`payment_methods`**: Métodos de pago habilitados (Tarjetas, Transferencias, Billeteras).
3. **`financial_transactions`**: Registro unificado de depósitos, retiros y pagos de premios (`Payout`). *(Aplica lógica de nulos condicionales según el tipo de movimiento)*.
4. **`sports`**: Catálogo general de disciplinas deportivas.
5. **`leagues`**: Ligas asociadas a cada deporte.
6. **`teams`**: Equipos participantes.
7. **`team_leagues`**: Tabla intermedia (N:M) entre equipos y ligas.
8. **`sports_events`**: Partidos o encuentros programados con resultados y estado.
9. **`market_types`**: Tipos de mercados de apuesta (Ganador, Goles, Puntos).
10. **`markets`**: Instancias de mercados creados para un evento deportivo específico.
11. **`market_selections`**: Opciones de selección dentro de cada mercado.
12. **`odds_history`**: Registro histórico y evolución de las cuotas.
13. **`bet_selections`**: Selecciones individuales dentro de cada boleto de apuesta.

---

📂 4. Estructura Real del Repositorio

```text
SISTEMA DE APUESTAS/
├── SQL/
│   ├── Diagrama de entedidad relacion (Modelo de Base de datos).jpg
│   └── 01_ddl_and_data_dump.sql
│
├── PYTHON/
│   ├── export_to_csv.py
│   └── venv/
│
├── CSV/
│   ├── users.csv
│   ├── bet_tickets.csv
│   ├── financial_transactions.csv
│   ├── payment_methods.csv
│   └── ... (las 13 tablas en .csv)
│
├── Tablas_Gestion_Apuestas_CSV.zip
├── .gitignore
└── README.md

```

---

## 🛠️ 5. Tecnologías Utilizadas

* **Base de Datos:** PostgreSQL (DDL, DML, FKs, CHECK Constraints).
* **Lenguajes & Librerías:** Python 3, `pandas` (Estructuración de DataFrames), `psycopg` (Conector PostgreSQL).
* **Visualización & BI:** Power BI Desktop / Power Query.
* **Control de Versiones & Entorno:** Git, GitHub, VS Code, PowerShell.

---

🔄 6. Flujo General del Proyecto (ETL & BI Pipeline)

```text
 ┌───────────────────────┐
 │   PostgreSQL Database │  --> (13 Tablas Normalizadas)
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │ PYTHON / psycopg      │  --> Script export_to_csv.py
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │ Carpeta CSV / ZIP     │  --> Exportación a CSV UTF-8 / Distribución
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │   Power Query / BI    │  --> Carga de Tablas y Modelo Relacional (1:N)
 └───────────────────────┘

```

---

👥 7. Integrantes del Equipo

**Jayzir Slaider Martínez Chamorro**
**Adrian Vergara** (`adrian-verg23`)
**Evelyn Alejadra Penagos Torres**
