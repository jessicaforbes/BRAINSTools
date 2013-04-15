
### HACK:  Just force download of all data and do nothing with it for now.
set(ALL_DICOM_TARBALLS
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertGeSignaHdxBMatrixTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertGeSignaHdxBigEndianTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertGeSignaHdxFSLTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertGeSignaHdxTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertGeSignaHdxtBMatrixTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertGeSignaHdxtTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchieva2BMatrixTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchieva2Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchieva3Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchieva4Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchieva6Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchieva7Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchievaBMatrixTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchievaBigEndianTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertPhilipsAchievaTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertSiemensTrioSyngo2004A1Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertSiemensTrioSyngo2004A2Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertSiemensTrioTim2Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertSiemensTrioTim3Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertSiemensTrioTimBigEndian1Test.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertSiemensTrioTimTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/DWIConvertSiemensVerioTest.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/GeSignaHDx.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/GeSignaHDxBigEndian.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/GeSignaHDxt.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/PhilipsAchieva1.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/PhilipsAchieva2.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/PhilipsAchieva3.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/PhilipsAchieva4.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/PhilipsAchieva6.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/PhilipsAchieva7.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/PhilipsAchievaBigEndian1.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/SiemensTrio-Syngo2004A-1.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/SiemensTrio-Syngo2004A-2.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/SiemensTrioTim1.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/SiemensTrioTim2.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/SiemensTrioTim3.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/SiemensTrioTimBigEndian1.tar.gz
${TestData_DIR}/DWI_TestData_TARBALLS/SiemensVerio.tar.gz
)

# THIS IS A HACK FOR TESTING.  It should be more elegant in the future.
set(AllTARBALLSDownloads "")
foreach( curr_tarball ${ALL_DICOM_TARBALLS})
  message(STATUS "Working on ${curr_tarball}")
  get_filename_component(base_filename "${curr_tarball}" NAME)
  ExternalData_add_test( ${PROJECT_NAME}FetchData NAME UncompressDWITarballs_${base_filename}
    WORKING_DIRECTORY ${DWIConvert_BINARY_DIR}
    COMMAND  ${CMAKE_COMMAND} -E tar xzf DATA{${curr_tarball}}
  )
  list(APPEND AllTARBALLSDownloads UncompressDWITarballs_${base_filename})
endforeach()
########## END HACK

#
# Test CLI executables
#
include_regular_expression("^.*$")

include_directories(${DWIConvert_SOURCE_DIR})
include_directories(${DWIConvert_BINARY_DIR})
include_directories(${ModuleDescriptionParser_SOURCE_DIR})

