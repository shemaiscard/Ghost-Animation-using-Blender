# Ghost Animation Using Cloth Physics in Blender

A computer animation project demonstrating the creation of a ghost animation using cloth physics simulation in Blender. This project was developed as part of a Computer Animation & Modeling final project.

## Table of Contents
- [Demo](#demo)
- [Introduction](#introduction)
- [Setup](#setup)
- [Cloth Simulation Basics](#cloth-simulation-basics)
- [Animating Textures & Geometry](#animating-textures--geometry)
- [Camera Setting & Rendering](#camera-setting--rendering)
- [Screenshots](#screenshots)

## Demo

https://github.com/shemaiscard/Ghost-Animation-using-Blender/raw/main/Ghost%20video.mp4

## Introduction

This project aims to create a realistic ghost animation utilizing Blender's cloth physics system. The ghost is constructed using basic geometric shapes (sphere for head, cylinders for arms) with a cloth plane draped over it to achieve a ghostly appearance. The animation combines cloth simulation with strategic lighting and texturing to enhance the spooky effect.

## Setup

### Creating the Ghost Structure
1. Created a sphere for the ghost's head and cylinders for the arms
2. Added two planes:
   - Upper plane: Acts as the cloth
   - Lower plane: Serves as the ground
3. Positioned all objects to form a ghost-like shape

### Applying Cloth Physics
- Applied cloth physics to the upper plane
- Configured collision settings between cloth and ghost structure
- Fine-tuned physics parameters for realistic cloth behavior

## Cloth Simulation Basics

### Adding Cloth Modifier
- Applied cloth modifier to the plane
- Adjusted properties:
  - Gravity
  - Weight
  - Collision parameters
- Optimized for soft, floating effect

### Smoothness and Scale
- Added subdivision modifier for smooth cloth appearance
- Calibrated plane scale to match ghost structure
- Fine-tuned subdivision levels for optimal performance

### Collision Settings
- Enabled collisions for:
  - Sphere (head)
  - Cylinders (arms)
  - Ground plane
- Adjusted collision bounds for accurate physics simulation

## Animating Textures & Geometry

### Parenting Objects
- Sphere set as parent to cylinders for unified movement
- Cloth parented to sphere for synchronized animation
- Established proper hierarchy for smooth animation flow

### Animation
- Animated sphere movement:
  - Primary motion along X-axis
  - Secondary rotation on Z-axis
- Created wind-hovering effect
- Normalized trajectory curves for smooth motion

## Camera Setting & Rendering

### Lighting
- Positioned point light between cylinders
- Parented light to sphere for dynamic illumination
- Applied glow effects to cloth material
- Created atmospheric lighting for spooky ambiance

### Camera Positioning
- Optimized camera angle for ghost visualization
- Configured dim, eerie lighting setup
- Established proper framing for animation sequence

### Rendering
- Render engine: Blender Cycles
- Configured settings for:
  - Realistic lighting
  - Shadow quality
  - Material properties
- Optimized render settings for quality and performance

> **HDR Note:** The scene uses an HDR environment map for ambient lighting. A free HDR can be downloaded from [Poly Haven](https://polyhaven.com/hdris). Download any HDR of your choice, save it locally, and load it in Blender under *World Properties > Surface > Environment Texture*.

## Screenshots

### Ghost Structure Setup
![Ghost Structure Setup](https://github.com/user-attachments/assets/f24b0b42-a2a1-4c83-b953-2aeab17ff111)

### Cloth Simulation in Action
![Cloth Simulation in Action](https://github.com/user-attachments/assets/5fbfbc77-3287-4751-ae6c-837b8b54681b)

### Final Rendered Ghost
![Final Rendered Ghost](https://github.com/user-attachments/assets/6722dbfd-e5d4-4975-ac3e-178c4c9367b8)

## Project Files

The project includes:
- Blender source file (.blend) compiled in .tar.xz to reduce the size
- Texture assets
- Animation keyframes
- Render settings configuration

## Requirements

- Blender 3.0 or higher (developed with Blender 4.2.2 LTS)
- Minimum 8GB RAM recommended
- Graphics card with OpenGL 4.0 support

## Usage

1. Download and extract `Ghost.tar.xz`
2. Open the `.blend` file in Blender
3. Adjust cloth simulation parameters if needed
4. Modify animation keyframes as desired
5. Load an HDR environment texture (see [HDR Note](#rendering) above)
6. Configure render settings and export the final animation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Special thanks to:
- Computer Animation & Modeling course instructors
- Blender community for cloth physics documentation
- Fellow students for feedback and suggestions
