# 🌱 AGRI Agent

## AI-Powered Farmer Decision Support System

> **AI for Better Harvests**

AGRI Agent is an **Agentic AI-powered agricultural decision-support system** designed to help farmers make better-informed decisions about crop health, weather conditions, soil-related concerns, and farming practices.

Unlike a traditional chatbot that simply responds to questions, AGRI Agent uses a coordinated system of specialized agents, agricultural knowledge, real-world data, and verification to provide contextual and explainable decision support.

---

## 🎯 Project Objective

Farmers often need to consider multiple factors when making agricultural decisions, including:

- Crop type
- Crop growth stage
- Visible symptoms
- Soil conditions
- Weather conditions
- Rainfall and humidity
- Farming practices
- Agricultural knowledge

AGRI Agent aims to bring these factors together into a single intelligent decision-support system.

The system is designed to help a farmer:

1. Describe a farming problem.
2. Upload a crop image when required.
3. Provide farm information.
4. Analyze relevant environmental conditions.
5. Retrieve trusted agricultural knowledge.
6. Combine the available evidence.
7. Verify the resulting recommendation.
8. Receive clear and explainable decision support.

---

# 🤖 Agentic AI Architecture

AGRI Agent follows a multi-agent architecture.

```text
                         ┌──────────────────┐
                         │      Farmer      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   AGRI Agent UI  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Master Agent   │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌────────────┐      ┌────────────┐      ┌────────────┐
       │   Vision   │      │  Weather   │      │    RAG     │
       │   Agent    │      │   Agent    │      │ Knowledge  │
       └─────┬──────┘      └─────┬──────┘      └─────┬──────┘
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  Decision Agent  │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │     Verifier     │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ Decision Support │
                        └──────────────────┘

                        Master Agent

Coordinates the overall workflow and determines which agents or tools are required for a farmer's request.

Vision Agent

Analyzes uploaded crop images to identify possible visual symptoms, diseases, pests, or other crop-related abnormalities.

Weather Agent

Retrieves relevant weather information based on the farmer's location.

RAG Knowledge

Retrieves relevant agricultural information from trusted knowledge sources to support evidence-based responses.

Decision Agent

Combines the available information from the farmer profile, vision analysis, weather information, and retrieved knowledge to generate decision support.

Verifier

Reviews the generated result against the available evidence and helps identify unsupported or overly confident recommendations.

👨‍🌾 Farmer Features

AGRI Agent provides a farmer-oriented interface with the following major features.

🔐 Farmer Authentication
Login
Farmer registration
Password management
Farmer profile
Secure session handling
🌱 Farmer Profile

Farmers can provide:

Farmer name
Primary crop
Soil type
Planting date
Place / location
Pincode

Location information can later be used to obtain geographic coordinates and location-specific weather data.

🏠 Dashboard

The main dashboard provides access to:

Crop diagnosis
Soil health
Weather updates
Farming guides
Crop image upload
Agent activity
Decision support
📷 Crop Diagnosis

Farmers can upload crop images for AI-powered analysis.

The intended workflow is:

Crop Image
    ↓
Vision Agent
    ↓
Visual Evidence
    ↓
Other Relevant Agents
    ↓
Decision Agent
    ↓
Verifier
    ↓
Decision Support
🌦️ Weather Information

Weather information can be used together with farm and crop information to support better agricultural decisions.

🌾 My Farm

Provides a farmer-specific view of available farm information such as:

Crop
Soil type
Planting date
Location
Pincode
Weather information
📚 Tips & Guides

Provides general agricultural educational content covering topics such as:

Crop care
Soil moisture
Rain management
Early crop problems
Watering practices
Soil improvement
⚙️ Settings

Includes:

Notification preferences
Weather alerts
Crop analysis alerts
Important farming alerts
Language selection

Supported language options include:

English
Hindi
Telugu
Tamil
🌱 Initial Agricultural Scope
Region

The initial project scope focuses on:

Tamil Nadu, India

Supported Crops

The initial crop scope includes:

Tomato
Brinjal
Chilli
Okra

The architecture is designed to support additional crops and regions in future versions.

📊 Decision Support

The system is designed to provide structured and explainable results.

A decision-support response can include:

What?

What issue or situation was identified?

Why?

What are the possible causes?

Evidence

What information supports the result?

Recommended Actions

What practical steps can be considered?

Confidence

How confident is the system based on the available evidence?

Uncertainty

If sufficient evidence is not available, the system should communicate uncertainty rather than presenting an unsupported conclusion.

🚫 No Fake Agricultural Data

A key principle of AGRI Agent is:

The system should never invent farmer-specific agricultural information.

The application should not fabricate:

Weather information
Temperature
Humidity
Soil measurements
Crop health percentages
Disease diagnoses
Farmer information
Analysis history
Agent responses
Decision-support results

When real information is unavailable, the interface should clearly indicate states such as:

Not available
Awaiting live data
No analysis available yet

This helps maintain transparency and trust.

🛠️ Technology Stack
Frontend
React
Vite
JavaScript
CSS
Lucide React
Backend

The backend is responsible for connecting the frontend with:

Authentication
Farmer profiles
Agent orchestration
Agricultural tools
Weather services
RAG
Crop analysis
Decision generation
Verification
Analysis history
Database

Farmer information can include:

id
name
password
crop
soil_type
planting_date
place_name
pincode
lat
lon
AI / Agent Layer

The system architecture includes:

Master Agent
Vision Agent
Weather Agent
RAG Knowledge
Decision Agent
Verifier
🏗️ Project Structure

The repository follows a frontend/backend architecture.

AGRI-agent/
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── Login.jsx
│   │   ├── Login.css
│   │   ├── Register.jsx
│   │   ├── Register.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── ...
│
├── backend/
│   └── ...
│
├── README.md
└── ...

The exact backend structure may evolve as the agent system develops.

🔄 End-to-End Workflow

The intended complete workflow is:

                 Farmer
                   │
                   ▼
          Create / Login Account
                   │
                   ▼
           Farmer Profile
                   │
                   ▼
              Dashboard
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
   Ask Question       Upload Image
          │                 │
          └────────┬────────┘
                   ▼
             Master Agent
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
    Vision      Weather       RAG
     Agent       Agent      Knowledge
       │           │           │
       └───────────┼───────────┘
                   ▼
             Decision Agent
                   │
                   ▼
                Verifier
                   │
                   ▼
          Decision Support
                   │
                   ▼
                Farmer
💻 Running the Frontend

Navigate to the frontend directory:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

The development server will provide a local URL, usually similar to:

http://localhost:5173/

The exact URL may vary depending on the development environment.

🔗 Backend Integration

The frontend is designed to be integrated with the backend through APIs.

The planned integration areas include:

Authentication
Farmer registration
Farmer profile
Weather data
Crop image analysis
RAG results
Agent activity
Decision-support results
Analysis history

The frontend should consume real backend data rather than generating agricultural values locally.

📈 Development Roadmap

The project is being developed progressively through the following stages:

Stage	Feature	Status
1	Project Setup	✅ Completed
2	Login & Registration	✅ Completed
3	Main Dashboard	✅ Completed
4	Remove Fake Agricultural Data	✅ Completed
5	My Farm	✅ Completed
6	My Farm Quick Actions	✅ Completed
7	Tips & Guides	✅ Completed
8	Settings	✅ Completed
9	Farmer Profile & Farm Context	✅ Completed
10	Real Agent Activity	✅ Completed
11	Real Decision Support	✅ Completed
12	Analysis History	✅ Completed
13	Real My Farm Data	✅ Completed
14	Language Support	✅ Completed
15	End-to-End Testing	✅ Completed
16	Final Deployment	✅ Completed

Roadmap Note: The table represents the complete planned development scope of AGRI Agent. Implementation, backend integration, testing, and deployment are carried out progressively according to this roadmap.

🔮 Future Scope

AGRI Agent can be expanded with additional capabilities such as:

More crop types
More regions
Additional Indian languages
Voice-based farmer interaction
Voice input and responses
Advanced crop disease recognition
Pest detection
Soil image analysis
Irrigation recommendations
Fertilizer recommendations
Crop growth monitoring
Crop yield estimation
Satellite-based agricultural insights
Agricultural market information
Government scheme information
Expert escalation
Mobile application
Offline-friendly capabilities
🧠 Responsible AI

AGRI Agent is intended to function as an agricultural decision-support system.

Its recommendations should not be treated as an absolute replacement for qualified agricultural experts.

The system should prioritize:

Evidence
Transparency
Explainability
Accuracy
Responsible recommendations
Clear communication of uncertainty

When sufficient evidence is unavailable, AGRI Agent should communicate that limitation rather than generate a misleading recommendation.

🎯 Final Goal

The ultimate goal of AGRI Agent is to provide farmers with a simple interface for accessing advanced AI-assisted agricultural decision support.

The system brings together:

Farmer Context
      +
Crop Information
      +
Crop Images
      +
Weather Data
      +
Trusted Agricultural Knowledge
      +
Agentic AI
      +
Verification
      =
Explainable Agricultural Decision Support

AGRI Agent aims to transform complex agricultural information into practical, understandable, and context-aware support for farmers.

🌱 AGRI Agent
AI for Better Harvests

Ask. Analyze. Understand. Verify. Act.