set(DWIBinDir ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

foreach(CLP DWICompare DWISimpleCompare)
  set ( ${CLP}_SOURCE ${CLP}.cxx)
  generateclp(${CLP}_SOURCE ${CLP}.xml)
  add_executable(${CLP} ${${CLP}_SOURCE})
  target_link_libraries (${CLP} DWIConvertSupportLib )
endforeach()

add_executable(FSLTextFileCompare FSLTextFileCompare.cxx)
target_link_libraries (FSLTextFileCompare DWIConvertSupportLib )

add_executable(NrrdToNIfTI NrrdToNIfTI.cxx)
target_link_libraries(NrrdToNIfTI DWIConvertSupportLib)

set (CLP DWIConvert)
add_executable(${CLP}Test ${CLP}Test.cxx ${DWIConvertTest_SRC})
add_dependencies(${CLP}Test ${CLP} ${AllTARBALLSDownloads})
target_link_libraries(${CLP}Test DWIConvertSupportLib BRAINSCommonLib )

if(NOT SETIFEMPTY)
  macro(SETIFEMPTY)
    set(KEY ${ARGV0})
    set(VALUE ${ARGV1})
    if(NOT ${KEY})
      set(${ARGV})
    endif(NOT ${KEY})
  endmacro(SETIFEMPTY KEY VALUE)
endif(NOT SETIFEMPTY)

set(TEMP ${CMAKE_CURRENT_BINARY_DIR})

include(${CMAKE_CURRENT_LIST_DIR}/MIDAS.cmake)
SETIFEMPTY(MIDAS_REST_URL "http://midas.kitware.com/api/rest" CACHE STRING "The MIDAS server where testing data resides")

set(MIDAS_KEY_DIR "${DWIConvert_SOURCE_DIR}/TestSuite/keys")

add_test(NAME DWIConvertHelpTest
  COMMAND ${SLICER_LAUNCH_COMMAND} $<TARGET_FILE:DWIConvertTest> DWIConvertTest --help
  )

add_test(NAME DWIConvertDWICompareHelpTest
  COMMAND ${Slicer_LAUNCH_COMMAND} $<TARGET_FILE:DWICompare>
  --help
  )

midas_add_test(NAME DWIConvertGeSignaHdxTest COMMAND ${CMAKE_COMMAND}
  -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{GeSignaHDx.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/GeSignaHDx
  -D TEST_TEMP_OUTPUT=${TEMP}/GeSignaHDxTest.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertGeSignaHdxFSLTest COMMAND ${CMAKE_COMMAND}
  -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWISimpleCompare>
  -D TEST_TEXT_COMPARE=$<TARGET_FILE:FSLTextFileCompare>
  -D TEST_BASELINE=MIDAS{GeSignaHDx.nii.gz.md5}
  -D TEST_BASELINE_BVEC=MIDAS{GeSignaHDx.bvec.md5}
  -D TEST_BASELINE_BVAL=MIDAS{GeSignaHDx.bval.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/GeSignaHDx
  -D TEST_TEMP_OUTPUT=${TEMP}/GeSignaHDxTest.nii.gz
  -D TEST_FSL_FLAG=ON
  -D TEST_TEMP_BVEC=${TEMP}/GeSignaHDxTest.bvec
  -D TEST_TEMP_BVAL=${TEMP}/GeSignaHDxTest.bval
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

add_test(NAME FSLToNrrdTest
  COMMAND ${CMAKE_COMMAND}
  -DVEC_FILE=${TEMP}/GeSignaHDxTest.bvec
  -DVAL_FILE=${TEMP}/GeSignaHDxTest.bval
  -DNII_FILE=${TEMP}/GeSignaHDxTest.nii.gz
  -DNRRD_FILE=${TEMP}/FSLToNrrdTest.nrrd
  -DNRRD_COMPARE_FILE=${TEMP}/GeSignaHDxTest.nrrd
  -DFSL_TO_NRRD=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -P ${CMAKE_CURRENT_LIST_DIR}/FSLToNrrdTest.cmake
  )

set_property(TEST FSLToNrrdTest
  APPEND PROPERTY DEPENDS DWIConvertGeSignaHdxFSLTest)

add_test(NAME NrrdToFSLTest
  COMMAND ${CMAKE_COMMAND}
  -DNRRD_FILE=${TEMP}/FSLToNrrdTest.nrrd
  -DVEC_COMPARE_FILE=${TEMP}/GeSignaHDxTest.bvec
  -DVAL_COMPARE_FILE=${TEMP}/GeSignaHDxTest.bval
  -DNII_COMPARE_FILE=${TEMP}/GeSignaHDxTest.nii.gz
  -DVEC_FILE=${TEMP}/NrrdToFSLTest.bvec
  -DVAL_FILE=${TEMP}/NrrdToFSLTest.bval
  -DNII_FILE=${TEMP}/NrrdToFSLTest.nii.gz
  -DNRRD_TO_FSL=$<TARGET_FILE:DWIConvert>
  -DTEST_COMPARE_PROGRAM=$<TARGET_FILE:DWISimpleCompare>
  -DTEXT_COMPARE_PROGRAM=$<TARGET_FILE:FSLTextFileCompare>
  -P ${CMAKE_CURRENT_LIST_DIR}/NrrdToFSLTest.cmake
  )

set_property(TEST NrrdToFSLTest
  APPEND PROPERTY DEPENDS FSLToNrrdTest)

midas_add_test(NAME DWIConvertGeSignaHdxBigEndianTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{GeSignaHDx.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/GeSignaHDxBigEndian
  -D TEST_TEMP_OUTPUT=${TEMP}/GeSignaHDxBigEndianTest.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertGeSignaHdxBMatrixTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{GeSignaHDx.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/GeSignaHDx
  -D TEST_TEMP_OUTPUT=${TEMP}/GeSignaHDxTest.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertGeSignaHdxtTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{GeSignaHDxt.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/GeSignaHDxt
  -D TEST_TEMP_OUTPUT=${TEMP}/GeSignaHDxtTest.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertGeSignaHdxtBMatrixTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{GeSignaHDxt.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/GeSignaHDxt
  -D TEST_TEMP_OUTPUT=${TEMP}/GeSignaHDxtTest.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchievaTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva1.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchieva1
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchieva1Test.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchievaBigEndianTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva1.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchievaBigEndian1
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchievaBigEndian1Test.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchievaBMatrixTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva1.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchieva1
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchieva1Test.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchieva2Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva2.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchieva2
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchieva2Test.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchieva2BMatrixTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva2.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchieva2
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchieva2Test.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchieva3Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva3.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchieva3
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchieva3Test.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchieva4Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva4.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchieva4
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchieva4Test.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchieva6Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva6.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchieva6
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchieva6Test.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertPhilipsAchieva7Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{PhilipsAchieva7.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/PhilipsAchieva7
  -D TEST_TEMP_OUTPUT=${TEMP}/PhilipsAchieva7Test.nrrd
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertSiemensTrioTimTest
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{SiemensTrioTim1.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/SiemensTrioTim1
  -D TEST_TEMP_OUTPUT=${TEMP}/SiemensTrioTim1Test.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertSiemensTrioTimBigEndian1Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{SiemensTrioTim1.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/SiemensTrioTimBigEndian1
  -D TEST_TEMP_OUTPUT=${TEMP}/SiemensTrioTimBigEndian1Test.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertSiemensTrioTim2Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{SiemensTrioTim2.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/SiemensTrioTim2
  -D TEST_TEMP_OUTPUT=${TEMP}/SiemensTrioTim2Test.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertSiemensTrioTim3Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{SiemensTrioTim3.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/SiemensTrioTim3
  -D TEST_TEMP_OUTPUT=${TEMP}/SiemensTrioTim3Test.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertSiemensVerioTest
  COMMAND ${CMAKE_COMMAND}
  -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{SiemensVerio.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/SiemensVerio
  -D TEST_TEMP_OUTPUT=${TEMP}/SiemensVerio.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertSiemensTrio_Syngo2004A_1Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{SiemensTrio-Syngo2004A-1.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/SiemensTrio-Syngo2004A-1
  -D TEST_TEMP_OUTPUT=${TEMP}/SiemensTrio-Syngo2004A-1.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

midas_add_test(NAME DWIConvertSiemensTrio_Syngo2004A_2Test
  COMMAND ${CMAKE_COMMAND} -D TEST_PROGRAM=$<TARGET_FILE:DWIConvert>
  -D TEST_COMPARE_PROGRAM=$<TARGET_FILE:DWICompare>
  -D TEST_BASELINE=MIDAS{SiemensTrio-Syngo2004A-2.nrrd.md5}
  -D TEST_INPUT=${DWIConvert_BINARY_DIR}/SiemensTrio-Syngo2004A-2
  -D TEST_TEMP_OUTPUT=${TEMP}/SiemensTrio-Syngo2004A-2.nrrd
  -D TEST_PROGRAM_ARGS=--useBMatrixGradientDirections
  -P ${CMAKE_CURRENT_LIST_DIR}/DicomToNrrdDWICompareTest.cmake
  )

ExternalData_Add_Target( ${PROJECT_NAME}FetchData )  # Name of data management target
