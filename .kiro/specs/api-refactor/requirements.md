# Requirements Document

## Introduction

This document captures the requirements for refactoring the Flask Data Analysis API. The goal is to fix four known bugs, eliminate dead code, improve readability by adopting Python naming conventions, consolidate data loading with a module-level cache, and complete the Swagger documentation — all while preserving the existing file and folder structure and keeping every endpoint working correctly.

## Glossary

- **API**: The Flask Data Analysis API application described in this document.
- **ServiceFunctions**: The class in `ServiceFunctions.py` that provides static data-access methods consumed by route modules.
- **DataLoader**: The module-level caching layer (a dict keyed by file path) that replaces per-call file reads in `ServiceFunctions.py`.
- **DatasetConfig**: The `DatasetConfig` class in `configs/dataset_config.py` that resolves absolute paths to data files.
- **Blueprint**: A Flask `Blueprint` object that groups related route handlers.
- **Swagger**: The Flasgger-powered interactive API documentation served at `/apidocs/`.
- **snake_case**: Python naming convention where words are separated by underscores (e.g., `get_head_data_info`).
- **camelCase**: Mixed-case naming convention currently used in the codebase (e.g., `getHeadDataInfo`), which must be replaced.
- **Dead code**: Code that is syntactically present but can never be executed (e.g., statements after a `return` with no route decorator).

---

## Requirements

### Requirement 1: Bug Fix — Dead `/api/info` Endpoint

**User Story:** As a developer, I want the `/api/info` endpoint to be reachable, so that I can inspect available routes and API metadata without reading source code.

#### Acceptance Criteria

1. WHEN a client sends `GET /api/info`, THE API SHALL return a JSON response containing the API name, description, version, and a list of available endpoint groups.
2. THE `general_routes` Blueprint SHALL register the `/api/info` route with a `@general_bp.route` decorator so the handler is reachable.
3. THE `general_routes` module SHALL contain no unreachable code blocks (no statements placed after a `return` statement outside of a function body).

---

### Requirement 2: Bug Fix — Athlete HTML Routes Missing Argument

**User Story:** As a user, I want the athlete HTML pages to load without a server error, so that I can view athlete data in a browser.

#### Acceptance Criteria

1. WHEN a client requests `GET /athletesInfoHead`, THE API SHALL render the `athletesInfo.html` template populated with the first 10 athlete records.
2. WHEN a client requests `GET /athletesInfoTail`, THE API SHALL render the `athletesInfo.html` template populated with the last 10 athlete records.
3. THE `athlete_routes` module SHALL call `get_athletes_info_from_the_head` and `get_athletes_info_from_the_tail` with the integer argument `10` so that no `TypeError` is raised at runtime.

---

### Requirement 3: Bug Fix — Missing `getCsvDataSetInfoForFirstTenRecords` Method

**User Story:** As a user, I want the student HTML page to load without a server error, so that I can view student performance data in a browser.

#### Acceptance Criteria

1. WHEN a client requests `GET /studentsInfo`, THE API SHALL render the `studentInfo.html` template populated with the first 10 student records.
2. THE `student_routes` module SHALL NOT call any method on `ServiceFunctions` that does not exist; the helper function `get_student_data_set` SHALL use `DataLoader` or a valid `ServiceFunctions` method to retrieve the first 10 records.
3. IF the student dataset file cannot be read, THEN THE API SHALL render the `studentInfo.html` template with an empty table and log the error.

---

### Requirement 4: Bug Fix — Discarded `head`/`tail` Result in ServiceFunctions

**User Story:** As a developer, I want `get_head_data_info` and `get_tail_data_info` to return the correct sliced records, so that callers receive the expected subset of data.

#### Acceptance Criteria

1. WHEN `get_head_data_info(dataset_path, n)` is called, THE `ServiceFunctions` class SHALL return a JSON response containing only the first `n` rows of the dataset at `dataset_path`.
2. WHEN `get_tail_data_info(dataset_path, n)` is called, THE `ServiceFunctions` class SHALL return a JSON response containing only the last `n` rows of the dataset at `dataset_path`.
3. THE `ServiceFunctions` class SHALL assign the result of `data.head(n)` and `data.tail(n)` to a variable before serialising it, so that the full unsliced dataset is never returned in place of the slice.

