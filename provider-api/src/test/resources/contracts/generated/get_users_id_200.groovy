org.springframework.cloud.contract.spec.Contract.make {
  description "GET /users/{id} (auto-generated)"

  request {
    method GET()
    urlPath("/users/1")
  }

  response {
    status OK()
    headers { contentType(applicationJson()) }
  }
}
