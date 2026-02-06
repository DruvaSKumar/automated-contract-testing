package contracts.users

org.springframework.cloud.contract.spec.Contract.make {
    description "Invalid id (0) returns 400"

    request {
        method GET()
        urlPath("/users/0")
    }

    response {
        status BAD_REQUEST()
    }
}