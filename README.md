# SoleShapper - Blender Plug-In

SoleShapper is a Blender plug-in designed specifically for shoe designers who need intuitive, art-directed control over shaping sole meshes through procedural methods rather than manual sculpting.

## Features

- Default sole mesh baked into the plugin (no external files needed)
- Load custom OBJ meshes for any sole shape
- Procedural noise deformation applied via vertex normals
- Zone masking for targeted deformation
- Export deformed soles as STL or OBJ
- Reset to base mesh and iterate freely

## Requirements

- Blender 4.2.0 or later (tested with Blender 5.x)

## Installation

1. Download or clone this repository
2. Open Blender and go to **Edit > Preferences**
3. Click the **Add-ons** tab
4. Click the drop-down arrow next to the **Install** button and choose **Install from Disk...**
5. Navigate to this folder and select `__init__.py`
6. Tick the checkbox to enable the add-on

## Usage

1. Press **N** in the 3D Viewport to open the side panel
2. Look for the **SoleShapper2** tab
3. Click **Load Default Sole** or **Load Custom OBJ**
4. Adjust noise parameters (scale, strength, seed, etc.)
5. Click **Apply Noise Deformation**
6. Reset to base and try again any time

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
