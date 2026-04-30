# 🍱 AI-Powered Smart Canteen Recommendation System
> **CS242: Object-Oriented Programming Project**  
> A robust FastAPI-based backend that uses Generative AI (Gemini) to provide intelligent dining recommendations.

## 🌟 Key Features
- **AI Decision Engine**: Integrates with Google Gemini 1.5 Flash to analyze crowd density (50%), distance (30%), and trends (20%) for human-like advice.
- **Advanced OOP Architecture**: Implements strict Object-Oriented principles including Encapsulation, Behavioral Interaction, and State Validation.
- **Real-time Data Simulation**: Analyzes historical crowd trends to predict future dining comfort.
- **Precise Geolocation**: Uses verified building-center coordinates for accurate distance calculations.

## 🛠 Technology Stack
- **Framework**: FastAPI (Python)
- **AI Service**: Google GenAI SDK (Gemini 1.5 Flash)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Data Analysis**: Pandas (for CSV/Excel data cleaning)
- **Validation**: Pydantic v2

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- PostgreSQL Database

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/dr-benny/cs242-backend.git
cd cs242-backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=canteen_db
GEMINI_API_KEY=your_gemini_api_key_from_ai_studio
```

### 4. Database Initialization
Seed the database with initial canteen and crowd data:
```bash
python scripts/seed.py
```

### 5. Running the Application
```bash
uvicorn canteen_system.app.main:app --reload --port 8001
```

## 📍 API Endpoints
- **Interactive Documentation**: `http://127.0.0.1:8001/docs` (Swagger UI)
- **Get All Canteens**: `GET /canteens/all`
- **Get Smart Recommendation**: `GET /canteens/recommend?lat={lat}&lng={lng}&start_time={YYYY-MM-DD HH:MM}&end_time={YYYY-MM-DD HH:MM}`

## 📐 Architecture & OOP Compliance
This project strictly follows the course requirements for Object-Oriented Programming:
- **Encapsulation**: All models use private attributes (`_`) with proper `@property` getters/setters.
- **Behavioral Methods**: Classes like `User` and `Canteen` contain logic-rich methods (e.g., `calculateOccupancyStatus`).
- **Robustness**: Centralized exception handling via `CanteenAppError` and custom middleware.
- **MVC Pattern**: Clear separation between Models, Managers (Services), and Controllers (Routers).

---
*Developed as part of the CS242 curriculum.*
