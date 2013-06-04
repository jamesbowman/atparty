
FILE(GLOB SRCS *.cpp)
FILE(GLOB HDRS *.h)

ADD_EXECUTABLE(gdatparty
	${SRCS}
	${HDRS}
	)

set_property( TARGET gdatparty PROPERTY COMPILE_DEFINITIONS EMULATED )

target_link_libraries(gdatparty
	libgdemu
	)
