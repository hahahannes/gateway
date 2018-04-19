# Goal
Implement a gateway to access a CoAP resource directory, which stores the CoAP endpoints and services.
Requested functionalities:
* Device and service registration as well as discovery
* Possibility to send data to the platform over web socket connection
* Possibility to send commands from the platform to the coap devices

# Functionality
The client connector starts a connection to the platform connector via web sockets.
Then it can send data to the platform and execute incoming commands. Therefor it accesses a resource direcotry to gather the ip adress and sends a request to the device.
New devices register on the resource directory which sends the registration data to this gateway.

## CoRE Resource Directory (RD)
CoAP Server.
This project is an implementation of the [CoRE Resource Directory Standard, Version 11](https://tools.ietf.org/html/draft-ietf-core-resource-directory-11) and the [specifications of the CoAP Protocol regarding Service Registration and Discovery](https://tools.ietf.org/html/rfc7252#page-64). 

* Things register on the platform after multicast discovery or by already knowing the platform
* The resource directory acts as a coap client and discovers things and registers them

The project is written in Python3.4.
A thing has to know the platform or has to discover it to register itself. Therefor it has the ip adress hard coded or uses device to device or device to server discovery mechanisms. For example it can use Multicast DNS to find the platform in a local network by using IP multicast or it can find the platform in an other directory server using the CoRE Resource Directory Standard.
The platform as a resource directory exposes several API endpoints:
* ./well-known/core
* /rd-lookup
* /rd
* /rd-group

The "./well-known/core" endpoint is defined in the CoAP Protocol and should be used to provide informations about the thing. The platform as resource directory as well as the thing should provide it. It can be accessed by an unicast request or a multicast request.

The "/rd-lookup" endpoint is be used by the an interested client to discover and search for things within the platform.

The "/rd" endpoint is the main endpoint and is used by the thing itself on the platform using different parameters.


## Executer
CoAP Client
The Executer module contains an CoAP executor that recieves commands of the Web Socket Connector and executes them by looking up for the requested device and perfoming a CoAP request.

## Observer
CoAP Client
The observer gets the data of all connected devices by looking up in the RD and performing frequently GET requests. Next it sends the data via the Web Socket Connector to the Platform Connector.

## Pinger
CoAP Client
The pinger checks frequently if the registered devices in the RD are online or offline. If a device does not respond to a simple empty CoAP GET Ping it is considered as disconnected but not as removed. Within in the RD it gets the status 0 for disconnected and on the platform it gets disconnected.

# Usage
Run the main script
```shell
python3 main.py
```

