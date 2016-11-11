/*
Copyright (c) 2016, Autonomous Vehicle Systems Lab, Univeristy of Colorado at Boulder

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

*/


#ifndef _AVSEIGENSUPPORT_
#define _AVSEIGENSUPPORT_
#include <Eigen/Dense>

/*! \addtogroup Sim Utility Group
* @{
*/

//!@brief General conversion between any Eigen matrix and output array
void eigenMatrixXd2CArray(Eigen::MatrixXd inMat, double *outArray);
//!@brief Rapid conversion between 3-vector and output array
void eigenVector3d2CArray(Eigen::Vector3d & inMat, double *outArray);
//!@brief Rapid conversion between 3x3 matrix and output array
void eigenMatrix3d2CArray(Eigen::Matrix3d & inMat, double *outArray);
//!@brief General conversion between a C array and an Eigen matrix
void cArray2EigenMatrixXd(double *inArray, Eigen::MatrixXd & outMat, int nRows, int nCols);
//!@brief Specific conversion between a C array and an Eigen 3-vector
void cArray2EigenVector3d(double *inArray, Eigen::Vector3d & outMat);
//!@brief Specfici conversion between a C array and an Eigen 3x3 matrix
void cArray2EigenMatrix3d(double *inArray, Eigen::Matrix3d & outMat);


#endif /* _GaussMarkov_HH_ */
