![](https://github.com/balena-labs-projects/balena-cam/blob/master/balena-cam/app/client/balena-cam-readme.png?raw=true)

# balenaCam using MQTT

Stream your balena device's camera feed publishing to a MQTT broker.

## Getting started

Running this project is as simple as deploying it to a fleet.

One-click deploy to balenaCloud:

[![](https://balena.io/deploy.png)](https://dashboard.balena-cloud.com/deploy)

**or**

- Sign up on [balena.io](https://balena.io/) and follow our [Getting Started Guide](https://balena.io/docs/learn/getting-started).
- Clone this repository to your local workspace.
- Unset (delete) the environment variable `BALENA_HOST_CONFIG_gpu_mem` or `RESIN_HOST_CONFIG_gpu_mem` if exists, from the `Configuration` side tab under "fleets".
- Set these variables in the `Configuration` side tab under "fleets".

  - `BALENA_HOST_CONFIG_start_x` = `1`
  - Set all the following `gpu_mem` variables so your Pi can autoselect how much memory to allocate for hardware accelerated graphics, based on how much RAM it has available

    | Key                                   | Value     |
    | ------------------------------------- | --------- |
    | **`BALENA_HOST_CONFIG_gpu_mem_256`**  | **`192`** |
    | **`BALENA_HOST_CONFIG_gpu_mem_512`**  | **`256`** |
    | **`BALENA_HOST_CONFIG_gpu_mem_1024`** | **`448`** |

- Using [Balena CLI](https://www.balena.io/docs/reference/cli/), push the code with `balena push <fleet-name>`.
- See the magic happening, your device is getting updated 🌟Over-The-Air🌟!
- In order for your device to be accessible over the internet, toggle the switch called `PUBLIC DEVICE URL`.
- Once your device finishes updating, you can watch the live feed by visiting your device's public URL.

### Password Protect your balenaCam device

To protect your balenaCam devices using a username and a password set the following environment variables.

| Key            | Value                      |
| -------------- | -------------------------- |
| **`username`** | **`yourUserNameGoesHere`** |
| **`password`** | **`yourPasswordGoesHere`** |

💡 **Tips:** 💡

- You can set them as [fleet environment variables](https://www.balena.io/docs/learn/manage/serv-vars/#fleet-environment-and-service-variables) and every new balenaCam device you add will be password protected.
- You can set them as [device environment variables](https://www.balena.io/docs/learn/manage/serv-vars/#device-environment-and-service-variables) and the username and password will be different on each device.

### Optional Settings

- To rotate the camera feed by 180 degrees, add a **device variable**: `rotation` = `1` (More information about this on the [docs](https://www.balena.io/docs/learn/manage/serv-vars/)).
- To suppress any warnings, add a **device variable**: `PYTHONWARNINGS` = `ignore`

### TURN server configuration

If you have access to a TURN server and you want your balenaCam devices to use it. You can easily configure it using the following environment variables. When you set them all the app will use that TURN server as a fallback mechanism when a direct WebRTC connection is not possible.

| Key                 | Value                                              |
| ------------------- | -------------------------------------------------- |
| **`STUN_SERVER`**   | **`stun:stun.l.google.com:19302`**                 |
| **`TURN_SERVER`**   | **`turn:<yourTURNserverIP>:<yourTURNserverPORT>`** |
| **`TURN_USERNAME`** | **`<yourTURNserverUsername>`**                     |
| **`TURN_PASSWORD`** | **`yourTURNserverPassword`**                       |

## Configure the MQTT broker

To configure where to publish the images via MQTT you will need to define some variables.


| Key            | Value                      |
| -------------- | -------------------------- |
| **`mqtt-broker`** | **`your broker IP address goes here`** |
| **`mqtt-port`** | **`your broker port goes here`** |
| **`mqtt-topic`** | **`the topic where you are going to publish goes here`** |

## Supported Browsers

- **Chrome** (but see note above)
- **Firefox** (but see note above)
- **Safari**
- **Edge** (only mjpeg stream)

## Become a balena poweruser

Want to learn more about what makes balena work? Try one of our [masterclasses](https://www.balena.io/docs/learn/more/masterclasses/overview/). Each lesson is a self-contained, deeply detailed walkthrough on core skills to be successful with your next edge project.

Check them out at our [docs](https://www.balena.io/docs/learn/more/masterclasses/overview/). Also, reach out to us on the [Forums](https://forums.balena.io/) if you need help.
