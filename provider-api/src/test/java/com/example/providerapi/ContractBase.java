package com.example.providerapi;

//wires WebMvcTest + MockMvc + RestAssuredMockMvc so SCC’s generated tests can execute requests without full app startup.

import io.restassured.module.mockmvc.RestAssuredMockMvc;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(UserController.class)
@ComponentScan(basePackages = "com.example.providerapi")
public abstract class ContractBase {

    @Autowired
    protected MockMvc mockMvc;

    @BeforeEach
    void setup() {
        RestAssuredMockMvc.mockMvc(mockMvc);
    }
}