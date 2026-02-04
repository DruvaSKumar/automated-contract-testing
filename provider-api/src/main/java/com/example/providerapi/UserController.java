package com.example.providerapi;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/users")
public class UserController {

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getUser(@PathVariable int id) {
        Map<String, Object> user = new HashMap<>();
        user.put("id", id);
        user.put("name", "John");
        user.put("email", "john@example.com");
        return ResponseEntity.ok(user);
    }
}
