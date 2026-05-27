# Visual Version Control System (VCS) Engine

A full-stack implementation of a custom version control system simulator. The project features a decoupled architecture, combining a lightweight, high-performance Python backend with an interactive graph visualization frontend to map out commit histories, dynamic branching, and branch merging in real time.

---

## Technical Highlights

* **Content-Addressable Storage:** Implements a Git-inspired architecture where code changes, directories (trees), and commits are converted into unique cryptographic hashes for immutable storage.
* **Dynamic Directed Acyclic Graph (DAG):** Automatically tracks and renders the repository's structural history canvas, mapping out precise node lineages and historical paths.
* **Multi-Parent Branch Merging:** Features backend merging logic that generates custom merge commits pointing to two distinct parent branches simultaneously.
* **Persistent State Machine:** Uses a localized data storage system to ensure repository history, branch states, and operation logs persist across server restarts.

---

## Architecture & API Blueprints

The application uses a completely decoupled REST API structure to handle all version control calculations asynchronously:

* `POST /commit` : Receives data payload, hashes the content, updates the branch head pointer, and records the commit.
* `POST /branch` : Spawns a named reference pointer referencing the current active commit hash.
* `POST /checkout` : Updates the active workspace state to point to a specific branch or isolated commit node.
* `POST /merge` : Merges changes from a source branch into the target branch, automatically creating a dual-parent commit node.
* `GET /graph` : Compiles the current storage matrix into a node-and-edge layout optimized for the client-side graphics renderer.

---

## Core Technology Stack

* **Backend Framework:** Python / FastAPI (Asynchronous ASGI application routing)
* **Data Validation:** Pydantic v2 (Input schema validation models)
* **Frontend UI Canvas:** JavaScript / Vis-Network Engine (Dynamic graph visualization)
* **CSS Framework:** Tailwind CSS Core CDN (Dark-mode interfaces)

---

## Production Startup Guide

To spin up the development engine locally, follow these execution steps:

1. Install Dependencies:
   ```bash
   pip install -r requirements.txt

2. Launch the ASGI Server:
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

3. Access the Interfaces:
~ Main Dashboard: Open http://localhost:8000 in your web browser.
~ Interactive API Explorer: Open http://localhost:8000/docs for the automatic Swagger UI playground.
