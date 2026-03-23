# user.cmake - custom additions for MPLAB Extension CMake layout

get_filename_component(GPJ_ROOT "${CMAKE_SOURCE_DIR}/../../.." ABSOLUTE)

# Add sources to the XC8 compile object library (C files)
set(GPJ_COMPILE_TARGET GPJ_default_default_XC8_compile)

# Include paths for headers
target_include_directories(${GPJ_COMPILE_TARGET} PRIVATE
    ${GPJ_ROOT}/apps
    ${GPJ_ROOT}/drivers
    ${GPJ_ROOT}/bsp
)

target_compile_options(${GPJ_COMPILE_TARGET} PRIVATE
    -I${GPJ_ROOT}/apps
    -I${GPJ_ROOT}/drivers
    -I${GPJ_ROOT}/bsp
)


# Source files (edit/add lines here to match your real filenames)
target_sources(${GPJ_COMPILE_TARGET} PRIVATE
    ${GPJ_ROOT}/apps/traffic.c
    ${GPJ_ROOT}/drivers/uart.c
    ${GPJ_ROOT}/drivers/i2c.c
    ${GPJ_ROOT}/drivers/lcd.c
    #${GPJ_ROOT}/bsp/pic16f887_bsp.c
)

target_compile_definitions(${GPJ_COMPILE_TARGET} PRIVATE _XTAL_FREQ=4000000UL)

