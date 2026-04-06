# TransitFlow 🇲🇾 (Malaysian Transit & Safety Assistant)

![TransitFlow Banner](https://img.shields.io/badge/Status-Live-success?style=for-the-badge&logo=google-cloud&logoColor=white)
![License](https://img.shields.io/badge/License-Polyform--Noncommercial-blue?style=for-the-badge)

TransitFlow (now **Public Safety Section 9**) is a next-generation, AI-driven transit and safety assistant designed specifically for the Malaysian landscape. It leverages the power of **Google ADK** (Agent Development Kit) and **Vertex AI** to provide real-time transit data, safety alerts from MetMalaysia, and carbon footprint analysis for sustainable travel.

---

## 🚀 Recent Updates (April 2026)

*   🛡️ **BudiProtocol Implementation**: New "Price Shielding" logic that compares the **RM 1.99 Budi95 Citizen Rate** against the market floating price to calculate actual trip savings.
*   🚦 **Virtual Route Intelligence**: Implemented a Geodesic-based routing fallback (1.3x Road Multiplier) to ensure accurate distance estimation regardless of official API availability.
*   💾 **Firestore Weekly Caching**: Integrated a 7-day persistent cache for the DataGovMy Fuel Registry to optimize backend performance and reduce external API dependency.
*   🛰️ **Reactive GPS Context**: Full support for real-time `navigator.geolocation.watchPosition`, allowing instant agent context updates when F12 DevTools sensors are overridden.
*   🗺️ **InfoBanjir Integration**: The "Live Warnings" widget is now linked directly to the official **MetMalaysia/Public InfoBanjir** maps portal.

---

## ✨ Core Features

*   🏙️ **Hyper-Local Context**: Detects current location (GPS) and provides human-readable name hints (e.g., "KLCC" or "KL Sentral").
*   ⚠️ **Localized Safety Filtering**: Transitioned from national noise to specific **State/City-level** alert filtering (e.g., Selangor, Kuala Lumpur) for better utility.
*   🚆 **Open Data Transit Search**: Deep integration with `Data.gov.my` for bus, rail, and traffic registry lookups.
*   🌱 **EcoNomics Impact Report**: Compares carbon footprint and fuel costs between Personal Cars (Market/Budi95), Grab (SKPS Commercial), and Public Transit.
*   🛡️ **Hardened Security**: Implements the "Anti-Leak Protocol" to secure Firebase and API credentials.

---

## 🏗️ Architecture (ADK Supervisor Agent)

The system is powered by the `TransitFlowSupervisor` agent in `agents/supervisor.py`, which coordinates three specialized tools:
1.  **Safety Analyst**: Monitors live Malaysian meteorological events with localized filtering.
2.  **Transit Intelligence**: Queries government registries for local transit availability.
3.  **Eco-Calculator**: Computes environmental and economic impacts using the **BudiProtocol**.
4.  **Distance Estimator**: Native tool for geodesic distance calculation.

---

## 🛠️ Technical Stack

*   **Core Logic**: [Google ADK](https://github.com/google/adk) for multi-agent orchestration.
*   **Intelligence**: [Vertex AI](https://cloud.google.com/vertex-ai) (Gemini 3 Flash/Pro) with Enterprise Routing.
*   **Database**: **Cloud Firestore** for weekly metadata caching and price persistence.
*   **Backend**: Python 3.12 (FastAPI), Uvicorn, Docker.
*   **Frontend**: Modern HTML5, Vanilla CSS3 (Glassmorphism), Firebase Web SDK.
*   **Infrastructure**: Google Cloud Run & Firebase Hosting.

---

## 📜 License

This project is licensed under the **Polyform Noncommercial License 1.0.0**. See the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ in Malaysia using Google Antigravity Agentic IDE.*
