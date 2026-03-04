# **PHASE 0 – FOUNDATIONS ✅**

Environment:
- OS: Windows (local only)
- Java: 25 LTS
- Maven: 3.9.12
- Git: Installed and verified
- IDE: IntelliJ IDEA

What was built:
- Spring Boot 3.5.10 application (provider-api)
- REST endpoint: GET /users/{id}
- Swagger/OpenAPI via springdoc-openapi

Verification:
-run: mvn spring-boot:run
- http://localhost:8080/users/1 → OK
- http://localhost:8080/swagger-ui.html → OK

Status:
- Provider API running locally
- OpenAPI spec available
- Ready for contract testing


# **PHASE 1 – Provider API polish ✅**

Changes:
- Introduced DTO: UserDto (id, name, email)
- Added OpenAPI annotations (@Operation, @ApiResponse, @Schema)
- New endpoint: GET /users (list)
- Validation: @Min, @NotBlank, @Email

Verification:
- Swagger shows summaries, field descriptions, examples
- Schemas reflect constraints (min, email format)
- GET /users and GET /users/{id} both work

  - Intentionally break API to see contract fail (learning milestone)

# **Phase 2 – Manual Contract Testing with Spring Cloud Contract**

## 1) Executive Summary

We have a working **Spring Boot provider API** with **Swagger/OpenAPI** and **validation**, plus **provider‑side contract tests** using **Spring Cloud Contract**. The contracts verify behavior for **200 / 400 / 404** scenarios and **fail predictably** when we introduce breaking changes (e.g., remove `email` or change HTTP status). This establishes a strong, CI‑friendly safety net for future changes and prepares the ground for **Phase 3 (auto‑generate contracts from OpenAPI)** and the **AI layer**.

---

## 2) What We Built (Outcomes)

- **Contract Testing (Provider‑side)**:
    - Spring Cloud Contract (SCC 5.0.2) configured with a **base test** (`ContractBase`) using `@WebMvcTest` + `MockMvc` + **RestAssuredMockMvc binding**.
    - **Groovy DSL contracts** for the happy path (200), invalid id (400), and not found (404).
    - Verified the safety net: **tests fail** when we remove `email` or change status to `201`, and go **green** again on revert.

# **PHASE 3 — Automate Contract Generation (Week 3)**

**Goal**

Remove manual contract writing.

**Steps**

1. Extract **OpenAPI spec** (openapi.json)
2. Build an **AI agent (script)**
    - Inputs:
        - OpenAPI spec
    - Output:
        - Contract files
3. Agent logic:
    - Parse endpoints
    - For each endpoint:
        - Create request/response contract
        - Include required fields, status codes
4. Generate contracts automatically

**Tools**

- Java / Python script
- AI API or Copilot-assisted logic

**Success Criteria**

✅ Contracts are auto-generated

✅ No manual contract writing needed

## What the script does (big picture)

1. **Fetches your live OpenAPI spec**
    
    It calls `http://localhost:8080/v3/api-docs` (provided by springdoc) to read the **current** API description of your running provider.
    
2. **Iterates over every path & operation**
    
    For each HTTP method under each path (e.g., `GET /users`, `GET /users/{id}`), it looks for a **successful JSON response** (prefers 200; falls back to 201 if present).
    
3. **Synthesizes a realistic response body + matchers**
    - If the schema (e.g., `UserDto`) has `example` values, it uses them.
    - Otherwise it builds a **concrete example** based on the field types (e.g., `email` → `"john@example.com"`, `integer` → `1`, etc.).
    - It then attaches **`bodyMatchers`** to enforce correctness without overfitting:
        - **type matchers** for numbers/booleans/objects/arrays/strings,
        - a **regex matcher** for `format: email` fields.
    
    This combination is intentional: we keep the **body** human-friendly and the **rules** in `bodyMatchers`—the same approach you adopted for manual contracts.
    
4. **Resolves path variables to examples**
    
    For a URL like `/users/{id}`, it finds parameter examples (or falls back to smart defaults like `1`), and emits a contract that hits a **concrete path** (e.g., `/users/1`).
    
5. **Writes one Groovy contract per operation**
    
    Files are created in:
    
    ```
    src/test/resources/contracts/generated/
      get_users_id_200.groovy
      get_users_200.groovy
    ```
    
    The filenames encode the method, path, and success code (e.g., `_200`).
    
6. **Leaves manual contracts untouched**
    
    Generated contracts live in `contracts/generated/` to keep them separate from your **manual** contracts. You can keep both—in practice, the generator covers the basics while manual contracts capture edge cases or special behaviors.
    

---

### INTER PHASE: MAKE IT EASY

```jsx
mvn -Pcontracts verify
```

- **Boot start/stop in the IT window**
You start the app in **`pre-integration-test`** and stop it in **`post-integration-test`** with `spring-boot-maven-plugin`. That’s the documented pattern used together with documentation generation at build time.

- **Run the Python generator while the app is up**
You call your script in **`integration-test`** using `exec-maven-plugin` and point it at `OPENAPI_URL=http://localhost:8080/v3/api-docs`. Invoking Python via `exec-maven-plugin` with `executable=python` + `workingDirectory=${project.basedir}` is the standard, cross‑platform approach.

- **Execute tests after generation**
You explicitly trigger **Surefire’s** `test` goal **again** in the **`integration-test`** phase. That ensures the contracts generated in IT are present before tests run. (By default, Surefire runs in `test` phase; calling it again in IT is a common workaround when you generate test inputs later in the lifecycle.)

- **IDE visibility for SCC generated tests**
The `build-helper-maven-plugin` adds the SCC generated test‑sources folder to the test classpath (good for IntelliJ). This is suggested in Spring Cloud Contract docs so IDEs “see” generated tests.
