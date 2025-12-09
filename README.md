![](https://github.com/balena-labs-projects/balena-cam/blob/master/balena-cam/app/client/balena-cam-readme.png?raw=true)

# Edge Impulse + balenaCam + Node-RED and MQTT

This project stream your balena device's camera feed inferencing with Edge Impulse ML models and publishing to a MQTT broker. Node-RED enables developers to build applications on the top of the inferenced images.

This demo is intended for the Raspberry Pi 4 - any version of that board should work. You should plug a standard USB webcam into one of the USB ports of your Pi.

You'll also need a free [Edge Impulse account](https://edgeimp.com/master25) and an impulse that does image detection (sample public impulses for this are available that you can clone)

Finally, a free or paid [balenaCloud account](https://balena.io) which you can sign up for here.


## Getting started

Running this project is as simple as deploying it to a fleet.

One-click deploy to balenaCloud:

[![](https://balena.io/deploy.png)](https://dashboard.balena-cloud.com/deploy)

**Alternatively**

- Sign up on [balena.io](https://balena.io/) and follow our [Getting Started Guide](https://balena.io/docs/learn/getting-started).
- Clone this repository to your local workspace.
- To configure where to publish the images via MQTT you will need to define some variables. Set these variables in the `Device Variables` side tab under "fleets". 

    | Key                                   | Value     |
    | ------------------------------------- | --------- |
    | **`MQTT_BROKER`**  | **`mqtt`** |
    | **`MQTT_PORT`**  | **`1833`** |
    | **`MQTT_TOPIC`** | **`edge-impulse/enterprise/site/area/line/image`** |
    | **`USERNAME`** | **`balena`** |
    | **`PASSWORD`** | **`balena`** |

- Using [Balena CLI](https://www.balena.io/docs/reference/cli/), push the code with `balena push <fleet-name>`.
- See the magic happening, your device is getting updated 🌟Over-The-Air🌟!
- Once your device finishes updating, you can watch the live feed by visiting your device's public URL or using the local IP address (port 80).


## Become a balena poweruser

Want to learn more about what makes balena work? Try one of our [masterclasses](https://www.balena.io/docs/learn/more/masterclasses/overview/). Each lesson is a self-contained, deeply detailed walkthrough on core skills to be successful with your next edge project.

Check them out at our [docs](https://www.balena.io/docs/learn/more/masterclasses/overview/). Also, reach out to us on the [Forums](https://forums.balena.io/) if you need help.
