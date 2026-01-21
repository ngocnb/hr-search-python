# Technical Assignment: Senior Backend Engineer

## Overview
The task is to write a simple **Django / FastAPI microservice** for an HR company. You are responsible for building the API that populates the **employee search directory**.

* **Database:** Feel free to create entities and their attributes as you like in a relational DB.
* **Scope:** * 💡 Only the **Search API** has to be implemented. 
    * 💡 Please ignore the Add employee / Import / Export CTA.
    * 💡 You are only required to implement the search API. You do not have to implement CRUD APIs for any of the entities.

---

## Filter Options & Logic

### Filter options
- Status: Active, Not started, Terminated
- Locations
- Companies
- Departments
- Positions

All options are multi selected.

### Dynamic Columns
Different organisations prefer different columns in the output. For example, one might display contact info, department, location, and position, while another displays only department, location, and position.
* **Configuration:** You can assume the column order and visibility are configurable at an organization level.
* **Storage:** 💡 You do not have to create a CRUD API to store the configuration. Assume it’s stored in a configuration of your choice (DB / file / etc).

### Performance
* Assume there are **millions of users** in the database.
* Design the API considering heavy load (e.g., indexing, sharding, etc.).

### Rate-Limiting
* We do not want users abusing the API. Create an appropriate rate-limiting system to prevent spamming.

---

## Requirements

### Functional Requirements
* **Language/Framework:** Python / FastAPI.
* **Containerization:** The service must be containerized.
* **Documentation:** API information must be shareable in an **OpenAPI** format.
* **Testing:** The API must be unit tested.
* **Rate-Limiting:** **No external library** is allowed for rate-limiting. Please use your own implementation, no matter how naive.
* **Security:** There shouldn’t be a data leak (e.g., info from other organisations, or extra attributes not displayed on the UI).
* **Migrations:** 💡 No need to create complex relations in migrations. Focus as much time on the API as possible.

### Non-Functional Requirements
* **Dependencies:** You may not use any external dependencies or libraries (only the **standard library** is allowed).
* **Testing Exception:** You may use external testing libraries if you choose.
* **Environment:** The application should execute correctly in a Linux (or UNIX-like) environment.

---

## Deliverables
Include the following in your submission:
1.  **GitHub Repository:** Link to your repository containing all code and toolings needed to install and run the tool.
2.  **README.md:** Documentation for an end-user (likely a fellow developer). Assume a Unix environment (Mac/Linux).

---

## Final Notes
If the submission is of sufficient quality, we will have a further discussion on code architecture and a pair-programming session to simulate real-world changes. **Do not copy and paste too much.**