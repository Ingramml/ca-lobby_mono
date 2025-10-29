# CA Lobby - California Lobbying Database & Web Application

Full-stack monorepo for visualizing California lobbying disclosure data from the CAL-ACCESS system.

## Project Structure

```
ca-lobby_mono/
├── backend/          # Python data pipeline, BigQuery views & schemas
│   ├── pipeline/     # ETL scripts for data ingestion
│   ├── docs/         # Backend documentation
│   └── *.sql         # BigQuery view definitions
├── frontend/         # React web application
│   ├── src/          # React components and application code
│   ├── public/       # Static assets
│   └── docs/         # Frontend documentation
└── docs/             # Shared project documentation
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Run data pipeline
python run_download.py
python run_upload_pipeline.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The application will open at http://localhost:3000

## Documentation

- **Backend Documentation**: [backend/docs/](backend/docs/)
- **Frontend Documentation**: [frontend/docs/](frontend/docs/)
- **Database Strategy**: [docs/DATABASE_STRATEGY_RECOMMENDATION.md](docs/DATABASE_STRATEGY_RECOMMENDATION.md)
- **Architecture Overview**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Technology Stack

**Backend:**
- Python 3.x
- Google BigQuery
- BigLocalNews.org API

**Frontend:**
- React 18
- Material-UI / Tailwind CSS
- Recharts for data visualization

## Data Source

This project uses California lobbying disclosure data from the [CAL-ACCESS database](http://cal-access.sos.ca.gov/), accessed via [BigLocalNews.org](https://biglocalnews.org/).

## License

[Specify your license here]

## Contributing

This is a monorepo project. When contributing:
- Backend changes go in `backend/`
- Frontend changes go in `frontend/`
- Shared documentation goes in `docs/`

For questions or issues, please contact [your contact info].
