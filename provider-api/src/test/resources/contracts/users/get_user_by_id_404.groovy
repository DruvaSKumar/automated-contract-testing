package contracts.users

org.springframework.cloud.contract.spec.Contract.make {
    description "Get user by ID that does not exist returns 404"

    request {
        method GET()
        urlPath("/users/999")
    }

    response {
        status NOT_FOUND()
    }
}