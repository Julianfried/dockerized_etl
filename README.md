## ETL Pipeline Automation

This project includes an automated triggering mechanism that starts the ETL pipeline when the Docker environment is healthy:

1. When the containers start up, the system performs health checks on all components
2. Once the webserver and scheduler are healthy, a special health check DAG runs automatically
3. This health check DAG verifies:
   - PostgreSQL database connection
   - Table existence and data
   - Airflow connections
   - Filesystem access
   - System resources
4. After all checks pass, it automatically triggers the ETL pipeline

This ensures that your data pipeline only runs when the entire environment is properly set up and healthy.

### How the Automation Works

The automatic triggering system consists of:

1. **Health Check DAG**: Runs system checks and triggers the ETL pipeline
2. **Startup Script**: Unpauses and triggers the health check DAG
3. **Container Health Checks**: Ensures all components are ready
4. **Modified Entrypoint**: Runs the startup process at the right time

### Manually Triggering the Pipeline

If you need to manually trigger the ETL pipeline:

```bash
docker-compose exec airflow-scheduler airflow dags trigger pandas_etl_pipeline
```

You can also trigger it through the Airflow UI.# TestFligoo Data Pipeline

A complete data engineering solution featuring Apache Airflow, PostgreSQL, Pandas, and Great Expectations.

## Overview

This project implements a containerized data pipeline with the following components:

- **Apache Airflow**: Workflow orchestration platform
- **PostgreSQL**: Database for storing both application and pipeline data
- **Pandas**: Data manipulation and analysis library
- **Great Expectations**: Data validation framework
- **Poetry**: Dependency management

The solution automatically creates the required `testfligoo` database and `testdata` table when the containers are started.

## Prerequisites

- Docker and Docker Compose
- Git

## Project Structure

```
dockerized_etl/
├── dags/                   # Airflow DAG definitions
│   └── etl.py              # Sample DAG for data processing
├── data/                   # Data directory for pipeline artifacts
├── init-scripts/           # Database initialization scripts
│   └── 01-init-db.sql      # Creates testfligoo database and testdata table
├── notebooks/              # Jupyter Notebooks directory
├── logs/                   # Airflow logs directory
├── plugins/                # Airflow plugins directory
├── scripts/                # Utility scripts
│   └── entrypoint.sh       # Container entrypoint script
├── .gitignore              # Git ignore file
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── poetry.lock             # Poetry lock file (dependencies)
├── pyproject.toml          # Poetry project configuration
└── README.md               # This file
```

## Getting Started

### 1. Clone the Repository

```
git clone <repository-url>
cd dockerized_etl
```

### 2. Create Required Directories

```
mkdir -p dags logs plugins data
```

### 3. Enviroment Variables

Based on the .env.example file, create a .env in the root folder adding you AVIATION_STACK_API_KEY

### 4. Build and start the Services

```
docker build .

docker-compose up -d
```

This will:
- Build the Docker image with all dependencies
- Start PostgreSQL database
- Initialize the `testdata` table (for health check)  and  `testfligoo` database
- Start Airflow webserver and scheduler
- Initialize Airflow with an admin user

### 5. Access the Airflow Web UI

Open your browser and navigate to:

```
http://localhost:8080
```

Login with the default credentials:
- Username: `admin`
- Password: `admin`

### 6. Activate and Run the DAG

In the Airflow UI:
1. Navigate to DAGs
2. Find the "testfligoo_pipeline" DAG
3. Activate the DAG by toggling the switch
4. Trigger the DAG by clicking the "Play" button

## Data Pipeline

The included sample DAG (`etl.py`) demonstrates a complete ETL (Extract, Transform, Load) process with data quality validation:

1. **Extract**: Retrieves data from the aviation API
2. **Transform**: Performs data transformations using Pandas
3. **Validate**: Validates the transformed data using Great Expectations
4. **Load**: Loads the transformed data back to PostgreSQL in a table

## The ETL DAG Structure

1. **extract.py**: Handles data extraction from PostgreSQL
2. **transform.py**: Processes the data with pandas operations
3. **data_quality.py**: Performs checks on the data
4. **load.py**: Loads the data back to PostgreSQL
5. **etl.py**: Main DAG file that orchestrates the whole process

## Connecting to the Database

The PostgreSQL database is exposed on port 5432 and the server is already loaded in pgadmin4. You can login:
```
http://localhost:5050/

Database: testfligoo
Username: airflow
MasterPassword: airflow
Password: airflow
```

Using you prefered RDBMS, you can connect manually to it using:

```
Host: localhost
Port: 5432
Database: testfligoo
Username: airflow
Password: airflow
```
## Jupyter Notebook

You can run the flight_data_analysis.ipynb notebook for data exploring.

## Customizing the Pipeline

### Adding Dependencies

To add new Python dependencies:

1. Add them to `pyproject.toml` using Poetry:
   ```
   docker-compose exec airflow-webserver poetry add <package-name>
   ```
2. Rebuild the Docker image:
   ```
   docker-compose build
   docker-compose up -d
   ```
## Development

### Adding Custom Operators

Place custom Airflow operators in the `plugins/` directory.

### Code Quality and Linting

This project includes several linting tools to maintain code quality:

1. **Setup the linting environment**:
   ```
   # Install dependencies (including dev dependencies for linting)
   poetry install
   ```

2. **Available linting commands**:
   ```
   # Run all linters at once
   poetry run black dags/ plugins/ --check
   poetry run isort dags/ plugins/ --check --profile black
   poetry run flake8 dags/ plugins/
   poetry run pylint dags/ plugins/
   poetry run mypy dags/ plugins/

   # Format code automatically
   poetry run black dags/ plugins/
   poetry run isort dags/ plugins/ --profile black

   # Run type checking
   poetry run mypy dags/ plugins/

   #Or run all of them using pre-commit
   # Run on a specific Python file
   poetry run pre-commit run --files dags/etl.py

3. **Individual linting tools**:
   - **Black**: Code formatter (maintains consistent style)
   - **isort**: Sorts imports systematically
   - **flake8**: Style guide enforcement
   - **pylint**: Code analysis for bugs and quality issues
   - **mypy**: Static type checking

4. **VS Code Integration**:
   If you're using VS Code, the included `.vscode/settings.json` configures the editor to:
   - Show linting errors in real-time
   - Format code on save
   - Organize imports automatically
5. **For Docker environments, build with linting support**:

    ```
    docker-compose build --build-arg DEV_MODE=true
    ```

## Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Great Expectations Documentation](https://docs.greatexpectations.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Poetry Documentation](https://python-poetry.org/docs/)


