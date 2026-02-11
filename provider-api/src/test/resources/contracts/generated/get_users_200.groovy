org.springframework.cloud.contract.spec.Contract.make {
  description "GET /users (auto-generated)"

  request {
    method GET()
    urlPath("/users")
  }

  response {
    status OK()
    headers { contentType(applicationJson()) }
  }
}
