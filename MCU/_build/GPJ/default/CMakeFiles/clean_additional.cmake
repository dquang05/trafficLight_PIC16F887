# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "")
  file(REMOVE_RECURSE
  "D:\\Hardware\\MPLab\\GPJ\\out\\GPJ\\default.cmf"
  "D:\\Hardware\\MPLab\\GPJ\\out\\GPJ\\default.hex"
  "D:\\Hardware\\MPLab\\GPJ\\out\\GPJ\\default.hxl"
  "D:\\Hardware\\MPLab\\GPJ\\out\\GPJ\\default.mum"
  "D:\\Hardware\\MPLab\\GPJ\\out\\GPJ\\default.o"
  "D:\\Hardware\\MPLab\\GPJ\\out\\GPJ\\default.sdb"
  "D:\\Hardware\\MPLab\\GPJ\\out\\GPJ\\default.sym"
  )
endif()
