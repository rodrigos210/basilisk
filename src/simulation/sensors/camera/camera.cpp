/*
 ISC License

 Copyright (c) 2016, Autonomous Vehicle Systems Lab, University of Colorado at Boulder

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
/*
    Camera Module

    Note:   This module simulates a camera. It writes a camera message with it's specs and image requests, as well as provides a template for image coruption
    Author: Thibaud Teil
    Date:   October 03, 2019
 
 */

/* modify the path to reflect the new module names */
#include <Eigen/Dense>
#include <string.h>
#include "camera.h"
#include "architecture/messaging/system_messaging.h"
#include "utilities/rigidBodyKinematics.h"
#include "utilities/linearAlgebra.h"
#include "utilities/astroConstants.h"

/*! The constructor for the Camera module. It also sets some default values at its creation.  */
Camera::Camera()
{
    this->OutputBufferCount = 2;
    this->pointImageOut = NULL;
    
    /*! Default values for the camera.  */
    strcpy(this->parentName, "spacecraft");
    this->cameraID = 1;
    this->resolution[0] = 512;
    this->resolution[1] = 512;
    this->renderRate = 60*1E9;
    v3SetZero(this->cameraPos_B);
    v3SetZero(this->sigma_CB);
    this->cameraIsOn = 0;
    this->filename = "";
    this->fieldOfView = 0.7;
    strcpy(this->skyBox, "black");

    /*! Default values for the perturbations.  */
    this->gaussian = 0;
    this->darkCurrent = 0;
    this->saltPepper = 0;
    this->cosmicRays = 0;
    this->blurParam = 0;
    this->hsv = std::vector<int>{0, 0, 0};
    this->rgbPercent = std::vector<int>{0, 0, 0};
    
    return;
}

/*! Selfinit performs the first stage of initialization for this module.
 It's primary function is to create messages that will be written to.
 @return void
 */
void Camera::SelfInit()
{
    /*! - Create output message of image */
    this->imageOutMsgID = SystemMessaging::GetInstance()->CreateNewMessage(this->imageOutMsgName,sizeof(CameraImageMsg),this->OutputBufferCount,"CameraImageMsg",this->moduleID);
    /*! - Create output message for camera */
    this->cameraOutID = SystemMessaging::GetInstance()->CreateNewMessage(this->cameraOutMsgName,sizeof(CameraConfigMsg),this->OutputBufferCount,"CameraConfigMsg",this->moduleID);
}


/*! CrossInit performs the second stage of initialization for this module.
 It's primary function is to link the input messages that were created elsewhere.
 @return void
 */
void Camera::CrossInit()
{
    /*! - Get the image data message ID*/
    this->imageInMsgID = SystemMessaging::GetInstance()->subscribeToMessage(this->imageInMsgName,sizeof(CameraImageMsg), this->moduleID);
}

/*! This is the destructor */
Camera::~Camera()
{
    return;
}


/*! This method performs a complete reset of the module.  Local module variables that retain time varying states between function calls are reset to their default values.
 @return void
 @param this The configuration data associated with the module
 */
void Camera::Reset(uint64_t CurrentSimNanos)
{
    return;
}

/*!
 * Adjusts the HSV values of each pixel.
 * Can be used to shift the hue, saturation, and brightness of an image.
 * @param cv::Mat source image
 * @param cv::Mat destination of modified image
 * @param std::vector<int> of H,S,V adjustment factors. H (-180 to 180) is added, S and V are percent multiplier factors)
 * @return void
 */
