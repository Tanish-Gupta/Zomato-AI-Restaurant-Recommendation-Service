# AI Restaurant Recommendation Service - Architecture

## Project Overview

An intelligent restaurant recommendation system that leverages LLM capabilities to provide personalized restaurant suggestions based on user preferences. The system uses the Zomato restaurant dataset from Hugging Face and integrates with an LLM to deliver natural language recommendations.

**Dataset Source:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│  │   Web UI    │    │  REST API   │    │     CLI     │                      │
│  │  (Gradio)   │    │   Client    │    │   Client    │                      │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                      │
└─────────┼──────────────────┼──────────────────┼─────────────────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      FastAPI Application                             │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  POST /recommend     - Get restaurant recommendations                │    │
│  │  GET  /cuisines      - List available cuisines                       │    │
│  │  GET  /locations     - List available locations                      │    │
│  │  GET  /health        - Service health check                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           │
│  │  Recommendation  │  │   LLM Service    │  │  Data Service    │           │
│  │     Service      │◄─┤                  │  │                  │           │
│  │                  │  │  - Prompt Build  │  │  - Query         │           │
│  │  - Orchestrates  │  │  - LLM Call      │  │  - Filter        │           │
│  │    workflow      │  │  - Response Parse│  │  - Transform     │           │
│  └────────┬─────────┘  └──────────────────┘  └────────┬─────────┘           │
│           │                                           │                      │
│           └───────────────────┬───────────────────────┘                      │
│                               ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      Restaurant Repository                           │    │
│  │                   (Data Access Layer)                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           │
│  │  Hugging Face    │  │  Local Cache     │  │  Processed       │           │
│  │  Dataset         │─▶│  (Parquet/CSV)   │─▶│  DataFrame       │           │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Groq LLM API                                   │   │
│  │              (Llama 3 / Mixtral - Ultra-fast inference)               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
zomato-ai-recommendation/
├── src/
│   ├── __init__.py              # Main package exports
│   ├── config.py                # Configuration management
│   ├── main.py                  # FastAPI application entry point
│   │
│   ├── phase1_data/             # PHASE 1: Data Foundation
│   │   ├── __init__.py
│   │   ├── loader.py            # HuggingFace dataset loader
│   │   ├── preprocessor.py      # Data cleaning and transformation
│   │   └── repository.py        # Data access layer with filtering
│   │
│   ├── phase2_llm/              # PHASE 2: Groq LLM Integration
│   │   ├── __init__.py
│   │   ├── groq_service.py      # Groq API interaction
│   │   ├── prompts.py           # Prompt templates
│   │   └── response_parser.py   # LLM response parsing
│   │
│   ├── phase3_api/              # PHASE 3: API Development
│   │   ├── __init__.py
│   │   ├── routes.py            # FastAPI route definitions
│   │   ├── schemas.py           # Pydantic request/response models
│   │   └── recommendation.py    # Recommendation orchestration
│   │
│   ├── phase4_ui/               # PHASE 4: User Interface
│   │   ├── __init__.py
│   │   └── gradio_app.py        # Gradio web interface
│   │
│   └── phase5_optimization/     # PHASE 5: Enhancement & Optimization
│       ├── __init__.py
│       ├── caching.py           # Response caching
│       └── cli.py               # Command-line interface
│
├── tests/
│   ├── __init__.py
│   ├── phase1/                  # Tests for Phase 1
│   │   ├── __init__.py
│   │   └── test_data.py
│   ├── phase2/                  # Tests for Phase 2
│   │   ├── __init__.py
│   │   └── test_llm.py
│   ├── phase3/                  # Tests for Phase 3
│   │   ├── __init__.py
│   │   └── test_api.py
│   └── phase4/                  # Tests for Phase 4
│       ├── __init__.py
│       └── test_ui.py
│
├── data/
│   └── cache/                   # Local dataset cache (parquet)
│
├── .env.example                 # Environment variables template
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── ARCHITECTURE.md              # This file
```

---

## Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │    │   Filter    │    │   Build     │    │   Call      │
│   Input     │───▶│   Dataset   │───▶│   Prompt    │───▶│   LLM       │
│             │    │             │    │             │    │             │
│ - Price     │    │ Match user  │    │ Include:    │    │ Send prompt │
│ - Location  │    │ criteria    │    │ - Context   │    │ with        │
│ - Rating    │    │ from        │    │ - Filtered  │    │ restaurant  │
│ - Cuisine   │    │ restaurant  │    │   results   │    │ data        │
│             │    │ data        │    │ - User pref │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Display   │    │   Format    │    │   Parse     │    │   LLM       │
│   to User   │◀───│   Response  │◀───│   LLM       │◀───│   Response  │
│             │    │             │    │   Output    │    │             │
│ Natural     │    │ Structure   │    │ Extract     │    │ Ranked      │
│ language    │    │ as JSON     │    │ recommen-   │    │ suggestions │
│ recommen-   │    │ or text     │    │ dations     │    │ with        │
│ dations     │    │             │    │             │    │ reasoning   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## API Specification

### Request Schema

```python
class RecommendationRequest:
    cuisine: Optional[str]           # e.g., "Italian", "Indian", "Chinese"
    location: Optional[str]          # e.g., "Connaught Place", "Koramangala"
    price_range: Optional[str]       # e.g., "low", "medium", "high"
    min_rating: Optional[float]      # e.g., 3.5, 4.0
    num_recommendations: int = 5     # Number of recommendations to return
    additional_preferences: str = "" # Free text for extra context
