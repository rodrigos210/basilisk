# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.8

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/local/Cellar/cmake/3.8.2/bin/cmake

# The command to remove a file.
RM = /usr/local/Cellar/cmake/3.8.2/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Users/nbellowe/Programming/Basilisk

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Users/nbellowe/Programming/Basilisk

# Include any dependencies generated for this target.
include FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/depend.make

# Include the progress variables for this target.
include FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/progress.make

# Include the compile flags for this target's objects.
include FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/flags.make

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o: FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/flags.make
FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o: FswAlgorithms/messaging/static_messaging.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/Users/nbellowe/Programming/Basilisk/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o"
	cd /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging && /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o -c /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging/static_messaging.cpp

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.i"
	cd /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging && /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging/static_messaging.cpp > CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.i

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.s"
	cd /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging && /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging/static_messaging.cpp -o CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.s

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o.requires:

.PHONY : FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o.requires

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o.provides: FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o.requires
	$(MAKE) -f FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/build.make FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o.provides.build
.PHONY : FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o.provides

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o.provides.build: FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o


# Object files for target AlgorithmMessaging
AlgorithmMessaging_OBJECTS = \
"CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o"

# External object files for target AlgorithmMessaging
AlgorithmMessaging_EXTERNAL_OBJECTS =

modules/libAlgorithmMessaging.a: FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o
modules/libAlgorithmMessaging.a: FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/build.make
modules/libAlgorithmMessaging.a: FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/Users/nbellowe/Programming/Basilisk/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX static library ../../modules/libAlgorithmMessaging.a"
	cd /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging && $(CMAKE_COMMAND) -P CMakeFiles/AlgorithmMessaging.dir/cmake_clean_target.cmake
	cd /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/AlgorithmMessaging.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/build: modules/libAlgorithmMessaging.a

.PHONY : FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/build

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/requires: FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/static_messaging.cpp.o.requires

.PHONY : FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/requires

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/clean:
	cd /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging && $(CMAKE_COMMAND) -P CMakeFiles/AlgorithmMessaging.dir/cmake_clean.cmake
.PHONY : FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/clean

FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/depend:
	cd /Users/nbellowe/Programming/Basilisk && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/nbellowe/Programming/Basilisk /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging /Users/nbellowe/Programming/Basilisk /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging /Users/nbellowe/Programming/Basilisk/FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : FswAlgorithms/messaging/CMakeFiles/AlgorithmMessaging.dir/depend

