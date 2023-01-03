if(BUILD_OPNAV)
  include(usingOpenCV)

  if(APPLE)
    link_libraries("-march=haswell -mno-lzcnt")
  endif()

else()
  message("SKIPPED: ${TARGET_NAME}")
  set(CUSTOM_DEPENDENCIES_HANDLED 1)
endif()
