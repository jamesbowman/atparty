
FILE(GLOB SRCS *.cpp)
FILE(GLOB HDRS *.h)

ADD_EXECUTABLE(gdatparty
	${SRCS}
	${HDRS}
	)

target_link_libraries(gdatparty
	libgdemu
	)
