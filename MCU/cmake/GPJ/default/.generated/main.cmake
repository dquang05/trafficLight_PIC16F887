include("${CMAKE_CURRENT_LIST_DIR}/rule.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/file.cmake")

set(GPJ_default_library_list )

# Handle files with suffix (s|as|asm|AS|ASM|As|aS|Asm), for group default-XC8
if(GPJ_default_default_XC8_FILE_TYPE_assemble)
add_library(GPJ_default_default_XC8_assemble OBJECT ${GPJ_default_default_XC8_FILE_TYPE_assemble})
    GPJ_default_default_XC8_assemble_rule(GPJ_default_default_XC8_assemble)
    list(APPEND GPJ_default_library_list "$<TARGET_OBJECTS:GPJ_default_default_XC8_assemble>")

endif()

# Handle files with suffix S, for group default-XC8
if(GPJ_default_default_XC8_FILE_TYPE_assemblePreprocess)
add_library(GPJ_default_default_XC8_assemblePreprocess OBJECT ${GPJ_default_default_XC8_FILE_TYPE_assemblePreprocess})
    GPJ_default_default_XC8_assemblePreprocess_rule(GPJ_default_default_XC8_assemblePreprocess)
    list(APPEND GPJ_default_library_list "$<TARGET_OBJECTS:GPJ_default_default_XC8_assemblePreprocess>")

endif()

# Handle files with suffix [cC], for group default-XC8
if(GPJ_default_default_XC8_FILE_TYPE_compile)
add_library(GPJ_default_default_XC8_compile OBJECT ${GPJ_default_default_XC8_FILE_TYPE_compile})
    GPJ_default_default_XC8_compile_rule(GPJ_default_default_XC8_compile)
    list(APPEND GPJ_default_library_list "$<TARGET_OBJECTS:GPJ_default_default_XC8_compile>")

endif()


# Main target for this project
add_executable(GPJ_default_image_M3cVlAgt ${GPJ_default_library_list})

set_target_properties(GPJ_default_image_M3cVlAgt PROPERTIES
    OUTPUT_NAME "default"
    SUFFIX ".elf"
    ADDITIONAL_CLEAN_FILES "${output_extensions}"
    RUNTIME_OUTPUT_DIRECTORY "${GPJ_default_output_dir}")
target_link_libraries(GPJ_default_image_M3cVlAgt PRIVATE ${GPJ_default_default_XC8_FILE_TYPE_link})

# Add the link options from the rule file.
GPJ_default_link_rule( GPJ_default_image_M3cVlAgt)


