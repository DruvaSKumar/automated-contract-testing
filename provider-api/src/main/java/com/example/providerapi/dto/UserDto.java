package com.example.providerapi.dto;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;



@Schema(name = "UserDto", description = "User representation returned by the API")
public class UserDto {

    @Min(value = 1, message = "id must be >= 1")
    @Schema(description = "Unique identifier of the user", example = "1", minimum = "1")
    private int id;

    @NotBlank(message = "name is required")
    @Schema(description = "Full name of the user", example = "John")
    private String name;

    @Email(message = "email must be valid")
    @Schema(description = "Primary email address", example = "john@example.com", format = "email")
    private String email;

    public UserDto() {}
    public UserDto(int id, String name, String email) { this.id = id; this.name = name; this.email = email; }


    // getters and setters...
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
}