void Camera::hueShift(const cv::Mat mSrc, cv::Mat &mDst, std::vector<int> HSV){
    cv::Mat hsv;
    cvtColor(mSrc, hsv, cv::COLOR_BGR2HSV);
    
    for (int j = 0; j < mSrc.rows; j++) {
        for (int i = 0; i < mSrc.cols; i++) {
            // Saturation is hsv.at<Vec3b>(j, i)[1] range: [0-255]
            // Value is hsv.at<Vec3b>(j, i)[2] range: [0-255]
            
            // hue range: [0-179)
            hsv.at<cv::Vec3b>(j, i)[0] = (hsv.at<cv::Vec3b>(j, i)[0] + this->hsv[0]) % 180;
            hsv.at<cv::Vec3b>(j, i)[1] = (hsv.at<cv::Vec3b>(j, i)[1]) * (this->hsv[1]/100. + 1.);
            hsv.at<cv::Vec3b>(j, i)[2] = (hsv.at<cv::Vec3b>(j, i)[2]) * (this->hsv[2]/100. + 1.);

            // saturate S and V values to [0,255]
            for(int k = 1; k < 3; k++){
                if(hsv.at<cv::Vec3b>(j,i)[k] < 0){
                    hsv.at<cv::Vec3b>(j,i)[k] = 0;
                }
                if(hsv.at<cv::Vec3b>(j,i)[k] > 255){
                    hsv.at<cv::Vec3b>(j,i)[k] = 255;
                }
            }
        }
    }
    cvtColor(hsv, mDst, cv::COLOR_HSV2BGR);
}

/*!
 * Adjusts the RGB values of each pixel by a percent value.
 * Can be used to simulate a sensor with different sensitivities to R, G, and B.
 * @param cv::Mat source image
 * @param cv::Mat destination of modified image
 * @param std::vector<int> of R,G,B scaling factors (percent multipliers)
 * @return void
 */
void Camera::RGBAdjustPercent(const cv::Mat mSrc, cv::Mat &mDst, std::vector<int> RGB){
    cv::Mat mRGB = cv::Mat(mSrc.size(), mSrc.type());
    mSrc.convertTo(mRGB, mSrc.type());
    
    // RGB values range [0, 255]
    // if value after adjustment is < 0 take 0
    // if value after is > 255 take 255
    for (int j = 0; j < mSrc.rows; j++) {
        for (int i = 0; i < mSrc.cols; i++) {
            mRGB.at<cv::Vec3b>(j,i)[0] = mRGB.at<cv::Vec3b>(j,i)[0] * (this->rgbPercent[0]/100. + 1.);
            mRGB.at<cv::Vec3b>(j,i)[1] = mRGB.at<cv::Vec3b>(j,i)[1] * (this->rgbPercent[1]/100. + 1.);
            mRGB.at<cv::Vec3b>(j,i)[2] = mRGB.at<cv::Vec3b>(j,i)[2] * (this->rgbPercent[2]/100. + 1.);
            
            // prevent overflow
            for(int k = 0; k < 3; k++){
                if(mRGB.at<cv::Vec3b>(j,i)[k] < 0){
                    mRGB.at<cv::Vec3b>(j,i)[k] = 0;
                }
                if(mRGB.at<cv::Vec3b>(j,i)[k] > 255){
                    mRGB.at<cv::Vec3b>(j,i)[k] = 255;
                }
            }
        }
    }
    mRGB.convertTo(mDst, mSrc.type());
}

/*!
 * Adds gaussian noise to an image.
 * Can be used to add color noise and dark current.
 * @param cv::Mat source image
 * @param cv::Mat destination of modified image
 * @param double mean pixel value
 * @param double standard deviation of pixel value
 * @return void
 */
void Camera::AddGaussianNoise(const cv::Mat mSrc, cv::Mat &mDst, double Mean, double StdDev)
{
    cv::Mat mSrc_16SC;
    //CV_16SC3 means signed 16 bit shorts three channels
    cv::Mat mGaussian_noise = cv::Mat(mSrc.size(), CV_16SC3);
    /*!  Generates random noise in a normal distribution.*/
    randn(mGaussian_noise, cv::Scalar::all(Mean), cv::Scalar::all(StdDev));
    
    mSrc.convertTo(mSrc_16SC, CV_16SC3);
    /*!  Adds the noise layer to the image layer with a weighted add to prevent overflowing the pixels.*/
    addWeighted(mSrc_16SC, 1.0, mGaussian_noise, 1.0, 0.0, mSrc_16SC);
    mSrc_16SC.convertTo(mDst,mSrc.type());
}