```

### Response Schema

```python
class RestaurantRecommendation:
    name: str
    cuisine: str
    location: str
    rating: float
    price_range: str
    reason: str                      # LLM-generated explanation

class RecommendationResponse:
    recommendations: List[RestaurantRecommendation]
    summary: str                     # LLM-generated summary
    query_context: dict              # Original query parameters
```

---

## Implementation Phases

### Phase 1: Data Foundation
**Goal:** Establish data pipeline and basic data access

**Tasks:**
- [ ] Set up project structure and dependencies
- [ ] Implement Hugging Face dataset loader
- [ ] Create data preprocessing pipeline
  - Handle missing values
  - Normalize price ranges
  - Clean cuisine and location fields
- [ ] Build restaurant repository with filtering capabilities
- [ ] Implement local caching mechanism
- [ ] Write unit tests for data layer

**Deliverables:**
- Working data loader with caching
- Cleaned and normalized dataset
- Repository with query methods

---

### Phase 2: Groq LLM Integration
**Goal:** Integrate Groq LLM for ultra-fast intelligent recommendations

**Tasks:**
- [ ] Set up Groq API configuration and authentication
- [ ] Select appropriate model (Llama 3 70B / Mixtral 8x7B)
- [ ] Design prompt templates for recommendations
  - System prompt with context
  - User preference formatting
  - Restaurant data injection
- [ ] Implement Groq LLM service with retry logic
- [ ] Create response parsing utilities
- [ ] Add error handling for API failures
- [ ] Write integration tests

**Deliverables:**
- Groq LLM service integration
- Prompt template system
- Response parser

---

### Phase 3: API Development
**Goal:** Build REST API for the recommendation service

**Tasks:**
- [ ] Set up FastAPI application
- [ ] Implement API routes
  - `/recommend` - Main recommendation endpoint
  - `/cuisines` - List available cuisines
  - `/locations` - List available locations
  - `/health` - Health check
- [ ] Create Pydantic schemas for validation
- [ ] Implement recommendation service (orchestration layer)
- [ ] Add request logging and monitoring
- [ ] Write API tests

**Deliverables:**
- Fully functional REST API
- API documentation (auto-generated by FastAPI)
- Request/response validation

---

### Phase 4: User Interface
**Goal:** Create user-friendly interface for interacting with the service

**Tasks:**
- [ ] Build Gradio web interface
  - Dropdown for cuisine selection
  - Location input/selection
  - Price range slider
  - Rating filter
  - Results display area
- [ ] Connect UI to API endpoints
- [ ] Add loading states and error handling
- [ ] Style the interface

**Deliverables:**
- Interactive web UI
- User-friendly recommendation flow

---

### Phase 5: Enhancement & Optimization
**Goal:** Improve performance and add advanced features

**Tasks:**
- [ ] Add response caching for repeated queries
- [ ] Implement rate limiting
- [ ] Optimize Groq model selection based on query complexity
- [ ] Create CLI interface for power users
- [ ] Performance optimization
  - Lazy loading of dataset
  - Efficient filtering algorithms
- [ ] Add logging and monitoring
- [ ] Documentation completion

**Deliverables:**
- Production-ready service
- Complete documentation
- CLI tool

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language** | Python 3.10+ | Primary development language |
| **Web Framework** | FastAPI | REST API development |
| **Data Handling** | Pandas, Datasets (HF) | Data loading and manipulation |
| **LLM Provider** | Groq | Ultra-fast LLM inference |
| **LLM Models** | Llama 3 70B / Mixtral 8x7B | Language model for recommendations |
| **LLM SDK** | groq-python | Groq API interaction |
| **UI Framework** | Gradio | Web interface |
| **Validation** | Pydantic | Request/response validation |
| **Testing** | Pytest | Unit and integration testing |
| **Environment** | python-dotenv | Configuration management |

---

## Configuration

### Environment Variables

```bash
# Groq LLM Configuration
GROQ_API_KEY=gsk_xxx             # Groq API key (get from console.groq.com)
GROQ_MODEL=llama3-70b-8192       # Options: llama3-70b-8192, llama3-8b-8192, mixtral-8x7b-32768

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# Data Settings
CACHE_DIR=./data/cache
DATASET_NAME=ManikaSaini/zomato-restaurant-recommendation
```

### Groq Model Options

| Model | Context Window | Best For |
|-------|----------------|----------|
| `llama3-70b-8192` | 8,192 tokens | Highest quality recommendations |
| `llama3-8b-8192` | 8,192 tokens | Faster responses, good quality |
| `mixtral-8x7b-32768` | 32,768 tokens | Large context (many restaurants) |

---

## Key Design Decisions

### 1. Pre-filtering Before LLM
Filter restaurants based on user criteria **before** sending to LLM. This:
- Reduces token usage and cost
- Provides more relevant context to the LLM
- Improves response quality and speed

### 2. LLM as Ranker & Explainer
The LLM's role is to:
- Rank the pre-filtered restaurants based on overall fit
- Generate natural language explanations for recommendations
- Provide a cohesive summary of the suggestions

### 3. Separation of Concerns
Clear separation between:
- **Data Layer:** Handles data loading, caching, and basic queries
- **Service Layer:** Business logic and orchestration
- **API Layer:** Request handling and validation

### 4. Groq for Ultra-Fast Inference
Using Groq as the LLM provider because:
- **Speed:** Groq's LPU (Language Processing Unit) delivers industry-leading inference speed
- **Cost-effective:** Competitive pricing for high-throughput applications
- **Quality models:** Access to Llama 3 and Mixtral models
- **Low latency:** Essential for real-time restaurant recommendations

---

## Sample Prompt Structure

```
System: You are a restaurant recommendation assistant. Based on the user's 
preferences and the available restaurant data, provide personalized 
recommendations with explanations.

User Preferences:
- Cuisine: {cuisine}
- Location: {location}
- Price Range: {price_range}
- Minimum Rating: {min_rating}

Available Restaurants:
{formatted_restaurant_list}

Instructions:
1. Analyze the restaurants based on the user's preferences
2. Rank the top {num_recommendations} restaurants
3. Provide a brief explanation for each recommendation
4. Include a summary of your recommendations
```

---

## Success Metrics

- **Response Time:** < 2 seconds for recommendation requests (leveraging Groq's fast inference)
- **Relevance:** Recommendations match user criteria
- **User Experience:** Intuitive UI with clear explanations
- **Reliability:** 99% uptime for API endpoints

---

## Future Enhancements (Out of Scope)

- User authentication and preference history
- Semantic search using embeddings
- Multi-language support
- Restaurant image integration
- Real-time data updates from Zomato API
- Collaborative filtering based on similar users
