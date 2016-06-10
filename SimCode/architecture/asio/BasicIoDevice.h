//
// BasicIoDevice.h
//
// University of Colorado, Autonomous Vehicle Systems (AVS) Lab
// Unpublished Copyright (c) 2012-2015 University of Colorado, All Rights Reserved
//

#ifndef BASIC_IO_DEVICE_H
#define BASIC_IO_DEVICE_H

#include <boost/asio.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/scoped_ptr.hpp>
#include <boost/bind.hpp>
#include <iostream>

#ifndef STREAM_BUFFER_SIZE
#define STREAM_BUFFER_SIZE 65507
#endif

/*---------------------------------------------------------------------------*/
class BasicIoObject
{
public:
    BasicIoObject() {}

    virtual ~BasicIoObject() {}

    virtual bool isOpen(void) = 0;
    virtual bool close(void) = 0;

    virtual bool receiveData(std::vector<char> &data) = 0;
    virtual bool sendData(std::string data) = 0;

    virtual void clearBuffers(void) = 0;

};

/*---------------------------------------------------------------------------*/
template<typename StreamType>
class BasicIoObject_t : public BasicIoObject
{
public:
    BasicIoObject_t();
    virtual ~BasicIoObject_t();

    virtual bool isOpen(void);
    virtual bool close(void);

    virtual bool receiveData(std::vector<char> &data) { return 1; }
    virtual bool sendData(std::string data) { return 1; }

    std::string getInputBuffer() { return m_inboundBuffer; }
    virtual void clearBuffers(void) {}
    void handleClearBuffers(const boost::system::error_code &ec, size_t bytes_transferred);

protected:
    boost::scoped_ptr<StreamType> m_stream;
    std::string m_outboundBuffer;
    std::vector<char> m_inboundBuffer;
};

/*---------------------------------------------------------------------------*/
template<typename StreamType>
BasicIoObject_t<StreamType>::BasicIoObject_t()
    : BasicIoObject()
{
    m_inboundBuffer.clear();
    m_outboundBuffer.clear();
}

template<typename StreamType>
BasicIoObject_t<StreamType>::~BasicIoObject_t()
{
    close();
}

template<typename StreamType>
bool BasicIoObject_t<StreamType>::isOpen()
{
    if(m_stream) {
        return m_stream->is_open();
    } else {
        return false;
    }
}

template<typename StreamType>
bool BasicIoObject_t<StreamType>::close(void)
{
    if(isOpen()) {
        boost::system::error_code ec;
        m_stream->close(ec);
        if(ec) {
            std::cout << "Error in " << __FUNCTION__ << " (" << ec.value() << ") " << ec.message() << std::endl;
            return false;
        }
        m_inboundBuffer.clear();
        m_outboundBuffer.clear();
    }
    return true;
}

template<typename StreamType>
void BasicIoObject_t<StreamType>::handleClearBuffers(const boost::system::error_code &ec,
        size_t bytesReceived)
{
    if(ec) {
        std::cout << "Error in " << __FUNCTION__ << " (" << ec.value() << ") " << ec.message() << std::endl;
    }
}

#endif