# Multi-Tenant Application with Flask and Citus

A scalable, secure multi-tenant application leveraging Flask and Citus (distributed PostgreSQL) for efficient tenant isolation, sharding, and horizontal scaling.

## Table of Contents

- [Multi-Tenancy Overview](#multi-tenancy-overview)
- [Database Design](#database-design)
  - [Schema Overview](#schema-overview)
  - [Sharding Strategy](#sharding-strategy)
- [System Architecture](#system-architecture)
  - [Web App Workflow](#web-app-workflow)
  - [Application layer workflow](#application-layer-workflow)
  - [Database layer workflow](#database-layer-workflow)
  - [Deployment layer workflow](#deployment-layer-workflow)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Citus Monitoring Guide with Docker Access](#citus-monitoring-guide-with-docker-access)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Development Guide](#development-guide)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)


## Multi-Tenancy Overview


This application provides a robust multi-tenant architecture with secure data isolation using Citus' sharding capabilities. Key features include:

- **Tenant Isolation**: Data separation via `tenant_id` sharding key
- **Horizontal Scaling**: Citus distributes data across worker nodes
- **Colocation**: Optimized joins for `users` and `notes` tables
- **Security**: Encrypted credentials and tenant-specific constraints

## Database Design

### Schema Overview

<img src="https://github.com/Bahar0900/MultiTenant-Application-with-Flask-and-Citus/blob/7d6351f9d5111082dd764f5b124b6e5fac649477/images/schema_Diagram.drawio.png?raw=true" alt="Schema Diagram">

The database consists of three main tables:

- **shared.tenants** (Reference Table):
  - Columns: `id`, `name`, `created_at`
  - Replicated across all nodes for fast access
- **shared.users** (Distributed Table):
  - Columns: `id`, `tenant_id`, `username`, `email`, `password`, `created_at`
  - Sharded by `tenant_id` with unique constraints per tenant
- **notes** (Distributed Table):
  - Columns: `id`, `content`, `user_id`, `created_at`, `updated_at`
  - Sharded by `user_id`, colocated with `users`

### Sharding Strategy

<img src="https://github.com/poridhioss/MultiTenant-Application-with-Flask-and-Citus/blob/42581ae744685afd4a6c75ff86235272933f18d1/images/shardingstrategy.svg" height='500' width='500'>

- **Hash-Based Sharding**: Uses `tenant_id` (for `users`) and `user_id` (for `notes`) as distribution keys
- **Colocation**: `notes` table is colocated with `users` for efficient joins
- **Reference Tables**: `tenants` table is replicated across all nodes

## System Architecture
### Web App workflow
<img src="https://github.com/poridhioss/MultiTenant-Application-with-Flask-and-Citus/blob/f3469419da650db07fd38e63153da013a94c58cb/images/completesystem.drawio.svg" >

- The client browser sends a **Request** to the Web Server.
- The Web Server forwards the **Request for Page Generation** to the Application Server.
- The Application Server processes the request and generates a **Dynamically Generated Page**.
- The **Dynamically Generated Page** is sent back to the Web Server.
- The Web Server sends the **Response** (containing the dynamically generated page) to the client browser.

### Application Layer Workflow
<img src="https://github.com/poridhioss/MultiTenant-Application-with-Flask-and-Citus/blob/1b01446f3c9f228d32efec17e7b0253e42cbc0d5/images/flaskserver.drawio%20(1).svg">

  - The Flask Server receives a **Request** from the Web Browser, typically an HTTP request (e.g., GET or POST) initiated by a user action like accessing a URL or submitting a form.
  - The request is routed to the appropriate handler using **routes.py**, which defines URL routes and maps them to specific functions (e.g., mapping `/home` to a homepage function).
  - The mapped **Functions** (written in Python) are executed, performing tasks such as:
    - Processing user inputs (e.g., form data).
    - Executing application logic or computations.
    - Preparing data for rendering or further processing.
  - If a webpage needs to be rendered, the function uses **Templates** (HTML files with embedded Python code via a templating engine like Jinja2). The function passes data to the template, which is rendered into a dynamic webpage.
  - If a redirect is required (e.g., after form submission), the function uses **Redirects** to send the browser to a new route.
  - The Flask Server sends the rendered webpage or redirect response back to the Web Browser for display.
  
### Database layer workflow
<img src="https://github.com/poridhioss/MultiTenant-Application-with-Flask-and-Citus/blob/c74f58253062c72b02809e0d8e3bd475ff66630b/images/citus%20updated_again.drawio.svg">

- The client sends an HTTP POST request to the Flask App (running on port web:5000) with the endpoint `/api/notes` and a payload containing the note content (content: Test note).
- The Flask App processes the request and sends an SQL INSERT statement to the Citus Coordinator (running on citus-master:5432, hosted on Docker Daemon on Host rpi-01) to insert the note into the `notes` table with the provided content and user ID (content, userId).
- The Citus Coordinator, operating within the `citus-overlay-network`, executes the SQL INSERT operation and distributes the task to the Citus Workers (running on separate Docker Daemons on Hosts rpi-02 and rpi-03). The Coordinator routes the data to the appropriate shards based on the user ID.
- The Citus Workers process the INSERT operation, store the note in their respective shards, and send an Acknowledgement back to the Citus Coordinator to confirm the operation’s success.
- The Citus Coordinator compiles the results and returns a Query Result containing the `note_id` of the newly created note to the Flask App.
- The Flask App finalizes the request by returning a JSON response to the client, indicating the note has been created (`note_created`).

### Deployment layer workflow
<img src="https://github.com/poridhioss/MultiTenant-Application-with-Flask-and-Citus/blob/9984a80c0cf7b017b51366f2e5d33538deecf860/images/docker.drawio.svg">

- The process begins with a browser sending an **http://localhost:5000** request to access the web application hosted on the Host Machine.
- The Host Machine runs a **Docker Service**, which is responsible for containerizing and managing the application's components.
- Docker deploys the **Frontend** (represented by `webapp`), which receives the HTTP request. The Frontend's role is to handle the user interface and client-side logic.
- The Frontend initiates an **API call** to the **Backend**, which is also containerized within Docker. This call requests data or operations to be performed.
- The Backend, deployed as a separate container, processes the API call by performing **API Operations**. It interacts with a **DB** (database) to handle **Data Operations**, such as retrieving or storing data.
- The Backend sends an **API response** back to the Frontend with the requested data or operation result.
- The Frontend then generates a **response** and sends it back to the browser, completing the request cycle.
- Docker's role is critical as it:
  - Provides containerization, ensuring the Frontend and Backend run in isolated environments with their dependencies.
  - Simplifies deployment by packaging the application and its environment into portable containers.
  - Enables scalability and consistency across different Host Machines by managing these containers efficiently.
    
## Getting Started

### Prerequisites

- **Docker** 20.10+ (required for containerized services)
- **Docker Compose** 1.29+ (for managing multi-container setup)
- **Python** 3.9+ (for running Flask application)
- **Git** (for cloning the repository)
- **curl** (for testing API endpoints)
- **psql** (optional, for manual database interaction)

Ensure these tools are installed on your system before proceeding. You can verify Docker and Docker Compose versions with:

```bash
docker --version
docker-compose --version
```

# 🛠 Setup Instructions

## 📥 1. Clone the Repository

First, clone the project and navigate into the directory:

```bash
git clone https://github.com/poridhioss/MultiTenant-Application-with-Flask-and-Citus.git
cd MultiTenant-Application-with-Flask-and-Citus
```

## 🐳 2. Start Docker Containers

Launch the Flask application and the Citus cluster using Docker Compose:

```bash
docker-compose up --build
```

Check running containers:

```bash
docker ps
```

**Expected:** You should see two containers running:
- `multitenant-application-with-flask-and-citus-citus-worker-1`
- `multitenant-application-with-flask-and-citus-web-1`
- `multitenant-application-with-flask-and-citus-citus-master-1`

## ✅ 3. Verify Services

- **Flask App:** Visit [http://localhost:5000](http://localhost:5000) in your browser.
- **Citus Cluster Health:**

Run this to see active worker nodes:

```bash
docker exec -it multitenant-application-with-flask-and-citus-citus-master-1 psql -U postgres -c "SELECT * FROM citus_get_active_worker_nodes();
```
**Expected:** active worker nodes:
- `citus-worker |      5432`
---

## 🔬 4. Test API Endpoints with `curl`

### 🔐 Register a New User

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser&email=newuser@example.com&password=Password123&tenant_name=NewOrg"
```

**Expected:** HTML page with "Redirecting to login".

---

### 🔑 Login User

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -c cookies.txt \
  -d "email=newuser@example.com&password=Password123"
```

**Expected:** HTML redirect to dashboard.

---

### 📝 Create Note

```bash
curl -X POST http://localhost:5000/notes \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -b cookies.txt \
  -d "content=This is my first note"
```

**Expected:** HTML with confirmation and notes list.

---

### 📄 Retrieve Notes

```bash
curl -X GET http://localhost:5000/notes -b cookies.txt
```

**Expected:** HTML page showing list of notes.

---

### 🚪 Logout

```bash
curl -b cookies.txt http://localhost:5000/logout
```

**Expected:** HTML redirect to homepage (`/`).

---

## 🔌 API Endpoints Summary

| Method | Endpoint       | Description                           |
|--------|----------------|---------------------------------------|
| POST   | /register  | Register a new tenant or user         |
| POST   | /login     | Authenticate user and begin session   |
| GET    | /notes     | Fetch notes for the logged-in user    |
| POST   | /notes     | Create a note for the current user    |


---

# 📈 Citus Monitoring Guide (Docker-Based)

## 🐳 Step 1: List Running Containers

```bash
docker ps
```

**Expected:** You should see two containers running:
- `multitenant-application-with-flask-and-citus-citus-worker-1`
- `multitenant-application-with-flask-and-citus-web-1`
- `multitenant-application-with-flask-and-citus-citus-master-1`

---

## 📦 Step 2: Enter the Citus Master Container

```bash
docker exec -it multitenant-application-with-flask-and-citus-citus-master-1 bash
```

---

## 🐘 Step 3: Access PostgreSQL

```bash
psql -U postgres
```

### List databases:

```sql
\l
```

### Connect to the desired database (likely `postgres`):

```sql
\c postgres
```

**Expected:** Confirmation that you're connected.

### List schemas:

```sql
/dn
```

### List shared tables:

```sql
\dt shared.*
```

### View tenant data:

```sql
SELECT * FROM shared.tenants;
```

**Expected:** Shows tenant name, e.g., `NewOrg`.

### View users:

```sql
SELECT * FROM shared.users;
```

**Expected:** Shows user info (e.g., `newuser@example.com`).

### View notes:

```sql
SELECT * FROM public.notes;
```

**Expected:** Shows all user notes.

---

## 📡 Step 4: Monitor Cluster & Shard Health

### 🗂 List Distributed Tables

```sql
SELECT * FROM citus_tables;
```

### 📦 View Shard Placements

```sql
SELECT * FROM pg_dist_shard;
```

**Example Output:**

| Table        | Shard ID | ... | Min Value      | Max Value      |
|--------------|----------|-----|----------------|----------------|
| shared.users | 102009   | ... | -2147483648    | -2013265921    |

This means records with shard key in this range go to shard `102009`.

### 🔁 Monitor Active Queries

```sql
SELECT * FROM pg_stat_activity WHERE datname = 'your_database_name';
```

---

## 🧰 Troubleshooting

### 🔍 Test DB Connection

```bash
docker-compose exec citus-master psql -U postgres -d postgres -c "SELECT 1"
```

If this fails, check logs or verify `DATABASE_URL` in `.env`.

### 📜 View Logs

```bash
docker-compose logs citus-master
docker-compose logs web
docker-compose logs citus-worker
```

### ♻️ Reset Docker Containers & Data

```bash
docker-compose down -v
docker-compose up -d
```

## Contributing

Contributions are welcome! Please:

- Submit issues or pull requests via [GitHub Issues](https://github.com/Bahar0900/MultiTenant-Application-with-Flask-and-Citus/issues)
- Follow **PEP 8** guidelines
- Ensure all tests pass

## Development Guide

Follow these guidelines for contributing to the project:

- Adhere to **PEP 8** for Python code style
- Run existing programs before submitting changes

## License

MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

- GitHub: [Bahar0900](https://github.com/Bahar0900)
- Email: `sagormdsagorchowdhury@gmail.com`

## Acknowledgments

- **Flask**: Lightweight web framework
- **Citus**: Distributed PostgreSQL extension
- **SQLAlchemy**: ORM for database interactions
- **Docker**: Containerization platform
