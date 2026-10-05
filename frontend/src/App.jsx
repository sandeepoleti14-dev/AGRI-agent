import { useState, useRef } from "react";
import Login from "./Login";
import Register from "./Register";

import {
  Home,
  Sprout,
  History,
  BookOpen,
  Settings,
  CloudSun,
  Bell,
  MessageCircle,
  Camera,
  Send,
  Image as ImageIcon,
  ChevronRight,
  Leaf,
  Wheat,
  Clock3,
  MapPin,
  Droplets,
  FlaskConical,
  Activity,
  RefreshCw,
  CalendarDays,
  UserRound,
  CheckCircle2,
  AlertCircle,
  CloudRain,
  Wind,
  Globe,
  LogOut,
  ArrowLeft,
  BrainCircuit,
  Eye,
  BookOpenText,
  Bot,
  ShieldCheck,
} from "lucide-react";

import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000";

function readStoredFarmer() {
  const storedProfile =
    sessionStorage.getItem("agri_farmer_profile") ||
    localStorage.getItem("agri_farmer_profile");

  if (!storedProfile) {
    return null;
  }

  try {
    const farmer = JSON.parse(storedProfile);
    return farmer && farmer.id != null && farmer.name
      ? farmer
      : null;
  } catch (error) {
    console.warn("Saved farmer profile is invalid:", error);
    localStorage.removeItem("agri_farmer_profile");
    sessionStorage.removeItem("agri_farmer_profile");
    return null;
  }
}

