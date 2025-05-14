# Hunyuan3d x Blender Bridge

## Description

Hunyuan3d Bridge is a Blender addon that integrates Hunyuan3D (specially Hunyuan 2.5) functionalities directly within Blender. This allows users to leverage the power of Hunyuan3D for their 3D projects without leaving the Blender environment. (Further details about the specific functionalities can be added here).

## Features

*   Generate 3D models from text prompts using Hunyuan3D API.
*   Latest Hunyuan3D 2.5!
*   Download and Import 3D models into Blender.
*   3D assets management.
*   Customizable settings for model generation.
*   User-friendly interface.


## Requirements

*   Blender 4.4+
*   Python 3.11+
*   Hunyuan3D account (you should provide a key and user to the addon)

## Installation

1.  Download the latest release `hunyuan3d_bridge.zip` (or the specific addon file) from the releases page or clone repo and compress the `hunyuan3d_blender` folder into a `zip` file.
2.  Open Blender (4.4+).
3.  Go to `Edit` > `Preferences` > `Add-ons`.
4.  Click `Install from disk` and navigate to the downloaded `.zip` file.
5.  Select the file and click `Install Add-on`.
6.  Enable the addon by checking the box next to its name ("Hunyuan3d Bridge").

## Usage

*   N-Panel, 'AI' tab, panel called 'Hunyuan3D'
*   First, you need to provide a key and user to the addon and start a session.
*   Then, you can generate 3D models from text prompts using the `Generate` button.

## Dependencies

This addon bundles the following Python modules:

*   imageio-2.37.0
*   numpy-2.2.3
*   pillow-11.1.0

These dependencies are handled automatically by the addon.

## Minimum Blender Version

Blender 4.4.0 or newer is required to use this addon.

## License

This addon is licensed under the GPL-2.0-or-later.
See the `blender_manifest.toml` file for more details.

## Maintainer

This addon is maintained by @jfranmatheu.

## Permissions

This addon requires the following permissions:
*   **Network Access**: This addon makes network requests to the Hunyuan3D API. Used for 3D model generation and download of 3d models.
*   **File Access**: This addon can read and write files to the Blender file system. Used for 3d assets management, import of 3d assets.

## Future Work

*   Improve the user interface.
*   Support image to 3d.
*   Support multi-image to 3d.
