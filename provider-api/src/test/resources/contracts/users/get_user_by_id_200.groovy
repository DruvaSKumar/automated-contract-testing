package contracts.users

//the source of truth for provider expectations; SCC reads these to generate & run tests.

import org.springframework.cloud.contract.spec.Contract

Contract.make {
    description "Get user by ID returns 200 with a valid body"

    request {
        method GET()
        urlPath("/users/1")
    }

    response {
        status OK()
        headers {
            contentType(applicationJson())
        }
        // ✔ Body uses concrete example values
        body(
                id: 1,
                name: "John",
                email: "john@example.com"
        )
        // ✔ All variability is expressed via bodyMatchers
        bodyMatchers {
            jsonPath('$.id', byEquality())            // exactly 1
            jsonPath('$.name', byType())              // any string
            jsonPath('$.email', byRegex(/^[^\s@]+@[^\s@]+\.[^\s@]+$/))
        }
    }
}