
##- project(BRAINSMush)

#-----------------------------------------------------------------------------
# Dependencies.
#

#
# ITK
#

FindITKUtil(BRAINSMush_ITK
  ITKBinaryMathematicalMorphology
  ITKCommon
  ITKConnectedComponents
  ITKIOImageBase
  ITKImageStatistics
  ITKMathematicalMorphology
  ITKOptimizers
  ITKRegionGrowing
  ITKThresholding)

#-----------------------------------------------------------------------------
# Output directories.
#

set(ALL_PROGS_LIST
  BRAINSMush
  )
foreach(prog ${ALL_PROGS_LIST})
  StandardBRAINSBuildMacro(NAME ${prog} TARGET_LIBRARIES BRAINSCommonLib )
endforeach()

if(0)
if(BUILD_TESTING AND NOT Slicer_BUILD_BRAINSTOOLS)
    add_subdirectory(TestSuite)
endif()
endif()
