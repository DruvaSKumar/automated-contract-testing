#PHASE 0 – FOUNDATIONS ✅

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
- http://localhost:8080/users/1 → OK
- http://localhost:8080/swagger-ui.html → OK

Status:
- Provider API running locally
- OpenAPI spec available
- Ready for contract testing

NEXT:
- Phase 1 – Provider API polish & OpenAPI clarity

#PHASE 1 – Provider API polish ✅

Changes:
- Introduced DTO: UserDto (id, name, email)
- Added OpenAPI annotations (@Operation, @ApiResponse, @Schema)
- New endpoint: GET /users (list)
- Validation: @Min, @NotBlank, @Email

Verification:
- Swagger shows summaries, field descriptions, examples
- Schemas reflect constraints (min, email format)
- GET /users and GET /users/{id} both work

Repo:
- Commit pushed with Phase 1 changes

Next:
- Phase 2 – Manual Contract Testing with Spring Cloud Contract
  - Add dependencies & plugin
  - Write first manual contract
  - Run mvn test
  - Intentionally break API to see contract fail (learning milestone)
