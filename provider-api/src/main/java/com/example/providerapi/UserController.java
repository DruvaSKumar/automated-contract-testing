package com.example.providerapi;
// all REST endpoints for users (the provider we verify).
import com.example.providerapi.dto.UserDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import jakarta.validation.constraints.Min;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@Validated //  enable method-parameter validation
@RestController
@RequestMapping("/users")
public class UserController {

    // Simulated "database"
    private static final Map<Integer, UserDto> USERS = new HashMap<>();
    static {
        USERS.put(1, new UserDto(1, "John", "john@example.com"));
        USERS.put(2, new UserDto(2, "Jane", "jane@example.com"));
    }

    @Operation(
            summary = "Get user by ID",
            description = "Returns a single user resource for the given identifier",
            responses = {
                    @ApiResponse(
                            responseCode = "200",
                            description = "User found",
                            content = @Content(schema = @Schema(implementation = UserDto.class))
                    ),
                    @ApiResponse(responseCode = "400", description = "Invalid ID (must be >= 1)"),
                    @ApiResponse(responseCode = "404", description = "User not found")
            }
    )
    @GetMapping("/{id}")
    public ResponseEntity<?> getUser(
            @Parameter(description = "Numeric ID of the user to retrieve", example = "1")
            @PathVariable @Min(1) int id // 👈 validate path var: must be >= 1
    ) {
        UserDto user = USERS.get(id);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build(); // 404 with empty body
        }
        return ResponseEntity.ok(user); // 200 with UserDto
        //return ResponseEntity.ok(new UserDto(id, "John", null)); //TO TEST THE CONTRACT
    }

    @Operation(
            summary = "List all users",
            description = "Returns a list of users"
    )
    @GetMapping
    public ResponseEntity<List<UserDto>> listUsers() {
        return ResponseEntity.ok(new ArrayList<>(USERS.values()));
    }
}
