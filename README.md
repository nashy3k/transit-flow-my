# 🏙️ TransitFlow 🇲🇾

**The Intelligent Subsidy & Mobility Advisor for a Resilient Malaysia.**

TransitFlow is a multi-agent AI system designed to navigate the economic and environmental complexities of modern Malaysian urban life. It integrates state-of-the-art **Geospatial Reasoning**, **Real-time National Safety Data**, and the **BudiProtocol Economics Engine.**

---

## 🚀 Key Features

-   **⛈️ Safety-First Routing**: Integrated with live **DataGovMy** meteorological telemetry to provide real-time flood and weather briefings on every journey query.
-   **💰 BudiProtocol Engine**: A dynamic economics simulator that calculates the savings between the **Market Fuel Rate** (RM 3.87) and the **Budi95 Subsidized Rate** (RM 2.05).
-   **🚆 Multi-Modal Optimization**: Direct comparison of Car, Motorbike, E-Hailing (Grab), and Public Transit (LRT/MRT/Bus) in a clean executive briefing.
-   **🧩 Scenario Navigator**: High-resilience frontend that flips between primary routes and nearest "Transit Hub" alternates to find the most economical journey.

---

## 🛠️ Technical Architecture & Stack

TransitFlow is powered by a high-resilience, multi-agent AI framework designed for national-scale production.

### 🔄 Process Flow
```mermaid
graph TD
    User([User Query]) --> Supervisor[Supervisor Agent]
    Supervisor --> Intent{Intent Resolution}
    Intent -- Journey --> Geo[Geospatial Skill / Tool]
    Intent -- Info --> Safety[Safety Skill / Tool]
    Geo --> Eco[EcoNomics Engine]
    Safety -- Request --> DGM[DataGovMy MCP Registry]
    Eco -- Request --> DGM
    DGM -- Response --> Visual[Visual JSON Assembly]
    Visual --> Frontend[Frontend Dashboard]
    Frontend --> Render([Scenario History & Cards])
```

> [!TIP]
> **Architectural Note**: To ensure sub-second response times for national safety alerts, TransitFlow utilizes **Atomic Tool-Calling** (Skill Injection) rather than nested LLM agents. This provides the intelligence of a multi-agent system with the performance of a production-grade application.

### 🏛️ System Design
```mermaid
graph LR
    subgraph "Client Layer"
        Web[Firebase Hosting / Static App]
    end
    subgraph "Application Layer (Cloud Run)"
        API[FastAPI / FastMCP Bridge]
        ADK[Agentic Development Kit]
    end
    subgraph "AI Core (Vertex AI)"
        Gemini[Gemini 2.5 Flash Lite]
    end
    subgraph "Data & Registry"
        DGM[DataGovMy MCP Skill]
        FS[Firestore Cache]
        Eco[Budi95 Engine]
    end
    
    Web <--> API
    API <--> ADK
    ADK <--> Gemini
    ADK --- DGM
    ADK --- FS
    ADK --- Eco
```

-   **AI Core**: **Vertex AI (Gemini 2.5 Flash Lite)** orchestrated via the **Google Agentic Development Kit (ADK)** using the **Supervisor-Tool Runner** pattern for autonomous reasoning.
-   **Communication Protocol**: **Model Context Protocol (MCP)** via **FastMCP** for decoupled, resilient tool-calling.
-   **Backend Engine**: **Python 3.12 (FastAPI)** deployed on **Google Cloud Run** for serverless auto-scaling.
-   **Frontend**: Professional Vanilla JS/HTML5/CSS3 dashboard hosted on **Firebase**.
-   **Registry Layer**: Real-time integration with the Malaysia Open Data registry (DataGovMy).

---

## 🏛️ ADK Orchestration Detail

TransitFlow utilizes the **ADK `Runner`** to maintain session persistence and tool-calling integrity. 
- **Supervisor Agent**: A single `TransitFlowSupervisor` acts as the primary reasoning node.
- **Skill Injection**: Instead of high-latency subagents, we utilize **Atomic Tool Injection** where specialized "Skills" (Geospatial, Economics, Meteorological) are injected directly into the Supervisor's toolbelt via the ADK.
- **Autonomous Reasoning**: The ADK handles the multi-step `thought -> action -> observation -> response` loop locally, ensuring the agent always cross-references weather safety before providing transit advice.

---

## 📈 Impact & Scalability

By choosing a **Serverless Multi-Agent Architecture** backed by **FastAPI** and **FastMCP**, TransitFlow ensures low-latency safety advice even during high-concurrency events (e.g., flash flood alerts). The **MCP-based design** allows for immediate expansion of data sources (e.g., adding TNB outages or SPAD arrivals) without refactoring the core reasoning logic.

---

*Built with ❤️ in Malaysia. Powered by **Google Gemini** and the **Google Cloud Stack**.* 🇲🇾🚆🎬📈