---

### Requirement 5: Data Loading Cache

**User Story:** As a developer, I want each dataset file to be read from disk only once per process lifetime, so that repeated API calls do not incur unnecessary I/O overhead.

#### Acceptance Criteria

1. THE `DataLoader` SHALL maintain a module-level dictionary keyed by absolute file path whose values are the corresponding loaded `pandas.DataFrame` objects.
2. WHEN `DataLoader` is asked to load a path that is already in the cache, THE `DataLoader` SHALL return the cached `DataFrame` without reading the file again.
3. WHEN `DataLoader` is asked to load a path that is not yet in the cache, THE `DataLoader` SHALL read the file, store the result in the cache, and return the `DataFrame`.
4. THE `DataLoader` SHALL support both `.csv` and `.xlsx`/`.xls` file extensions, raising a `ValueError` for any other extension.
5. IF a file cannot be read (e.g., path does not exist), THEN THE `DataLoader` SHALL raise the underlying exception so callers can handle it appropriately.

---

### Requirement 6: Remove Unused Imports

**User Story:** As a developer, I want `ServiceFunctions.py` to import only the libraries it actually uses, so that the module loads faster and its dependencies are clear.

#### Acceptance Criteria

1. THE `ServiceFunctions` module SHALL NOT import `seaborn`, `matplotlib`, `plotly`, or `numpy` at module level.
2. THE `requirements.txt` file SHALL retain `seaborn`, `matplotlib`, `plotly`, and `numpy` only if they are used elsewhere in the project; otherwise THE project SHALL remove them from `requirements.txt`.
3. THE `ServiceFunctions` module SHALL import `pandas` and `os` (and any other libraries it genuinely uses).

---

### Requirement 7: Rename Functions to snake_case

**User Story:** As a developer, I want all function and method names to follow PEP 8 snake_case conventions, so that the codebase is consistent and idiomatic Python.

#### Acceptance Criteria

1. THE `ServiceFunctions` class SHALL rename all camelCase static methods to snake_case equivalents (e.g., `getHeadDataInfo` → `get_head_data_info`).
2. THE module-level helper functions in `ServiceFunctions.py` (`getCSVData`, `getExcelData`, `getData`) SHALL be renamed to `get_csv_data`, `get_excel_data`, and `get_data` respectively.
3. WHEN any route module imports or calls a renamed function or method, THE route module SHALL use the new snake_case name so that no `AttributeError` or `ImportError` is introduced.
4. THE route-level helper functions in `athlete_routes.py`, `student_routes.py`, and `dataset_routes.py` SHALL also be renamed to snake_case (e.g., `getAthletesInfoFromTheHead` → `get_athletes_info_from_the_head`).

---

### Requirement 8: Health Endpoint

**User Story:** As an operator, I want a `GET /api/health` endpoint, so that I can verify the API is running and check its uptime without inspecting logs.

#### Acceptance Criteria

1. WHEN a client sends `GET /api/health`, THE API SHALL return HTTP 200 with a JSON body containing at minimum the fields `status` (string `"ok"`) and `timestamp` (ISO 8601 UTC datetime string).
2. THE `/api/health` endpoint SHALL be registered in `general_routes.py` with a `@general_bp.route` decorator.
3. IF an unexpected error occurs while building the health response, THEN THE API SHALL return HTTP 500 with a JSON body containing an `error` field.

---

### Requirement 9: Dataset Query Parameter for Generic Endpoints

**User Story:** As a developer, I want the generic dataset exploration endpoints to accept a `dataset` query parameter, so that I can inspect any configured dataset without separate hardcoded routes.

#### Acceptance Criteria