/*!
 * Adds dead and hot pixels to an image.
 * @param cv::Mat source image
 * @param cv::Mat destination of modified image
 * @param float probability of dead pixels
 * @param float probability of hot pixels
 * @return void
 */
void Camera::AddSaltPepper(const cv::Mat mSrc, cv::Mat &mDst, float pa, float pb){
    /*! These lines will make the hot and dead pixels different every time.*/
    // uint64 initValue = time(0);
    // RNG rng(initValue);
    
    /*! This line makes the hot and dead pixels the same frame to frame.*/
    cv::RNG rng;
    
    /*!  Determines the amount of hot/dead pixels based on the input probabilities.*/
    int amount1 = mSrc.rows * mSrc.cols * pa;
    int amount2 = mSrc.rows * mSrc.cols * pb;
    
    cv::Mat mSaltPepper = cv::Mat(mSrc.size(), mSrc.type());
    mSrc.convertTo(mSaltPepper, mSrc.type());
    
    cv::Vec3b black;
    black.val[0] = 0;
    black.val[1] = 0;
    black.val[2] = 0;
    
    cv::Vec3b white;
    white.val[0] = 255;
    white.val[1] = 255;
    white.val[2] = 255;
    
    /*!  Chooses random pixels to be stuck or dead in the amount calculated previously.*/
    for(int counter = 0; counter < amount1; counter++){
        mSaltPepper.at<cv::Vec3b>(rng.uniform(0, mSaltPepper.rows), rng.uniform(0, mSaltPepper.cols)) = black;
    }
    
    for(int counter = 0; counter < amount2; counter++){
        mSaltPepper.at<cv::Vec3b>(rng.uniform(0, mSaltPepper.rows), rng.uniform(0, mSaltPepper.cols)) = white;
    }
    
    mSaltPepper.convertTo(mDst, mSrc.type());
}

/*!
 * Adds a cosmic ray to an image. The ray is modelled as a single pixel wide white line.
 * @param cv::Mat source image
 * @param cv::Mat destination of modified image
 * @param float probability of getting a ray each frame
 * @param double if adding multiple rays pass in the number of each to guarantee a random ray
 * @param int max length of cosmic ray
 * @return void
 */
void Camera::AddCosmicRay(const cv::Mat mSrc, cv::Mat &mDst, float probThreshhold, double randOffset, int maxSize){
    /*! Uses the current sim time and the random offset to ensure a different ray every time.*/
    uint64 initValue = CurrentSimNanos;
    cv::RNG rng(initValue + time(0) + randOffset);
    
    float prob = rng.uniform(0.0, 1.0);
    if (prob > probThreshhold) {
        cv::Mat mCosmic = cv::Mat(mSrc.size(), mSrc.type());
        mSrc.convertTo(mCosmic, mSrc.type());
    
        /*!  Chooses a random point on the image. Then chooses a second random point within 50 pixels in either direction.*/
        int x = rng.uniform(0, mCosmic.rows);
        int y = rng.uniform(0, mCosmic.cols);
        int deltax = rng.uniform(-maxSize/2, maxSize/2);
        int deltay = rng.uniform(-maxSize/2, maxSize/2);
        
        cv::Point p1 = cv::Point(x, y);
        cv::Point p2 = cv::Point(x + deltax, y + deltay);
        line(mCosmic, p1, p2, cv::Scalar(255, 255, 255), 1, cv::LINE_8);
    
        mCosmic.convertTo(mDst, mSrc.type());
    }
}

/*!
 * Adds a user specified number of cosmic rays to an image. Rays are modelled as a single pixel wide white line.
 * The maximum length is hard-coded as 50 pixels.
 * @param cv::Mat source image
 * @param cv::Mat destination of modified image
 * @param double number of cosmic rays to be added
 * @return void
 */
