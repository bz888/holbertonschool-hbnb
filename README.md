# HBnB

This repository contains two application directories:

- `app/` — the Flask API and database layer.
- `client/` — the vanilla JavaScript frontend.

## Setup

Clone the repository and move into its root directory:

```bash
git clone https://github.com/bz888/holbertonschool-hbnb.git
```

### Backend

Follow the [backend setup instructions](app/README.md) to install the Python
dependencies and start the Flask API on port `8080`.

### Frontend

Keep the Flask API running on port `8080`. In a second terminal, move to the
`client/` directory from the repository root and start a local HTTP server:

```bash
cd client/
python -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser. The
frontend must be served over HTTP because it uses JavaScript modules.
