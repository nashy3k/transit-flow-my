# 🏛️ TransitFlow "Kinetic" – Phase 2 Release
**High-Resilience Multi-Agent Mobility Orchestrator for Malaysia**

> **Phase 2 Status**: [PRODUCTION HARDENED] 🦾  
> **Target**: Gen AI Academy Hackathon (APAC Cohort 1)

TransitFlow "Kinetic" is a production-grade evolution of the TransitFlow prototype. It is a state-aware mobility engine that bridges the gap between **Real-Time Geospatial Intelligence** and **National Economics (Budi95)**.

### 🚀 Phase 2 Kinetic Innovations:
- **🧠 Semantic Memory Bank**: Powered by **Cloud SQL + pgvector**, enabling the agent to remember and recall journey patterns across user sessions.
- **⚡ ADK Kinetic Engine**: A high-resilience **Supervisor-Tool orchestrator** built on the **Google Agentic Development Kit (ADK)** for sub-second multi-agent reasoning.
- **📡 MCP Registry Bridge**: Decoupled tool integration via **Model Context Protocol**, allowing live sensing of **DataGovMy** fuel and weather telemetry.
TransitFlow protects Malaysian commuters from global fuel volatility (RM 3.97) and unpredictable flash floods.

---

## 🚀 Phase 2 "Kinetic" Upgrades

*   **⚡ Gemini 3.1 Flash Lite**: Upgraded to the latest 3.1 series for lower latency and higher reasoning precision.
*   **🧠 Agentic Memory Bank (NEW)**: Long-term persistent memory powered by **CloudSQL + pgvector**. TransitFlow now remembers user journey patterns and preferences across sessions for hyper-personalized safety advice.
*   **💰 Live Economics Sensing**: Dynamically fetches current market fuel rates (RM 3.97) via the **DataGovMy MCP Bridge**.
*   **🗑️ Clear History (NEW)**: Secure, one-click reset for local browser state and the persistent **Memory Bank**, ensuring a fresh start for every journey.
*   **📍 Diverse Proximity (NEW)**: Intelligent station discovery that prioritizes modal variety (KTM, LRT, MRT).
*   **🔐 Production Security**: 100% integration with **Google Cloud Secret Manager**.

---

## 🚀 Key Features

-   **⛈️ Safety-First Routing**: Integrated with live **DataGovMy** meteorological telemetry for real-time flood and weather briefings.
-   **💰 BudiSavings Shield**: A dynamic economics simulator that calculates the savings between the **Market Fuel Rate** (RM 3.97) and the **Budi95 Subsidized Rate** (RM 2.05).
-   **🚆 Multi-Modal Optimization**: Direct comparison of Car, Motorbike, E-Hailing (Grab), and Public Transit (LRT/MRT/Bus).

---

## 🛠️ Technical Architecture & Stack

TransitFlow is powered by the **TransitFlow "Kinetic" Engine**, a high-resilience, multi-agent AI framework designed for national-scale production.

### 🔄 Process Flow
```mermaid
graph TD
    User([User Query]) --> Supervisor[ADK Supervisor]
    Supervisor --> Intent{Multi-Stage Intent Resolution}
    
    subgraph "Parallel Tool Execution (MCP Bridge)"
        Intent -- Safety --> Safety[DataGovMy Weather & Flood Tool]
        Intent -- Journey --> Geo[PostGIS Geospatial Tool]
        Intent -- Economy --> Eco[Live Fuel Parquet Sensing]
        Intent -- Recall --> Mem[pgvector Memory Bank Recall]
    end
    
    Safety -- Alerts --> Supervisor
    Geo -- Transit Node --> Supervisor
    Eco -- Market Rate: RM 3.97 --> Supervisor
    Mem -- Past Patterns --> Supervisor
    
    Supervisor -- Synthesize --> JSON[Visual Insight Assembly]
    JSON --> UI[Production Dashboard]
    UI -- Reset --> Clear[Clear History / Agent Reset]
```

### 🏛️ Production-Grade Hardening
*   **🔐 Secret Management**: 100% integration with **Google Cloud Secret Manager**.
*   **🏢 Database (Cloud SQL)**: Geospatial proximity logic powered by **PostgreSQL (PostGIS)** and semantic search via **pgvector**.
*   **🖥️ Windows First**: ASCII-hardened logging system ensuring stability across local Windows dev and Linux production.

---

## ⚖️ License

TransitFlow is licensed under the **Polyform Noncommercial License 1.0.0**. See the [LICENSE](LICENSE) file for details.

---

**Production URL**: [https://transitflow-kinetic-4dcycqsk3q-uc.a.run.app](https://transitflow-kinetic-4dcycqsk3q-uc.a.run.app)

*Built with ❤️ in Malaysia. Powered by **Google Gemini** and the **Google Cloud Stack**.* 🇲🇾🚆🎬📈