function App() {
  // ============================================================
  // LOGIN STATE
  // ============================================================

  const [registeredAccount, setRegisteredAccount] =
    useState(readStoredFarmer);

  const [showLogin, setShowLogin] = useState(
    () => !readStoredFarmer()
  );

  const [showRegister, setShowRegister] = useState(false);

  const [farmerId, setFarmerId] = useState(
    () => readStoredFarmer()?.id || ""
  );

  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const [currentPage, setCurrentPage] = useState("home");

  const [farmRefreshing, setFarmRefreshing] = useState(false);

  // ============================================================
  // SETTINGS STATE
  // ============================================================

  const [notificationsEnabled, setNotificationsEnabled] =
    useState(
      localStorage.getItem("agri_notifications") !== "false"
    );

  const [weatherAlertsEnabled, setWeatherAlertsEnabled] =
    useState(
      localStorage.getItem("agri_weather_alerts") !== "false"
    );

  const [cropAlertsEnabled, setCropAlertsEnabled] =
    useState(
      localStorage.getItem("agri_crop_alerts") !== "false"
    );

  const [importantAlertsEnabled, setImportantAlertsEnabled] =
    useState(
      localStorage.getItem("agri_important_alerts") !== "false"
    );

  const [language, setLanguage] = useState(
    localStorage.getItem("agri_language") || "English"
  );

  // ============================================================
  // HISTORY PAGE STATE
  // ============================================================

  const [selectedHistory, setSelectedHistory] = useState(null);

  const historyData = [];

  // ============================================================
  // TIPS & GUIDES STATE
  // ============================================================

  const [selectedGuide, setSelectedGuide] = useState(null);
  const [guideCategory, setGuideCategory] = useState("All");
  const [guideSearch, setGuideSearch] = useState("");

  // ============================================================
  // TIPS & GUIDES DATA
  // ============================================================

  const guidesData = [
    {
      id: 1,
      category: "Crop Care",
      title: "Tomato Crop Care Basics",
      description:
        "Learn the basic practices for maintaining healthy tomato plants throughout the growing season.",
      readTime: "5 min read",
      icon: "sprout",
      content: [
        "Monitor your tomato plants regularly for changes in leaf color, growth, and overall appearance.",
        "Maintain suitable soil moisture and avoid both excessive watering and prolonged dryness.",
        "Remove damaged or diseased plant material carefully and monitor nearby plants for similar symptoms.",
        "Support healthy growth by maintaining suitable sunlight, spacing, and general field hygiene.",
      ],
    },
    {
      id: 2,
      category: "Soil Health",
      title: "Understanding Soil Moisture",
      description:
        "Understand why soil moisture matters and how farmers can monitor watering conditions.",
      readTime: "4 min read",
      icon: "soil",
      content: [
        "Soil moisture affects root development, nutrient availability, and overall crop growth.",
        "Check the soil condition before adding water rather than following a fixed watering schedule.",
        "Heavy rainfall can temporarily increase soil moisture, so irrigation decisions should consider recent weather.",
        "Regular monitoring can help reduce unnecessary watering and protect the crop from moisture stress.",
      ],
    },
    {
      id: 3,
      category: "Weather",
      title: "Managing Crops During Rain",
      description:
        "Practical considerations for protecting crops before and after significant rainfall.",
      readTime: "4 min read",
      icon: "weather",
      content: [
        "Monitor local rainfall conditions and avoid unnecessary irrigation when significant rain is expected.",
        "After heavy rainfall, inspect the field for standing water, damaged plants, and changes in soil condition.",
        "Good drainage can help reduce prolonged waterlogging around crop roots.",
        "Continue monitoring the crop for disease symptoms after periods of high moisture.",
      ],
    },
    {
      id: 4,
      category: "Pest & Disease",
      title: "Early Signs of Crop Problems",
      description:
        "Learn what to observe when leaves, stems, or fruits begin showing unusual changes.",
      readTime: "6 min read",
      icon: "pest",
      content: [
        "Look for changes in leaf color, spots, curling, wilting, holes, or unusual growth.",
        "Check whether symptoms are appearing on older leaves, newer leaves, or across the entire plant.",
        "Inspect nearby plants to determine whether the issue appears isolated or widespread.",
        "When symptoms are unclear, capture a clear crop image and use the AI analysis workflow for additional decision support.",
      ],
    },
    {
      id: 5,
      category: "Crop Care",
      title: "Watering Tomato Plants",
      description:
        "General guidance for monitoring water needs and avoiding unnecessary irrigation.",
      readTime: "4 min read",
      icon: "water",
      content: [
        "Check soil moisture before watering and consider recent rainfall and weather conditions.",
        "Watering requirements can change as the crop grows and environmental conditions change.",
        "Avoid creating prolonged wet conditions around the root zone.",
        "Use the farm information and weather information available in AGRI Agent when making irrigation decisions.",
      ],
    },
    {
      id: 6,
      category: "Soil Health",
      title: "Improving Soil Condition",
      description:
        "General practices that can support healthier soil and better crop growing conditions.",
      readTime: "5 min read",
      icon: "soil",
      content: [
        "Observe soil structure, moisture, drainage, and visible changes in the growing area.",
        "Organic matter and suitable natural inputs can contribute to healthier soil conditions when used appropriately.",
        "Avoid unnecessary chemical application without understanding the crop and soil requirements.",
        "For specific nutrient deficiencies or soil problems, use verified agricultural information and appropriate soil testing where available.",
      ],
    },
  ];

  // ============================================================
  // IMAGE UPLOAD
  // ============================================================

  const fileInputRef = useRef(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploadError, setUploadError] = useState("");

  // ============================================================
  // AGENT WORKFLOW STATE
  // ============================================================

  const [activeAgent, setActiveAgent] = useState(-1);
  const [completedAgents, setCompletedAgents] = useState([]);
  const [workflowComplete, setWorkflowComplete] = useState(false);
  const [workflowError, setWorkflowError] = useState(false);

  const [decisionResult, setDecisionResult] = useState(null);

  const normalizeConfidence = (value, isFraction = false) => {
    if (value == null || value === "") {
      return null;
    }

    const numericValue = Number(value);

    if (!Number.isFinite(numericValue)) {
      return null;
    }

    const percent = isFraction
      ? numericValue * 100
      : numericValue;
    return Math.min(Math.max(percent, 0), 100);
  };

  const readImageAsDataUrl = (file) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = () => resolve(String(reader.result));
      reader.onerror = () => reject(new Error("Unable to read selected image."));
      reader.readAsDataURL(file);
    });

  const agentSteps = [
    {
      name: "Master Agent",
      description: "Understanding your request",
      icon: BrainCircuit,
    },
    {
      name: "Vision Agent",
      description: "Analyzing crop image",
      icon: Eye,
    },
    {
      name: "Weather Agent",
      description: "Checking weather conditions",
      icon: CloudSun,
    },
    {
      name: "RAG Knowledge",
      description: "Searching trusted sources",
      icon: BookOpenText,
    },
    {
      name: "Decision Agent",
      description: "Combining the evidence",
      icon: Bot,
    },
    {
      name: "Verifier",
      description: "Checking recommendation",
      icon: ShieldCheck,
    },
  ];

  // ============================================================
  // FARM DATA
  // ============================================================
  const farmData = {
    farmerName:
      registeredAccount?.name || farmerId || "Farmer",

    farmerId:
      farmerId || "Not available",

    region:
      registeredAccount?.place_name ||
      decisionResult?.region ||
      "Not available",

    crop:
      registeredAccount?.crop ||
      decisionResult?.crop ||
      "Not available",

    farmStatus:
      decisionResult
        ? "Analysis available"
        : "Awaiting analysis",

    season: "Not available",

    growthStage:
      registeredAccount?.growth_stage ||
      decisionResult?.growthStage ||
      "Not available",

    cropHealth:
      decisionResult?.what ||
      "Not available",

    soilCondition:
      registeredAccount?.soil_type ||
      decisionResult?.soilCondition ||
      "Not available",

    soilMoisture: "Not available",

    lastSoilCheck: "Not available",
    plantingDate:
      registeredAccount?.planting_date || "Not available",
    pincode:
      registeredAccount?.pincode || "Not available",

    temperature:
      decisionResult?.weather?.current?.temperature_c != null
        ? `${decisionResult.weather.current.temperature_c}°C`
        : "Not available",

    humidity:
      decisionResult?.weather?.current?.humidity_pct != null
        ? `${decisionResult.weather.current.humidity_pct}%`
        : "Not available",

    rainfall:
      decisionResult?.weather?.current?.precipitation_mm != null
        ? `${decisionResult.weather.current.precipitation_mm} mm`
        : "Not available",

    wind:
      decisionResult?.weather?.current?.wind_speed_10m != null
        ? `${decisionResult.weather.current.wind_speed_10m} km/h`
        : "Not available",

    weatherStatus:
      decisionResult?.weather?.status === "ok"
        ? "Current conditions"
        : "Not available",

    lastAnalysis: decisionResult
      ? "Latest analysis available"
      : "No analysis yet",

    recentDiagnosis:
      decisionResult?.what ||
      "No crop analysis available yet",
  };

  // ============================================================
  // LOGIN
  // ============================================================

  if (showLogin) {
    return (
      <Login
        onLogin={async (name, password, rememberMe) => {
          const response = await fetch(
            `${API_BASE_URL}/api/auth/login`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ name, password }),
            }
          );
          const data = await response.json();
          if (!response.ok || data.status !== "success") {
            throw new Error(data.error || "Unable to sign in.");
          }

          const farmer = data.farmer;
          const storage = rememberMe ? localStorage : sessionStorage;
          localStorage.removeItem("agri_farmer_profile");
          sessionStorage.removeItem("agri_farmer_profile");
          storage.setItem(
            "agri_farmer_profile",
            JSON.stringify(farmer)
          );
          localStorage.removeItem("agri_logged_in");
          localStorage.removeItem("agri_farmer_id");
          setRegisteredAccount(farmer);
          setFarmerId(farmer.id);
          setShowLogin(false);
          setShowRegister(false);
          setCurrentPage("home");
        }}
        onCreateAccount={() => {
          setShowLogin(false);
          setShowRegister(true);
        }}
      />
    );
  }

  // ============================================================
  // REGISTER
  // ============================================================

  if (showRegister) {
    return (
      <Register
        onBackToLogin={() => {
          setShowRegister(false);
          setShowLogin(true);
        }}
        onAccountCreated={async (account) => {
          const response = await fetch(
            `${API_BASE_URL}/api/auth/register`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(account),
            }
          );
          const data = await response.json();
          if (!response.ok || data.status !== "success") {
            throw new Error(
              data.error || "Unable to create the farmer account."
            );
          }

          const farmer = data.farmer;
          localStorage.setItem(
            "agri_farmer_profile",
            JSON.stringify(farmer)
          );
          sessionStorage.removeItem("agri_farmer_profile");
          setRegisteredAccount(farmer);
          setFarmerId(farmer.id);
          setShowRegister(false);
          setShowLogin(false);
          setCurrentPage("home");
        }}
      />
    );
  }

  // ============================================================
  // PAGE NAVIGATION
  // ============================================================

  const navigateTo = (page) => {
    setCurrentPage(page);

    if (page !== "history") {
      setSelectedHistory(null);
    }

    if (page !== "guides") {
      setSelectedGuide(null);
    }
  };

  // ============================================================
  // LOGOUT
  // ============================================================

  const handleLogout = () => {
    localStorage.removeItem("agri_logged_in");
    localStorage.removeItem("agri_farmer_id");
    localStorage.removeItem("agri_farmer_profile");
    sessionStorage.removeItem("agri_farmer_profile");

    setFarmerId("");
    setRegisteredAccount(null);
    setCurrentPage("home");
    setShowRegister(false);
    setShowLogin(true);
  };

  // ============================================================
  // SUBMIT ANALYSIS REQUEST
  // ============================================================

  const runAgentWorkflow = async (currentQuestion) => {
    setIsProcessing(true);
    setWorkflowComplete(false);
    setWorkflowError(false);
    setCompletedAgents([]);
    setActiveAgent(0);
    setDecisionResult(null);

    try {
      const questionText =
        currentQuestion ||
        question ||
        "Please analyze my crop.";

      let visionDetection = null;

      if (selectedImage?.file) {
        const imageDataUrl = await readImageAsDataUrl(
          selectedImage.file
        );

        visionDetection = {
          fileName: selectedImage.name,
          mimeType: selectedImage.file.type || "image/jpeg",
          dataUrl: imageDataUrl,
        };
      }

      const response = await fetch(
        `${API_BASE_URL}/api/analyze`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            farmerPrompt: questionText,
            farmerProfile: registeredAccount || null,

            visionDetection,
            weatherData: null,
            ragEvidence: [],
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || data.status !== "success") {
        throw new Error(
          data.error ||
            "AGRI Agent analysis failed."
        );
      }

      const result = data.result || {};
      if (result.farmerProfile) {
        setRegisteredAccount(result.farmerProfile);
        const storage = sessionStorage.getItem("agri_farmer_profile")
          ? sessionStorage
          : localStorage;
        storage.setItem(
          "agri_farmer_profile",
          JSON.stringify(result.farmerProfile)
        );
      }
      if (!result.decision || !result.verification) {
        throw new Error(
          "The agent workflow did not return a verified decision."
        );
      }
      if (Array.isArray(result.errors) && result.errors.length > 0) {
        throw new Error(result.errors.join(" "));
      }
      const decision = result.decision || {};
      const candidates =
        Array.isArray(decision.candidates)
          ? decision.candidates
          : [];
      const topCandidate = candidates[0] || {};
      const evidence =
        Array.isArray(decision.evidence)
          ? decision.evidence
          : [];
      const actions =
        Array.isArray(decision.actions)
          ? decision.actions
          : [];
      const visionResult = result.visionDetection || {};
      const verification = result.verification || {};
      const weatherValue = result.weatherData || null;
      const role2Confidence = normalizeConfidence(
        visionResult.confidence,
        true
      );
      const confidenceValue =
        role2Confidence == null
          ? null
          : normalizeConfidence(decision.confidence_score) ??
            role2Confidence;
      const getEvidenceText = (item) => {
        if (typeof item === "string") return item.trim();
        if (!item || typeof item !== "object") return "";
        return (
          [
            item.claim,
            item.content,
            item.text,
            item.title,
            item.source,
          ].find(
            (value) =>
              typeof value === "string" && value.trim()
          ) || ""
        );
      };
      const decisionEvidence = evidence
        .map(getEvidenceText)
        .filter(Boolean);
      const ragEvidence = Array.isArray(result.ragEvidence)
        ? result.ragEvidence.map(getEvidenceText).filter(Boolean)
        : [];
      const availableEvidence =
        decisionEvidence.length > 0
          ? decisionEvidence
          : ragEvidence;
      const evidenceSource =
        evidence.find(
          (item) =>
            item &&
            typeof item === "object" &&
            (item.source || item.title)
        )?.source ||
        evidence.find(
          (item) =>
            item &&
            typeof item === "object" &&
            item.title
        )?.title ||
        (Array.isArray(result.ragEvidence)
          ? result.ragEvidence.find(
              (item) =>
                item &&
                typeof item === "object" &&
                (item.source || item.title)
            )?.source ||
            result.ragEvidence.find(
              (item) =>
                item &&
                typeof item === "object" &&
                item.title
            )?.title
          : null);
      const selectedAgents = result.selectedAgents || [];
      const finishedAgents = [0];
      if (selectedAgents.includes("vision")) finishedAgents.push(1);
      if (result.weatherData) finishedAgents.push(2);
      if (
        selectedAgents.includes("rag") ||
        selectedAgents.includes("vision")
      ) {
        finishedAgents.push(3);
      }
      if (result.decision) finishedAgents.push(4);
      if (result.verification) finishedAgents.push(5);

      setCompletedAgents(finishedAgents);
      setActiveAgent(-1);

      setDecisionResult({
        confidence:
          confidenceValue == null
            ? "Not available"
            : `${confidenceValue}%`,
        crop:
          visionResult.crop ||
          result.farmerProfile?.crop ||
          registeredAccount?.crop ||
          "Not available",
        region:
          result.farmerProfile?.place_name ||
          registeredAccount?.place_name ||
          "Not available",
        weather: weatherValue,
        what:
          topCandidate.name ||
          visionResult.possible_disease ||
          "Uncertain",
        whatDescription:
          topCandidate.visual_evidence ||
          visionResult.observations?.join("; ") ||
          "More crop evidence is required.",
        candidates:
          candidates.length > 0
            ? candidates.map(
                (candidate) =>
                  `${candidate.name} (${
                    normalizeConfidence(candidate.confidence_pct) == null
                      ? "Not available"
                      : `${normalizeConfidence(candidate.confidence_pct)}%`
                  })`
              )
            : [],
        why:
          decision.caveats?.[0] ||
          verification.reason ||
          "The system needs additional evidence to confirm the issue.",
        evidence:
          availableEvidence.length > 0
            ? availableEvidence
            : ["Not available"],
        evidenceSummary:
          availableEvidence.length > 0
            ? "Evidence returned by the agent workflow."
            : "Evidence is not available from the current analysis.",
        source: evidenceSource || "Not available",
        actions:
          actions.length > 0
            ? actions.map(
                (item) =>
                  item.action ||
                  "Follow the recommended agricultural practice."
              )
            : ["No recommended actions are available."],
        verifierStatus:
          verification.status ||
          "unknown",
        escalation:
          decision.escalate === true ||
          result.needsEscalation === true,
        growthStage:
          result.farmerProfile?.growth_stage ||
          "Not available",
        soilCondition:
          result.farmerProfile?.soil_type ||
          "Not available",
      });

      setWorkflowComplete(true);
    } catch (error) {
      console.error(
        "AGRI Agent workflow error:",
        error
      );

      setDecisionResult({
        confidence: "Not available",
        what: "Analysis failed",
        whatDescription:
          error.message ||
          "Unable to connect to AGRI Agent.",
        candidates: [],
        why:
          "Please make sure the AGRI Agent API is running.",
        evidence: [
          "No evidence available from the current analysis.",
        ],
        evidenceSummary:
          "No result was received.",
        source: "AGRI Agent",
        actions: [
          "Check that the AGRI Agent API is running on port 5000.",
          "Try the analysis again.",
        ],
        verifierStatus: "error",
        escalation: true,
      });

      setWorkflowError(true);
    } finally {
      setIsProcessing(false);
      setActiveAgent(-1);
    }
  };

  // ============================================================
  // QUESTION SUBMIT
  // ============================================================

  const handleQuestionSubmit = (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion && !selectedImage) {
      return;
    }

    setSubmittedQuestion(
      trimmedQuestion || "Crop image submitted for analysis."
    );

    setCurrentPage("home");

   runAgentWorkflow(trimmedQuestion);
  };

  // ============================================================
  // IMAGE UPLOAD
  // ============================================================

  const handleImageUpload = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setUploadError("Choose a JPG, PNG, or WebP image.");
      event.target.value = "";
      return;
    }

    if (file.size > 8 * 1024 * 1024) {
      setUploadError("Images must be 8 MB or smaller.");
      event.target.value = "";
      return;
    }

    setUploadError("");
    if (selectedImage?.url) {
      URL.revokeObjectURL(selectedImage.url);
    }

    const imageUrl = URL.createObjectURL(file);

    setSelectedImage({
      file,
      url: imageUrl,
      name: file.name,
    });

  };

  // ============================================================
  // MY FARM REFRESH
  // ============================================================

  const refreshFarmData = () => {
    setFarmRefreshing(true);

    setTimeout(() => {
      setFarmRefreshing(false);
    }, 1200);
  };

  // ============================================================
  // SHARED SIDEBAR
  // ============================================================

  const renderSidebar = () => (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <Leaf size={25} strokeWidth={2.2} />
        </div>

        <div className="brand-text">
          <h1>
            AGRI <span>Agent</span>
          </h1>

          <p>AI for Better Harvests</p>
        </div>
      </div>

      <nav className="navigation">
        <button
          className={`nav-item ${
            currentPage === "home" ? "active" : ""
          }`}
          onClick={() => navigateTo("home")}
        >
          <Home size={18} />
          <span>Home</span>
        </button>

        <button
          className={`nav-item ${
            currentPage === "farm" ? "active" : ""
          }`}
          onClick={() => navigateTo("farm")}
        >
          <Sprout size={18} />
          <span>My Farm</span>
        </button>

        <button
          className={`nav-item ${
            currentPage === "history" ? "active" : ""
          }`}
          onClick={() => navigateTo("history")}
        >
          <Clock3 size={18} />
          <span>History</span>
        </button>

        <button
          className={`nav-item ${
            currentPage === "guides" ? "active" : ""
          }`}
          onClick={() => navigateTo("guides")}
        >
          <BookOpen size={18} />
          <span>Tips & Guides</span>
        </button>

        <button
          className={`nav-item ${
            currentPage === "settings" ? "active" : ""
          }`}
          onClick={() => navigateTo("settings")}
        >
          <Settings size={18} />
          <span>Settings</span>
        </button>
      </nav>

      <div className="farmer-card">
        <div className="farmer-avatar">
          <Leaf size={19} />
        </div>

        <div className="farmer-details">
          <strong>
            {registeredAccount?.name || farmerId || "Farmer"}
          </strong>
        </div>
      </div>
    </aside>
  );

  // ============================================================
  // SHARED TOP BAR
  // ============================================================

  const renderTopbar = () => (
    <header className="topbar">
      <div></div>

      <div className="top-actions">
        <div className="weather-mini">
          <div className="weather-icon">
            <CloudSun size={23} />
          </div>

          <div>
            <strong>Weather</strong>
            <span>
              {decisionResult?.weather?.current?.temperature_c != null
                ? `${decisionResult.weather.current.temperature_c}°C`
                : "Not available"}
            </span>
          </div>
        </div>

        <div className="top-divider"></div>

        <button
          className="notification"
          aria-label="Notifications"
        >
          <Bell size={20} />
        </button>
      </div>
    </header>
  );

  // ============================================================
  // MY FARM PAGE
  // ============================================================

  const renderMyFarm = () => (
    <>
      <div className="background-pattern pattern-top"></div>

      <div className="background-pattern pattern-bottom"></div>

      {renderTopbar()}

      <div className="farm-page">
        {/* HEADER */}

        <section className="farm-page-header">
          <div>
            <span className="farm-eyebrow">
              <Sprout size={15} />
              MY FARM
            </span>

            <h2>Your Farm Overview</h2>

            <p>
              Keep track of your crop, soil, water,
              weather, and current farm condition
              in one place.
            </p>
          </div>

          <button
            className="farm-refresh-button"
            onClick={refreshFarmData}
            disabled={farmRefreshing}
          >
            <RefreshCw
              size={16}
              className={
                farmRefreshing ? "refresh-spinning" : ""
              }
            />

            {farmRefreshing
              ? "Refreshing..."
              : "Refresh Farm Data"}
          </button>
        </section>

        {/* FARM STATUS */}

        <section className="farm-status-banner">
          <div className="farm-status-left">
            <div className="farm-main-icon">
              <Sprout size={27} />
            </div>

            <div>
              <span className="farm-small-label">
                CURRENT FARM
              </span>

              <h3>
                {farmData.crop === "Not available"
                  ? "Farm Overview"
                  : `${farmData.crop} Farm`}
              </h3>

              <p>
                <MapPin size={14} />
                {farmData.region}
              </p>
            </div>
          </div>

          <div className="farm-status-right">
            <div className="status-pill active">
              <span></span>
              {farmData.farmStatus}
            </div>

            <div className="farm-stage">
              <span>Growth Stage</span>

              <strong>{farmData.growthStage}</strong>
            </div>
          </div>
        </section>

        {/* PROFILE + OVERVIEW */}

        <section className="farm-two-column">
          {/* FARMER PROFILE */}

          <div className="farm-card profile-card">
            <div className="farm-card-header">
              <div className="farm-card-heading">
                <div className="farm-card-icon green">
                  <UserRound size={18} />
                </div>

                <div>
                  <span>PROFILE</span>
                  <h3>Farmer Details</h3>
                </div>
              </div>
            </div>

            <div className="profile-main">
              <div className="large-farmer-avatar">
                <Leaf size={30} />
              </div>

              <div>
                <h4>{farmData.farmerName}</h4>

                <p>
                  Farmer ID: {farmData.farmerId}
                </p>
              </div>
            </div>

            <div className="profile-details">
              <div className="profile-detail-item">
                <MapPin size={16} />

                <div>
                  <span>Region</span>
                  <strong>{farmData.region}</strong>
                </div>
              </div>

              <div className="profile-detail-item">
                <CalendarDays size={16} />

                <div>
                  <span>Planting Date</span>
                  <strong>{farmData.plantingDate}</strong>
                </div>
              </div>

              <div className="profile-detail-item">
                <MapPin size={16} />

                <div>
                  <span>Pincode</span>
                  <strong>{farmData.pincode}</strong>
                </div>
              </div>
            </div>
          </div>

          {/* FARM OVERVIEW */}

          <div className="farm-card">
            <div className="farm-card-header">
              <div className="farm-card-heading">
                <div className="farm-card-icon green">
                  <Sprout size={18} />
                </div>

                <div>
                  <span>FARM OVERVIEW</span>
                  <h3>Crop Information</h3>
                </div>
              </div>

              <div className="mini-status">
                <Activity size={14} />
                {farmData.cropHealth}
              </div>
            </div>

            <div className="overview-grid">
              <FarmMetric
                icon={<Sprout size={17} />}
                label="Main Crop"
                value={farmData.crop}
              />

              <FarmMetric
                icon={<Activity size={17} />}
                label="Growth Stage"
                value={farmData.growthStage}
              />

              <FarmMetric
                icon={<CalendarDays size={17} />}
                label="Season"
                value={farmData.season}
              />

              <FarmMetric
                icon={<CheckCircle2 size={17} />}
                label="Crop Health"
                value={farmData.cropHealth}
              />
            </div>
          </div>
        </section>

        {/* SOIL / WATER / WEATHER */}

        <section className="farm-section-heading">
          <div>
            <span>FARM CONDITIONS</span>

            <h3>Soil, Water & Weather</h3>
          </div>

          <p>{farmData.weatherStatus}</p>
        </section>

        <section className="farm-condition-grid">
          {/* SOIL */}

          <div className="farm-condition-card">
            <div className="condition-top">
              <div className="condition-icon soil">
                <FlaskConical size={20} />
              </div>

              <span className="condition-tag">
                SOIL
              </span>
            </div>

            <h3>{farmData.soilCondition}</h3>

            <p>
              Soil type is taken from your farmer profile.
              Live soil measurements are not available.
            </p>

            <div className="condition-footer">
              <span>Last checked</span>

              <strong>
                {farmData.lastSoilCheck}
              </strong>
            </div>
          </div>

          {/* WATER */}

          <div className="farm-condition-card">
            <div className="condition-top">
              <div className="condition-icon water">
                <Droplets size={20} />
              </div>

              <span className="condition-tag">
                WATER
              </span>
            </div>

            <div className="water-value">
              <h3>
                {farmData.soilMoisture}
              </h3>

              <span>Moisture</span>
            </div>

            <div className="moisture-bar">
              <div
                className="moisture-fill"
                style={{
                  width:
                    farmData.soilMoisture === "Not available"
                      ? "0%"
                      : farmData.soilMoisture,
                }}
              ></div>
            </div>

            <p>
              Soil moisture is not available from the
              current farm data source.
            </p>
          </div>

          {/* WEATHER */}

          <div className="farm-condition-card weather-condition-card">
            <div className="condition-top">
              <div className="condition-icon weather">
                <CloudSun size={20} />
              </div>

              <span className="condition-tag">
                WEATHER
              </span>
            </div>

            <div className="temperature-row">
              <h3>{farmData.temperature}</h3>

              <span>{farmData.rainfall}</span>
            </div>

            <div className="weather-details">
              <div>
                <CloudRain size={15} />

                <span>
                  {farmData.humidity}
                </span>
              </div>

              <div>
                <Wind size={15} />

                <span>{farmData.wind}</span>
              </div>
            </div>
          </div>
        </section>

        {/* CROP HEALTH */}

        <section className="farm-card crop-health-card">
          <div className="farm-card-header">
            <div className="farm-card-heading">
              <div className="farm-card-icon green">
                <Activity size={18} />
              </div>

              <div>
                <span>CROP HEALTH</span>

                <h3>Recent Crop Analysis</h3>
              </div>
            </div>

            <div className="health-badge">
              <Activity size={15} />

              {farmData.cropHealth}
            </div>
          </div>

          <div className="health-content">
            <div className="health-main">
              <div className="health-circle">
                <strong>N/A</strong>

                <span>Health</span>
              </div>

              <div className="health-summary">
                <h4>
                  {farmData.recentDiagnosis}
                </h4>

                <p>
                  This is the latest decision-support result;
                  health measurements are not available unless
                  provided by the farm data source.
                </p>
              </div>
            </div>

            <div className="health-last-check">
              <Clock3 size={17} />

              <div>
                <span>Last analysis</span>

                <strong>
                  {farmData.lastAnalysis}
                </strong>
              </div>
            </div>
          </div>

          <div className="farm-info-note">
            <AlertCircle size={16} />

            <span>
              Live farm and crop analysis values
              will be supplied by the backend.
            </span>
          </div>
        </section>

        {/* ======================================================
            UPDATED FARM QUICK ACTIONS
        ====================================================== */}

        <section className="farm-quick-section">
          <div className="farm-section-heading">
            <div>
              <span>FARM TOOLS</span>

              <h3>What would you like to do?</h3>
            </div>
          </div>

          <div className="farm-action-grid">

            {/* DIAGNOSE CROP */}

            <button
              type="button"
              className="farm-action-card"
              onClick={() => {
                setCurrentPage("home");

                setTimeout(() => {
                  fileInputRef.current?.click();
                }, 0);
              }}
            >
              <div className="farm-action-icon green">
                <Sprout size={20} />
              </div>

              <div>
                <strong>Diagnose Crop</strong>

                <span>
                  Analyze a crop image
                </span>
              </div>

              <ChevronRight size={17} />
            </button>

            {/* CHECK WEATHER */}

            <button
              type="button"
              className="farm-action-card"
              onClick={() => {
                setQuestion(
                  "I want a weather update for my farm."
                );

                setCurrentPage("home");
              }}
            >
              <div className="farm-action-icon blue">
                <CloudSun size={20} />
              </div>

              <div>
                <strong>Check Weather</strong>

                <span>
                  Get weather-based advice
                </span>
              </div>

              <ChevronRight size={17} />
            </button>

            {/* SOIL HEALTH */}

            <button
              type="button"
              className="farm-action-card"
              onClick={() => {
                setQuestion(
                  "I want to know about my soil health."
                );

                setCurrentPage("home");
              }}
            >
              <div className="farm-action-icon brown">
                <Wheat size={20} />
              </div>

              <div>
                <strong>Soil Health</strong>

                <span>
                  Ask about your soil
                </span>
              </div>

              <ChevronRight size={17} />
            </button>

          </div>
        </section>
      </div>
    </>
  );

  // ============================================================
  // DASHBOARD
  // ============================================================

  const renderDashboard = () => (
    <>
      <div className="background-pattern pattern-top"></div>

      <div className="background-pattern pattern-bottom"></div>

      {renderTopbar()}

      <div className="content-grid">
        {/* CENTER */}

        <section className="hero-section">
          <div className="welcome">
            <p className="eyebrow">Welcome to</p>

            <h2>
              AGRI <span>Agent</span>
            </h2>

            <h3>Your AI farming assistant</h3>

            <div className="accent-line"></div>

            <p className="description">
              Get decision support for your crops,
              soil, weather, and more.
              <br />
              Upload an image or ask a question
              to get started.
            </p>
          </div>

          {/* QUESTION BOX */}

          <div className="ask-card">
            <form
              className="question-box"
              onSubmit={handleQuestionSubmit}
            >
              <div className="question-icon">
                <MessageCircle size={18} />
              </div>

              <input
                type="text"
                placeholder="Describe what's happening with your crop..."
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                disabled={isProcessing}
              />

              <button
                type="button"
                className="camera-button"
                aria-label="Take crop photo"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                disabled={isProcessing}
              >
                <Camera size={19} />
              </button>

              <button
                type="submit"
                className="send-button"
                aria-label="Send question"
                disabled={isProcessing}
              >
                <Send size={18} />
              </button>
            </form>

            {/* HIDDEN IMAGE INPUT */}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/png, image/jpeg, image/webp"
              style={{ display: "none" }}
              onChange={handleImageUpload}
            />

            {uploadError && (
              <div className="upload-error" role="alert">
                {uploadError}
              </div>
            )}

            {/* SELECTED IMAGE PREVIEW */}

            {selectedImage && (
              <div
                style={{
                  marginTop: "16px",
                  padding: "12px",
                  borderRadius: "14px",
                  border: "1px solid #dfe9df",
                  background: "#f8fbf8",
                }}
              >
                <img
                  src={selectedImage.url}
                  alt="Selected crop"
                  style={{
                    width: "100%",
                    maxHeight: "260px",
                    objectFit: "cover",
                    borderRadius: "10px",
                    display: "block",
                  }}
                />

                <div
                  style={{
                    marginTop: "10px",
                    fontSize: "13px",
                    color: "#526052",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: "10px",
                  }}
                >
                  <span>
                    Selected image:{" "}
                    {selectedImage.name}
                  </span>

                  <div
                    style={{
                      display: "flex",
                      gap: "8px",
                      flexShrink: 0,
                    }}
                  >
                    <button
                      type="button"
                      onClick={() =>
                        fileInputRef.current?.click()
                      }
                      disabled={isProcessing}
                      style={{
                        border: "1px solid #cfdccd",
                        background: "#ffffff",
                        color: "#476047",
                        borderRadius: "8px",
                        padding: "7px 10px",
                        fontSize: "12px",
                        cursor: "pointer",
                      }}
                    >
                      Change
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        if (selectedImage?.url) {
                          URL.revokeObjectURL(
                            selectedImage.url
                          );
                        }

                        setSelectedImage(null);

                        if (fileInputRef.current) {
                          fileInputRef.current.value =
                            "";
                        }
                      }}
                      disabled={isProcessing}
                      style={{
                        border: "1px solid #ead2d2",
                        background: "#ffffff",
                        color: "#a05c5c",
                        borderRadius: "8px",
                        padding: "7px 10px",
                        fontSize: "12px",
                        cursor: "pointer",
                      }}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* LOCAL QUESTION STATUS */}

            {submittedQuestion && (
              <div className="question-status">
                <div>
                  <strong>Your question</strong>

                  <p>{submittedQuestion}</p>
                </div>

                <span>
                  {isProcessing
                    ? "Waiting for analysis service..."
                    : workflowComplete
                    ? "Analysis complete"
                    : "Submitted"}
                </span>
              </div>
            )}

            <div className="or-divider">
              <span></span>

              <p>or</p>

              <span></span>
            </div>

            <button
              className="upload-box"
              type="button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={isProcessing}
            >
              <div className="upload-icon">
                <ImageIcon size={20} />
              </div>

              <div className="upload-text">
                <strong>Upload Crop Image</strong>

                <small>JPG, PNG</small>
              </div>
            </button>
          </div>

          {/* ==================================================
              QUICK TOOLS
          ================================================== */}

          <div className="feature-grid">

            {/* CROP DIAGNOSIS */}

            <button
              className="feature-card green"
              type="button"
              onClick={() => {
                if (selectedImage) {
                  setSubmittedQuestion(
                    question.trim() ||
                      "Crop image submitted for diagnosis."
                  );

                  setCurrentPage("home");

                  runAgentWorkflow();
                } else {
                  setQuestion(
                    "Please upload a crop image for disease and pest diagnosis."
                  );

                  setCurrentPage("home");
                }
              }}
            >
              <div className="feature-icon">
                <Sprout size={22} />
              </div>

              <div className="feature-text">
                <strong>Crop Diagnosis</strong>

                <span>
                  Identify diseases
                  <br />
                  and pests
                </span>
              </div>

              <ChevronRight size={18} />
            </button>

            {/* SOIL HEALTH */}

            <button
              className="feature-card brown"
              type="button"
              onClick={() => {
                setQuestion(
                  "I want to know about my soil health."
                );

                setCurrentPage("home");
              }}
            >
              <div className="feature-icon">
                <Wheat size={22} />
              </div>

              <div className="feature-text">
                <strong>Soil Health</strong>

                <span>
                  Get soil analysis
                  <br />
                  and tips
                </span>
              </div>

              <ChevronRight size={18} />
            </button>

            {/* WEATHER UPDATE */}

            <button
              className="feature-card blue"
              type="button"
              onClick={() => {
                setQuestion(
                  "I want a weather update for my farm."
                );

                setCurrentPage("home");
              }}
            >
              <div className="feature-icon">
                <CloudSun size={22} />
              </div>

              <div className="feature-text">
                <strong>Weather Update</strong>

                <span>
                  Plan your farming
                  <br />
                  better
                </span>
              </div>

              <ChevronRight size={18} />
            </button>

            {/* FARMING GUIDE */}

            <button
              className="feature-card purple"
              type="button"
              onClick={() => navigateTo("guides")}
            >
              <div className="feature-icon">
                <BookOpen size={22} />
              </div>

              <div className="feature-text">
                <strong>Farming Guide</strong>

                <span>
                  Learn and improve
                  <br />
                  your yield
                </span>
              </div>

              <ChevronRight size={18} />
            </button>

          </div>
        </section>

        {/* RIGHT PANEL */}

        <aside className="right-panel">

          {/* AGENT ACTIVITY */}

          <div className="agent-activity">
            <div className="agent-activity-header">
              <div>
                <span className="agent-activity-label">
                  AI WORKFLOW
                </span>

                <h3>Agent Activity</h3>
              </div>

              <div
                className="agent-status-dot"
                style={{
                  background: isProcessing
                    ? "#78a878"
                    : workflowComplete
                    ? "#78a878"
                    : "#aeb8ae",
                }}
              ></div>
            </div>

            <div className="agent-steps">
              {agentSteps.map((agent, index) => {
                const isCompleted =
                  completedAgents.includes(index);

                const isActive =
                  activeAgent === index;

                return (
                  <div
                    key={agent.name}
                    className={`agent-step ${
                      isCompleted
                        ? "completed"
                        : isActive
                        ? "active"
                        : ""
                    }`}
                  >
                    <div className="agent-step-icon">
                      {isCompleted ? (
                        <CheckCircle2 size={15} />
                      ) : isActive ? (
                        <RefreshCw
                          size={15}
                          className="refresh-spinning"
                        />
                      ) : (
                        <span aria-hidden="true">·</span>
                      )}
                    </div>

                    <div>
                      <strong>{agent.name}</strong>

                      <span>
                        {isActive
                          ? "Processing..."
                          : agent.description}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {!isProcessing &&
              !workflowComplete &&
              !workflowError && (
                <div
                  style={{
                    marginTop: "12px",
                    paddingTop: "10px",
                    borderTop:
                      "1px solid #e6eee6",
                    fontSize: "11px",
                    fontWeight: "600",
                    color: "#7b887b",
                  }}
                >
                  Waiting for the real agent
                  workflow.
                </div>
              )}

            {workflowComplete && (
              <div
                style={{
                  marginTop: "12px",
                  paddingTop: "10px",
                  borderTop:
                    "1px solid #e6eee6",
                  fontSize: "11px",
                  fontWeight: "600",
                  color: "#6c956c",
                }}
              >
                <CheckCircle2 size={14} /> Analysis workflow completed
              </div>
            )}

            {workflowError && (
              <div className="workflow-error" role="alert">
                Analysis could not be completed.
              </div>
            )}
          </div>

          {/* QUICK ACCESS */}

          <div className="quick-access">
            <h3>
              <span className="bolt"><Activity size={15} /></span>
              Quick Access
            </h3>

            <QuickItem
              icon={<Sprout />}
              title="My Farm"
              subtitle="View your farm details"
              type="green"
              onClick={() => navigateTo("farm")}
            />

            <QuickItem
              icon={<History />}
              title="Crop History"
              subtitle="Past queries & solutions"
              type="purple"
              onClick={() => navigateTo("history")}
            />

            <QuickItem
              icon={<CloudSun />}
              title="Weather Update"
              subtitle="Current & forecast"
              type="blue"
              onClick={() => navigateTo("home")}
            />

            <QuickItem
              icon={<BookOpen />}
              title="Tips & Guides"
              subtitle="Learn and grow"
              type="orange"
              onClick={() => navigateTo("guides")}
            />
          </div>

          {/* QUOTE */}

          <div className="quote-card">
            <div className="quote-leaf">
              <Leaf size={18} />
            </div>

            <p>
              "Healthy soil,
              <br />
              healthy crops,
              <br />
              a better tomorrow."
            </p>

            <div className="quote-line"></div>
          </div>
        </aside>

        {/* AI DECISION SUPPORT */}

        {decisionResult && (
          <section className="decision-support">
            <div className="decision-header">
              <div>
                <span className="decision-label">
                  AI DECISION SUPPORT
                </span>

                <h3>
                  Your Crop Analysis
                </h3>

                <p>
                  The agents have combined the
                  available evidence to prepare a
                  decision-support result.
                </p>
              </div>

              <div className="decision-confidence">
                <span>Confidence</span>

                <strong>
                  {decisionResult.confidence}
                </strong>
              </div>
            </div>

            <div className="decision-grid">
              <div className="decision-card">
                <div className="decision-card-title">
                  <span className="decision-icon">
                    <Sprout size={15} />
                  </span>

                  <strong>What?</strong>
                </div>

                <h4>
                  {decisionResult.what}
                </h4>

                <p>
                  {decisionResult.whatDescription}
                </p>

                {decisionResult.candidates?.length >
                  0 && (
                  <div className="candidate-list">
                    {decisionResult.candidates.map(
                      (candidate, index) => (
                        <span key={`${candidate}-${index}`}>
                          {candidate}
                        </span>
                      )
                    )}
                  </div>
                )}
              </div>

              <div className="decision-card">
                <div className="decision-card-title">
                  <span className="decision-icon">
                    <Activity size={15} />
                  </span>

                  <strong>Why?</strong>
                </div>

                <p>
                  {decisionResult.why}
                </p>

                <div className="evidence-row">
                  {decisionResult.evidence?.map(
                    (item, index) => (
                      <span key={`${item}-${index}`}>
                        <CheckCircle2 size={13} /> {item}
                      </span>
                    )
                  )}
                </div>
              </div>

              <div className="decision-card">
                <div className="decision-card-title">
                  <span className="decision-icon">
                    <BookOpen size={15} />
                  </span>

                  <strong>Evidence</strong>
                </div>

                <p>
                  {decisionResult.evidenceSummary}
                </p>

                <div className="source-box">
                  <strong>Source</strong>

                  <span>
                    {decisionResult.source}
                  </span>
                </div>
              </div>

              <div className="decision-card action-card">
                <div className="decision-card-title">
                  <span className="decision-icon">
                    <CheckCircle2 size={15} />
                  </span>

                  <strong>
                    Recommended Actions
                  </strong>
                </div>

                <ol>
                  {decisionResult.actions?.map(
                    (action, index) => (
                      <li key={index}>
                        {action}
                      </li>
                    )
                  )}
                </ol>
              </div>
            </div>

            <div className="decision-footer">
              <div className="decision-status">
                <span className="status-check">
                  <CheckCircle2 size={15} />
                </span>

                <div>
                  <strong>
                    Verifier Status
                  </strong>

                  <span>
                    {decisionResult.verifierStatus}
                  </span>
                </div>
              </div>

              <div className="escalation-status">
                <span><AlertCircle size={15} /></span>

                <span>
                  {decisionResult.escalation}
                </span>
              </div>
            </div>
          </section>
        )}
      </div>
    </>
  );

  // ============================================================
  // HISTORY PAGE
  // ============================================================

  const renderHistory = () => {
    if (selectedHistory) {
      return (
        <>
          <div className="background-pattern pattern-top"></div>

          <div className="background-pattern pattern-bottom"></div>

          {renderTopbar()}

          <div className="history-page">
            <button
              className="history-back-button"
              onClick={() =>
                setSelectedHistory(null)
              }
            >
              <ArrowLeft size={15} /> Back to History
            </button>

            <section className="history-detail-header">
              <div>
                <span className="history-eyebrow">
                  ANALYSIS HISTORY
                </span>

                <h2>{selectedHistory.title}</h2>

                <p>
                  {selectedHistory.date} ·{" "}
                  {selectedHistory.crop}
                </p>
              </div>

              <div className="history-detail-status">
                <CheckCircle2 size={16} />

                {selectedHistory.status}
              </div>
            </section>

            <section className="history-detail-card">
              <div className="history-card-heading">
                <div className="history-card-icon green">
                  <Activity size={18} />
                </div>

                <div>
                  <span>ANALYSIS SUMMARY</span>

                  <h3>
                    What the agents found
                  </h3>
                </div>
              </div>

              <div className="history-summary-box">
                <div className="history-summary-main">
                  <span>Possible Result</span>

                  <h3>
                    {selectedHistory.title}
                  </h3>

                  <p>
                    {selectedHistory.summary}
                  </p>
                </div>

                <div className="history-confidence">
                  <span>Confidence</span>

                  <strong>
                    {selectedHistory.confidence}
                  </strong>
                </div>
              </div>
            </section>

            <section className="history-detail-card">
              <div className="history-card-heading">
                <div className="history-card-icon blue">
                  <MessageCircle size={18} />
                </div>

                <div>
                  <span>FARMER QUERY</span>

                  <h3>Your Question</h3>
                </div>
              </div>

              <div className="history-question-box">
                "{selectedHistory.question}"
              </div>
            </section>

            <section className="history-detail-card">
              <div className="history-card-heading">
                <div className="history-card-icon purple">
                  <Activity size={18} />
                </div>

                <div>
                  <span>AI WORKFLOW</span>

                  <h3>Agent Activity</h3>
                </div>
              </div>

              <div className="history-agent-grid">
                {agentSteps.map((agent) => (
                  <div
                    key={agent.name}
                    className="history-agent-item"
                  >
                    <div className="history-agent-check">
                      <CheckCircle2 size={15} />
                    </div>

                    <div>
                      <strong>{agent.name}</strong>

                      <span>Completed</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="history-workflow-footer">
                <CheckCircle2 size={16} />

                {selectedHistory.agents}
              </div>
            </section>

            <section className="history-detail-card">
              <div className="history-card-heading">
                <div className="history-card-icon orange">
                  <BookOpen size={18} />
                </div>

                <div>
                  <span>EVIDENCE</span>

                  <h3>
                    Information Considered
                  </h3>
                </div>
              </div>

              <div className="history-evidence-list">
                <div>
                  <CheckCircle2 size={16} />
                  Crop information
                </div>

                {selectedHistory.imageUsed && (
                  <div>
                    <CheckCircle2 size={16} />
                    Crop image
                  </div>
                )}

                <div>
                  <CheckCircle2 size={16} />
                  Weather information
                </div>

                <div>
                  <CheckCircle2 size={16} />
                  Trusted agricultural knowledge
                </div>
              </div>
            </section>

            <section className="history-detail-card">
              <div className="history-card-heading">
                <div className="history-card-icon green">
                  <Sprout size={18} />
                </div>

                <div>
                  <span>DECISION SUPPORT</span>

                  <h3>Recommended Actions</h3>
                </div>
              </div>

              <div className="history-actions-list">
                {selectedHistory.actions.map(
                  (action, index) => (
                    <div
                      key={index}
                      className="history-action-item"
                    >
                      <span>{index + 1}</span>

                      <p>{action}</p>
                    </div>
                  )
                )}
              </div>

              <div className="history-verifier">
                <div>
                  <CheckCircle2 size={17} />

                  <div>
                    <strong>
                      Verifier Status
                    </strong>

                    <span>
                      Recommendation passed
                      the initial verification.
                    </span>
                  </div>
                </div>

                <span>
                  {selectedHistory.status}
                </span>
              </div>
            </section>
          </div>
        </>
      );
    }

    return (
      <>
        <div className="background-pattern pattern-top"></div>

        <div className="background-pattern pattern-bottom"></div>

        {renderTopbar()}

        <div className="history-page">
          <section className="history-page-header">
            <div>
              <span className="history-eyebrow">
                <Clock3 size={15} />
                ANALYSIS HISTORY
              </span>

              <h2>
                Your Crop Analysis History
              </h2>

              <p>
                Review your previous questions,
                crop analyses, AI decisions, and
                recommendations.
              </p>
            </div>
          </section>

          <section className="history-stats">
            <div className="history-stat-card">
              <div className="history-stat-icon green">
                <Activity size={19} />
              </div>

              <div>
                <span>Total Analyses</span>

                <strong>
                  {historyData.length}
                </strong>
              </div>
            </div>

            <div className="history-stat-card">
              <div className="history-stat-icon blue">
                <CheckCircle2 size={19} />
              </div>

              <div>
                <span>Verified</span>

                <strong>
                  {historyData.filter(
                    (item) =>
                      item.status === "Verified"
                  ).length}
                </strong>
              </div>
            </div>

            <div className="history-stat-card">
              <div className="history-stat-icon purple">
                <Sprout size={19} />
              </div>

              <div>
                <span>Main Crop</span>

                <strong>
                  {farmData.crop}
                </strong>
              </div>
            </div>
          </section>

          <section className="history-list-section">
            <div className="history-section-title">
              <div>
                <span>RECENT ACTIVITY</span>

                <h3>Previous Analyses</h3>
              </div>

              <span className="history-count">
                {historyData.length} records
              </span>
            </div>

            {historyData.length > 0 ? (
              <div className="history-list">
                {historyData.map((item) => (
                  <div
                    key={item.id}
                    className="history-item"
                  >
                    <div className="history-item-icon">
                      <Sprout size={21} />
                    </div>

                    <div className="history-item-main">
                      <div className="history-item-top">
                        <div>
                          <h3>{item.title}</h3>

                          <span>
                            {item.crop} ·{" "}
                            {item.date}
                          </span>
                        </div>

                        <div className="history-status-pill">
                          <CheckCircle2 size={14} />

                          {item.status}
                        </div>
                      </div>

                      <p>{item.question}</p>

                      <div className="history-item-meta">
                        <span>
                          <Activity size={14} />
                          {item.agents}
                        </span>

                        <span>
                          <AlertCircle size={14} />
                          Confidence{" "}
                          {item.confidence}
                        </span>

                        {item.imageUsed && (
                          <span>
                            <ImageIcon size={14} />
                            Image used
                          </span>
                        )}
                      </div>
                    </div>

                    <button
                      className="history-view-button"
                      onClick={() =>
                        setSelectedHistory(item)
                      }
                    >
                      View Analysis

                      <ChevronRight size={16} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="history-empty-state">
                <div className="guides-empty-icon">
                  <History size={30} />
                </div>

                <h3>No analyses yet</h3>

                <p>
                  Your real crop analyses will
                  appear here after the agent
                  workflow is connected.
                </p>

                <button
                  type="button"
                  onClick={() =>
                    navigateTo("home")
                  }
                >
                  Start an Analysis
                </button>
              </div>
            )}
          </section>

          <div className="history-demo-note">
            <AlertCircle size={16} />

            <span>
              Analysis history is currently
              waiting for the backend data
              integration.
            </span>
          </div>
        </div>
      </>
    );
  };

  // ============================================================
  // SETTINGS PAGE
  // ============================================================

  const renderSettings = () => (
    <>
      <div className="background-pattern pattern-top"></div>

      <div className="background-pattern pattern-bottom"></div>

      {renderTopbar()}

      <div className="settings-page">

        {/* SETTINGS HEADER */}

        <section className="settings-page-header">
          <div>
            <span className="settings-eyebrow">
              <Settings size={15} />
              SETTINGS
            </span>

            <h2>Preferences & Account</h2>

            <p>
              Manage your notifications, application
              preferences, and account settings.
            </p>
          </div>
        </section>

        {/* NOTIFICATIONS */}

        <section className="settings-card">

          <div className="settings-card-header">
            <div className="settings-card-icon green">
              <Bell size={19} />
            </div>

            <div>
              <span>NOTIFICATIONS</span>
              <h3>Notification Preferences</h3>
            </div>
          </div>

          <div className="settings-option">
            <div className="settings-option-info">
              <strong>Notifications</strong>

              <span>
                Receive notifications from AGRI Agent.
              </span>
            </div>

            <button
              type="button"
              className={`settings-toggle ${
                notificationsEnabled ? "on" : ""
              }`}
              onClick={() => {
                const next = !notificationsEnabled;

                setNotificationsEnabled(next);

                localStorage.setItem(
                  "agri_notifications",
                  String(next)
                );
              }}
              aria-label="Toggle notifications"
            >
              <span></span>
            </button>
          </div>

          <div className="settings-option">
            <div className="settings-option-info">
              <strong>Weather Alerts</strong>

              <span>
                Get important weather-related alerts.
              </span>
            </div>

            <button
              type="button"
              className={`settings-toggle ${
                weatherAlertsEnabled &&
                notificationsEnabled
                  ? "on"
                  : ""
              }`}
              disabled={!notificationsEnabled}
              onClick={() => {
                const next = !weatherAlertsEnabled;

                setWeatherAlertsEnabled(next);

                localStorage.setItem(
                  "agri_weather_alerts",
                  String(next)
                );
              }}
              aria-label="Toggle weather alerts"
            >
              <span></span>
            </button>
          </div>

          <div className="settings-option">
            <div className="settings-option-info">
              <strong>Crop Analysis Alerts</strong>

              <span>
                Get updates related to crop analysis.
              </span>
            </div>

            <button
              type="button"
              className={`settings-toggle ${
                cropAlertsEnabled &&
                notificationsEnabled
                  ? "on"
                  : ""
              }`}
              disabled={!notificationsEnabled}
              onClick={() => {
                const next = !cropAlertsEnabled;

                setCropAlertsEnabled(next);

                localStorage.setItem(
                  "agri_crop_alerts",
                  String(next)
                );
              }}
              aria-label="Toggle crop analysis alerts"
            >
              <span></span>
            </button>
          </div>

          <div className="settings-option">
            <div className="settings-option-info">
              <strong>Important Farming Alerts</strong>

              <span>
                Receive important alerts that may require
                your attention.
              </span>
            </div>

            <button
              type="button"
              className={`settings-toggle ${
                importantAlertsEnabled &&
                notificationsEnabled
                  ? "on"
                  : ""
              }`}
              disabled={!notificationsEnabled}
              onClick={() => {
                const next = !importantAlertsEnabled;

                setImportantAlertsEnabled(next);

                localStorage.setItem(
                  "agri_important_alerts",
                  String(next)
                );
              }}
              aria-label="Toggle important farming alerts"
            >
              <span></span>
            </button>
          </div>

        </section>

        {/* PREFERENCES */}

        <section className="settings-card">

          <div className="settings-card-header">
            <div className="settings-card-icon blue">
              <Globe size={19} />
            </div>

            <div>
              <span>PREFERENCES</span>
              <h3>Application Preferences</h3>
            </div>
          </div>

          <div className="settings-option">
            <div className="settings-option-info">
              <strong>Language</strong>

              <span>
                Choose the language used in AGRI Agent.
              </span>
            </div>

            <select
              className="settings-select"
              value={language}
              onChange={(event) => {
                const selectedLanguage =
                  event.target.value;

                setLanguage(selectedLanguage);

                localStorage.setItem(
                  "agri_language",
                  selectedLanguage
                );
              }}
            >
              <option value="English">
                English
              </option>

              <option value="Hindi">
                Hindi
              </option>

              <option value="Telugu">
                Telugu
              </option>

              <option value="Tamil">
                Tamil
              </option>
            </select>
          </div>

        </section>

        {/* ACCOUNT */}

        <section className="settings-card">

          <div className="settings-card-header">
            <div className="settings-card-icon purple">
              <UserRound size={19} />
            </div>

            <div>
              <span>ACCOUNT</span>
              <h3>Account Settings</h3>
            </div>
          </div>

          <div className="settings-account-row">
            <div className="settings-account-info">
              <strong>Change Password</strong>

              <span>
                Password management will be connected
                to the backend authentication system.
              </span>
            </div>

            <button
              type="button"
              className="settings-secondary-button"
              disabled
            >
              Coming Soon
            </button>
          </div>

          <div className="settings-logout-row">
            <div className="settings-account-info">
              <strong>Log out of AGRI Agent</strong>

              <span>
                Sign out of this farmer account on
                this device.
              </span>
            </div>

            <button
              type="button"
              className="settings-logout-button"
              onClick={handleLogout}
            >
              <LogOut size={17} />
              Logout
            </button>
          </div>

        </section>

        {/* ABOUT */}

        <section className="settings-about-card">

          <div className="settings-about-icon">
            <Leaf size={22} />
          </div>

          <div>
            <span>ABOUT AGRI AGENT</span>

            <h3>AGRI Agent</h3>

            <p>
              AI-powered farmer decision support
              for better crop decisions.
            </p>

            <small>
              Version 1.0
            </small>
          </div>

        </section>

      </div>
    </>
  );

  // ============================================================
  // MAIN PAGE RENDER
  // ============================================================

  return (
    <div className="app-shell">
      {renderSidebar()}

      <main className="main-content">

        {/* HOME */}

        {currentPage === "home" &&
          renderDashboard()}

        {/* MY FARM */}

        {currentPage === "farm" &&
          renderMyFarm()}

        {/* HISTORY */}

        {currentPage === "history" &&
          renderHistory()}

        {/* ======================================================
            TIPS & GUIDES
        ====================================================== */}

        {currentPage === "guides" && (
          <div className="guides-page">

            {!selectedGuide ? (
              <>
                {/* GUIDES HEADER */}

                <div className="guides-header">
                  <div>
                    <span className="page-eyebrow">
                      KNOWLEDGE CENTER
                    </span>

                    <h1>Tips & Guides</h1>

                    <p>
                      Practical agricultural
                      knowledge to help you
                      understand your crop,
                      soil, weather, and common
                      farming problems.
                    </p>
                  </div>
                </div>

                {/* SEARCH */}

                <div className="guides-search">
                  <BookOpen size={20} />

                  <input
                    type="text"
                    placeholder="Search guides..."
                    value={guideSearch}
                    onChange={(event) =>
                      setGuideSearch(
                        event.target.value
                      )
                    }
                  />

                  {guideSearch && (
                    <button
                      type="button"
                      className="guide-search-clear"
                      onClick={() =>
                        setGuideSearch("")
                      }
                      aria-label="Clear guide search"
                    >
                      <span aria-hidden="true">×</span>
                    </button>
                  )}
                </div>

                {/* CATEGORIES */}

                <div className="guide-categories">
                  {[
                    "All",
                    "Crop Care",
                    "Soil Health",
                    "Weather",
                    "Pest & Disease",
                  ].map((category) => (
                    <button
                      key={category}
                      type="button"
                      className={`guide-category ${
                        guideCategory === category
                          ? "active"
                          : ""
                      }`}
                      onClick={() =>
                        setGuideCategory(category)
                      }
                    >
                      {category}
                    </button>
                  ))}
                </div>

                {/* FILTERED RESULTS */}

                {(() => {
                  const searchText =
                    guideSearch
                      .toLowerCase()
                      .trim();

                  const filteredGuides =
                    guidesData.filter((guide) => {
                      const matchesCategory =
                        guideCategory === "All" ||
                        guide.category ===
                          guideCategory;

                      const matchesSearch =
                        searchText === "" ||
                        guide.title
                          .toLowerCase()
                          .includes(searchText) ||
                        guide.description
                          .toLowerCase()
                          .includes(searchText) ||
                        guide.category
                          .toLowerCase()
                          .includes(searchText) ||
                        guide.content.some(
                          (point) =>
                            point
                              .toLowerCase()
                              .includes(searchText)
                        );

                      return (
                        matchesCategory &&
                        matchesSearch
                      );
                    });

                  return (
                    <>
                      <div className="guides-results-info">
                        <span>
                          {filteredGuides.length}{" "}
                          {filteredGuides.length === 1
                            ? "guide"
                            : "guides"}{" "}
                          available
                        </span>

                        {guideSearch && (
                          <span>
                            Results for "
                            <strong>
                              {guideSearch}
                            </strong>
                            "
                          </span>
                        )}
                      </div>

                      {filteredGuides.length > 0 ? (
                        <div className="guides-grid">
                          {filteredGuides.map(
                            (guide) => (
                              <div
                                className="guide-card"
                                key={guide.id}
                              >
                                <div className="guide-card-top">
                                  <div className="guide-icon">

                                    {guide.icon ===
                                      "sprout" && (
                                      <Sprout
                                        size={24}
                                      />
                                    )}

                                    {guide.icon ===
                                      "soil" && (
                                      <Wheat
                                        size={24}
                                      />
                                    )}

                                    {guide.icon ===
                                      "weather" && (
                                      <CloudRain
                                        size={24}
                                      />
                                    )}

                                    {guide.icon ===
                                      "pest" && (
                                      <AlertCircle
                                        size={24}
                                      />
                                    )}

                                    {guide.icon ===
                                      "water" && (
                                      <Droplets
                                        size={24}
                                      />
                                    )}

                                  </div>

                                  <span className="guide-category-label">
                                    {guide.category}
                                  </span>
                                </div>

                                <h2>
                                  {guide.title}
                                </h2>

                                <p>
                                  {guide.description}
                                </p>

                                <div className="guide-card-bottom">

                                  <span className="guide-read-time">
                                    <Clock3
                                      size={15}
                                    />

                                    {guide.readTime}
                                  </span>

                                  <button
                                    type="button"
                                    className="guide-read-button"
                                    onClick={() =>
                                      setSelectedGuide(
                                        guide
                                      )
                                    }
                                  >
                                    Read Guide

                                    <ChevronRight
                                      size={16}
                                    />
                                  </button>

                                </div>
                              </div>
                            )
                          )}
                        </div>
                      ) : (
                        <div className="guides-empty-state">

                          <div className="guides-empty-icon">
                            <BookOpen size={30} />
                          </div>

                          <h3>
                            No guides found
                          </h3>

                          <p>
                            We couldn't find a
                            guide matching your
                            search. Try another
                            keyword or category.
                          </p>

                          <button
                            type="button"
                            onClick={() => {
                              setGuideSearch("");
                              setGuideCategory("All");
                            }}
                          >
                            Clear Search
                          </button>

                        </div>
                      )}
                    </>
                  );
                })()}
              </>
            ) : (

              /* ==================================================
                 GUIDE DETAIL
              ================================================== */

              <div className="guide-detail-page">

                <button
                  type="button"
                  className="guide-back-button"
                  onClick={() =>
                    setSelectedGuide(null)
                  }
                >
                  <ArrowLeft size={15} /> Back to Guides
                </button>

                <div className="guide-detail-card">

                  {/* DETAIL HEADER */}

                  <div className="guide-detail-top">

                    <div className="guide-detail-icon">

                      {selectedGuide.icon ===
                        "sprout" && (
                        <Sprout size={30} />
                      )}

                      {selectedGuide.icon ===
                        "soil" && (
                        <Wheat size={30} />
                      )}

                      {selectedGuide.icon ===
                        "weather" && (
                        <CloudRain size={30} />
                      )}

                      {selectedGuide.icon ===
                        "pest" && (
                        <AlertCircle
                          size={30}
                        />
                      )}

                      {selectedGuide.icon ===
                        "water" && (
                        <Droplets size={30} />
                      )}

                    </div>

                    <div className="guide-detail-heading">

                      <span className="guide-category-label">
                        {selectedGuide.category}
                      </span>

                      <h1>
                        {selectedGuide.title}
                      </h1>

                      <div className="guide-detail-meta">
                        <Clock3 size={16} />

                        <span>
                          {selectedGuide.readTime}
                        </span>
                      </div>

                    </div>
                  </div>

                  {/* DESCRIPTION */}

                  <p className="guide-detail-description">
                    {selectedGuide.description}
                  </p>

                  {/* CONTENT */}

                  <div className="guide-content">

                    <div className="guide-content-heading">
                      <span>GUIDE CONTENT</span>

                      <h2>Key Points</h2>
                    </div>

                    <div className="guide-points">

                      {selectedGuide.content.map(
                        (point, index) => (
                          <div
                            className="guide-point"
                            key={index}
                          >

                            <div className="guide-point-number">
                              {index + 1}
                            </div>

                            <p>{point}</p>

                          </div>
                        )
                      )}

                    </div>
                  </div>

                  {/* AGRI AGENT NOTE */}

                  <div className="guide-detail-note">

                    <div className="guide-note-icon">
                      <Leaf size={20} />
                    </div>

                    <div>
                      <strong>
                        AGRI Agent Reminder
                      </strong>

                      <p>
                        This guide provides
                        general agricultural
                        information. For
                        crop-specific problems,
                        use the AI analysis
                        workflow with your farm
                        details and crop image
                        when available.
                      </p>
                    </div>

                  </div>

                  {/* BACK BUTTON */}

                  <button
                    type="button"
                    className="guide-back-bottom"
                    onClick={() =>
                      setSelectedGuide(null)
                    }
                  >
                    <ArrowLeft size={15} /> Back to Guides
                  </button>

                </div>
              </div>
            )}
          </div>
        )}

        {/* SETTINGS */}

        {currentPage === "settings" &&
          renderSettings()}

        {/* FOOTER */}

        <footer>
          <span>
            AGRI Agent · Farmer Decision Support
          </span>
        </footer>

      </main>
    </div>
  );
}

// ============================================================
// FARM METRIC COMPONENT
// ============================================================

function FarmMetric({ icon, label, value }) {
  return (
    <div className="farm-metric">
      <div className="farm-metric-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>

        <strong>{value}</strong>
      </div>
    </div>
  );
}

// ============================================================
// QUICK ITEM
// ============================================================

function QuickItem({
  icon,
  title,
  subtitle,
  type,
  onClick,
}) {
  return (
    <button
      type="button"
      className={`quick-item ${type}`}
      onClick={onClick}
    >
      <div className="quick-icon">
        {icon}
      </div>

      <div className="quick-text">
        <strong>{title}</strong>

        <span>{subtitle}</span>
      </div>

      <ChevronRight size={17} />
    </button>
  );
}

export default App;
