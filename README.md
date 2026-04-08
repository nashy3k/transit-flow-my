# 🏙️ TransitFlow 🇲🇾

**The Intelligent Subsidy & Mobility Advisor for a Resilient Malaysia.**

TransitFlow is a multi-agent AI system designed to navigate the economic and environmental complexities of modern Malaysian urban life. It integrates state-of-the-art **Geospatial Reasoning**, **Real-time National Safety Data**, and the **BudiProtocol Economics Engine.**

---

## 🚀 Key Features

-   **⛈️ Safety-First Routing**: Integrated with live **DataGovMy** meteorological telemetry to provide real-time flood and weather briefings on every journey query.
-   **💰 BudiProtocol Engine**: A dynamic economics simulator that calculates the savings between the **Market Fuel Rate** (RM 3.87) and the **Budi95 Subsidized Rate** (RM 2.05).
-   **🚆 Multi-Modal Optimization**: Direct comparison of Car, Motorbike, E-Hailing (Grab), and Public Transit (LRT/MRT/Bus) in a single executive view.
-   **🧩 Scenario Navigator**: High-resilience frontend that flips between primary routes and nearest "Transit Hub" alternates to find the most economical journey.
-   **🏥 High Resilience Tech**: Coordinate-first virtual routing with 1.3x geodesic fallbacks ensures destination targeting even when external map APIs underperform.

---

## 🛠️ Technical Architecture

-   **Brain**: Vertex AI (Gemini 2.5 Flash / Pro) orchestrated via the Google Agentic Development Kit (ADK).
-   **Backend**: Python 3.12 (FastAPI) deployed on **Google Cloud Run** for high-concurrency serverless scalability.
-   **Frontend**: Professional Vanilla JS/HTML5/CSS3 dashboard with JSON-RPC visual rendering, hosted on **Firebase**.
-   **Storage**: Firebase Firestore for weekly fuel price indexing and metadata caching.
-   **Registry**: Live SSE connection to the Malaysia Open Data registry (DataGovMy).

---

## 📈 Impact

TransitFlow empowers citizens to visualize the environmental and financial impact of their commute, incentivizing a shift toward public transit while safeguarding household budgets against energy price volatility.

---

*Built with ❤️ in Malaysia. Powered by **Google Gemini** and the **Google Cloud AI Stack**.* 🇲🇾🚆🎬📈
