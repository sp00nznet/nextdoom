cmake_minimum_required(VERSION 3.20)
project(nextdoom_recomp C)

# The lifted code models a 32-bit guest in portable C; the host is x64 and the
# guest address space is one reservation offset by g_mem_base (ns_core.c).
if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
  message(FATAL_ERROR "Configure for x64.")
endif()
set(CMAKE_C_STANDARD 11)

set(PCRECOMP "${CMAKE_SOURCE_DIR}/../pcrecomp" CACHE PATH "pcrecomp checkout")
if(NOT EXISTS "${PCRECOMP}/runtime/nextstep/ns_runtime.h")
  message(FATAL_ERROR "pcrecomp not found at ${PCRECOMP} -- clone https://github.com/sp00nznet/pcrecomp next to this repo or pass -DPCRECOMP=<path>.")
endif()

file(GLOB GEN_SOURCES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/src/recomp/gen/*.c")
if(NOT GEN_SOURCES)
  message(FATAL_ERROR "src/recomp/gen is empty -- run: py -3 run_lift.py")
endif()

find_package(SDL2 REQUIRED CONFIG)

add_executable(nextdoom
  ${GEN_SOURCES}
  src/main.c
  "${PCRECOMP}/runtime/nextstep/ns_core.c"
  "${PCRECOMP}/runtime/nextstep/ns_libc.c"
  "${PCRECOMP}/runtime/nextstep/ns_objc.c"
  "${PCRECOMP}/runtime/nextstep/ns_appkit.c"
)
target_include_directories(nextdoom PRIVATE
  "${PCRECOMP}/runtime/recomp32"
  "${PCRECOMP}/runtime/nextstep"
  src/recomp/gen
)
target_compile_definitions(nextdoom PRIVATE NEXTDOOM_ROOT="${CMAKE_SOURCE_DIR}/original")
# -foptimize-sibling-calls is load-bearing: a guest loop split across two lifted
# functions tail-calls itself, which is unbounded recursion until it is a jump.
target_compile_options(nextdoom PRIVATE -O2 -foptimize-sibling-calls -fno-strict-aliasing -w)
target_link_libraries(nextdoom PRIVATE SDL2::SDL2 m)
