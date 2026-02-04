package com.example.providerapi;

import com.example.providerapi.dto.UserDto;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/users")
public class UserController {

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable int id) {
        UserDto user = new UserDto(
                id,
                "John",
                "john@example.com"
        );
        return ResponseEntity.ok(user);
    }
}