1. WHEN a client calls any of `GET /api/dataset/shape`, `/api/dataset/columns`, `/api/dataset/sample`, or `/api/dataset/paginated` without a `dataset` query parameter, THE API SHALL default to the athletes dataset.
2. WHEN a client calls those endpoints with `?dataset=<name>` where `<name>` is a key recognised by `DatasetConfig.get_dataset_path`, THE API SHALL load and operate on the specified dataset.
3. IF the `dataset` query parameter value is not recognised by `DatasetConfig`, THEN THE API SHALL return HTTP 400 with a JSON body containing an `error` field describing the valid dataset names.
4. THE endpoints `GET /api/dataset/unique-values/<columnName>` and `GET /api/dataset/column-counts/<columnName>` SHALL also accept an optional `dataset` query parameter with the same defaulting and validation behaviour.

---

### Requirement 10: Complete and Accurate Swagger Documentation

**User Story:** As a developer, I want every endpoint to have accurate and complete Swagger docstrings, so that the `/apidocs/` UI reflects the real API contract.

#### Acceptance Criteria

1. THE `ServiceFunctions` module SHALL document every public method with a docstring describing its parameters and return value.
2. EVERY route handler in `general_routes.py`, `athlete_routes.py`, `student_routes.py`, and `dataset_routes.py` SHALL have a Flasgger-compatible YAML docstring that accurately describes its HTTP method, path parameters, query parameters, request body (if any), and all possible response codes and schemas.
3. THE Swagger docstring for `GET /api/dataset/shape`, `/api/dataset/columns`, `/api/dataset/sample`, `/api/dataset/paginated`, `/api/dataset/unique-values/<columnName>`, and `/api/dataset/column-counts/<columnName>` SHALL document the `dataset` query parameter added in Requirement 9.
4. THE Swagger docstring for `GET /api/health` SHALL document the `status` and `timestamp` response fields.
5. THE Swagger docstring for `GET /api/info` SHALL document all response fields including the endpoint groups list.
6. WHERE a route can return an error response, THE Swagger docstring SHALL include the corresponding error response code (400, 404, or 500) and schema.

---

### Requirement 11: Preserve Existing File and Folder Structure

**User Story:** As a developer, I want the refactor to stay within the existing file layout, so that deployment scripts and import paths do not need to change.

#### Acceptance Criteria

1. THE refactored codebase SHALL retain the files `app.py`, `ServiceFunctions.py`, `apis/routes.py`, `apis/general_routes.py`, `apis/athlete_routes.py`, `apis/student_routes.py`, `apis/dataset_routes.py`, `configs/dataset_config.py`, and `configs/swagger_config.py` at their current paths.
2. THE refactor SHALL NOT introduce new packages, sub-packages, or top-level modules beyond those already present.
3. THE `app.py` application factory SHALL continue to register blueprints via `register_blueprints` and initialise Swagger via `Flasgger`.

---

### Requirement 12: All Existing Endpoints Remain Functional

**User Story:** As a user, I want every endpoint that existed before the refactor to continue working correctly after it, so that no existing integrations break.

#### Acceptance Criteria

1. THE following endpoints SHALL return HTTP 200 with valid responses after the refactor: `GET /`, `GET /api/hello`, `GET /studentsInfo`, `GET /athletesInfoHead`, `GET /athletesInfoTail`, `GET /api/students/head`, `GET /api/students/all`, `GET /api/athletes/head/<n>`, `GET /api/athletes/tail/<n>`, `GET /api/athletes/all`, `GET /api/dataset/shape`, `GET /api/dataset/unique-values/<columnName>`, `GET /api/dataset/column-counts/<columnName>`, `GET /api/dataset/columns`, `GET /api/dataset/sample`, `GET /api/dataset/paginated`, and `GET /api/dataset/config`.
2. WHEN the Flask application starts, THE API SHALL not raise any `ImportError`, `AttributeError`, or `NameError` caused by the renaming or removal of functions.
3. THE HTML template endpoints SHALL continue to pass data to their respective Jinja2 templates using the same template variable names (`table_data`) so that the templates do not require modification.