void Camera::AddCosmicRayBurst(const cv::Mat mSrc, cv::Mat &mDst, double num){
    cv::Mat mCosmic = cv::Mat(mSrc.size(), mSrc.type());
    mSrc.convertTo(mCosmic, mSrc.type());
    for(int i = 0; i < std::round(num); i++){
        /*! Threshold defined such that 1 provides a 1/50 chance of getting a ray, and 10 will get about 5 rays per image*/
        /*! Currently length is limited to 50 pixels*/
        AddCosmicRay(mCosmic, mCosmic, 1/(std::pow(num,2)+0.02), i+1, 50);
    }
    mCosmic.convertTo(mDst, mSrc.type());
}

/*!
 * Applys all of the various pertubations to an image with user specified levels.
 * Each parameter is a double scaling actor. A parameter of 0 will result in the respective perturbation not being applied.
 * @param cv::Mat source image
 * @param cv::Mat destination of modified image
 * @param double scaling factor for gaussian noise
 * @param double scaling factor for dark current
 * @param double scaling factor for hot and dead pixels
 * @param double number of cosmic rays to add
 * @param double size of blur to apply
 * @return void
 */
void Camera::ApplyFilters(cv::Mat mSource, cv::Mat &mDst, double gaussian, double darkCurrent, double saltPepper, double cosmicRays, double blurparam){

    cv::Mat mFilters(mSource.size(), mSource.type());
    mSource.convertTo(mFilters, mSource.type());

    if (gaussian > 0){
        float scale = 2;
        AddGaussianNoise(mFilters, mFilters, 0, gaussian * scale);
        cv::threshold(mFilters, mFilters, gaussian*6, 255, cv::THRESH_TOZERO);
    }
    if(blurparam > 0){
        int blurSize = std::round(blurparam);
        blur(mFilters, mFilters, cv::Size(blurSize, blurSize), cv::Point(-1 , -1));
    }
    if(darkCurrent > 0){
        float scale = 15;
        AddGaussianNoise(mFilters, mFilters, darkCurrent * scale, 0.0);
    }
    if (abs(this->hsv[0])+this->hsv[1]+this->hsv[2] != 0) {
        hueShift(mFilters, mFilters, this->hsv);
    }
    if (this->rgbPercent[0]+this->rgbPercent[1]+this->rgbPercent[2] != 0) {
        RGBAdjustPercent(mFilters, mFilters, this->rgbPercent);
    }
    if (saltPepper > 0){
        float scale = 0.00002;
        AddSaltPepper(mFilters, mFilters, saltPepper * scale, saltPepper * scale);
    }
    if(cosmicRays > 0){
        AddCosmicRayBurst(mFilters, mFilters, std::round(cosmicRays));
    }
    
    mFilters.convertTo(mDst, mSource.type());
}

/*! This module reads an OpNav image and extracts circle information from its content using OpenCV's HoughCircle Transform. It performs a greyscale, a bur, and a threshold on the image to facilitate circle-finding. 
 @return void
 @param CurrentSimNanos The clock time at which the function was called (nanoseconds)
 */
