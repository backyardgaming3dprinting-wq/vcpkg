cmake_minimum_required(VERSION 3.15)
project(mesh_core_tests)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the test executable
add_executable(mesh_core_tests
    src/mesh_core/mesh_core_tests.cpp
)

target_include_directories(mesh_core_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/mesh_core
)

# Enable testing
enable_testing()
add_test(NAME mesh_core_tests COMMAND mesh_core_tests)