void Camera::UpdateState(uint64_t CurrentSimNanos)
{
    this->CurrentSimNanos = CurrentSimNanos;
    std::string localPath;
    CameraImageMsg imageBuffer;
    CameraImageMsg imageOut;
    CameraConfigMsg cameraMsg;
    memset(&imageBuffer, 0x0, sizeof(CameraImageMsg));
    memset(&imageOut, 0x0, sizeof(CameraImageMsg));
    memset(&cameraMsg, 0x0, sizeof(CameraConfigMsg));
    
    /*! - Populate the camera message */
    cameraMsg.cameraID = this->cameraID;
    strcpy(cameraMsg.parentName, this->parentName);
    cameraMsg.resolution[0] = this->resolution[0];
    cameraMsg.resolution[1] = this->resolution[1];
    cameraMsg.renderRate = this->renderRate;
    cameraMsg.fieldOfView = this->fieldOfView;
    cameraMsg.isOn = this->cameraIsOn;
    v3Copy(this->cameraPos_B, cameraMsg.cameraPos_B);
    v3Copy(this->sigma_CB, cameraMsg.sigma_CB);
    strcpy(cameraMsg.skyBox, this->skyBox);
    
    /*! - Update the camera config data no matter if an image is present*/
    SystemMessaging::GetInstance()->WriteMessage(this->cameraOutID, CurrentSimNanos, sizeof(CameraConfigMsg), reinterpret_cast<uint8_t *>(&cameraMsg), this->moduleID);
    
    cv::Mat imageCV, blurred;
    if (this->saveDir !=""){
        localPath = this->saveDir + std::to_string(CurrentSimNanos*1E-9) + ".jpg";
    }
    /*! - Read in the bitmap*/
    SingleMessageHeader localHeader;
    if(this->imageInMsgName != "")
    {
        SystemMessaging::GetInstance()->ReadMessage(this->imageInMsgID, &localHeader,
                                                    sizeof(CameraImageMsg), reinterpret_cast<uint8_t*>(&imageBuffer), this->moduleID);
        this->sensorTimeTag = localHeader.WriteClockNanos;
    }
    /* Added for debugging purposes*/
    if (!this->filename.empty()){
        imageCV = imread(this->filename, cv::IMREAD_COLOR);
        ApplyFilters(imageCV, blurred, this->gaussian, this->darkCurrent, this->saltPepper, this->cosmicRays, this->blurParam);
        if (this->saveImages == 1){
            cv::imwrite(localPath, blurred);
        }
    }
    else if(imageBuffer.valid == 1 && imageBuffer.timeTag >= CurrentSimNanos){
        /*! - Recast image pointer to CV type*/
        std::vector<unsigned char> vectorBuffer((char*)imageBuffer.imagePointer, (char*)imageBuffer.imagePointer + imageBuffer.imageBufferLength);
        imageCV = cv::imdecode(vectorBuffer, cv::IMREAD_COLOR);
        
        ApplyFilters(imageCV, blurred, this->gaussian, this->darkCurrent, this->saltPepper, this->cosmicRays, this->blurParam);
        if (this->saveImages == 1){
            cv::imwrite(localPath, blurred);
        }
        /*! If the permanent image buffer is not populated, it will be equal to null*/
        if (this->pointImageOut != NULL) {
            free(this->pointImageOut);
            this->pointImageOut = NULL;
        }
        /*! - Encode the cv mat into a png for the future modules to decode it the same way */
        std::vector<unsigned char> buf;
        std::vector<int> compression;
        compression.push_back(0);
        cv::imencode(".png", blurred, buf, compression);
        /*! - Output the saved image */
        imageOut.valid = 1;
        imageOut.timeTag = imageBuffer.timeTag;
        imageOut.cameraID = imageBuffer.cameraID;
        imageOut.imageType = imageBuffer.imageType;
        imageOut.imageBufferLength = (int32_t)buf.size();
        this->pointImageOut = malloc(imageOut.imageBufferLength*sizeof(char));
        memcpy(this->pointImageOut, &buf[0], imageOut.imageBufferLength*sizeof(char));
        imageOut.imagePointer = this->pointImageOut;
        
        SystemMessaging::GetInstance()->WriteMessage(this->imageOutMsgID, CurrentSimNanos, sizeof(CameraImageMsg), reinterpret_cast<uint8_t *>(&imageOut), this->moduleID);
        
        return;
    }
    else{
        /*! - If no image is present, write zeros in message */
        SystemMessaging::GetInstance()->WriteMessage(this->imageOutMsgID, CurrentSimNanos, sizeof(CameraImageMsg), reinterpret_cast<uint8_t *>(&imageBuffer), this->moduleID);
        return;}
 
}

