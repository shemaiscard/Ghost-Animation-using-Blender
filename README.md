# Ghost Animation Using Cloth Physics in Blender

A computer animation project demonstrating the creation of a ghost animation using cloth physics simulation in Blender. This project was developed as part of a Computer Animation & Modeling final project.

## Table of Contents
- [Introduction](#introduction)
- [Setup](#setup)
- [Cloth Simulation Basics](#cloth-simulation-basics)
- [Animating Textures & Geometry](#animating-textures--geometry)
- [Camera Setting & Rendering](#camera-setting--rendering)
- [Screenshots](#screenshots)

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
- Utilized Blender Cycles render engine
- Configured settings for:
  - Realistic lighting
  - Shadow quality
  - Material properties
- Optimized render settings for quality and performance

## Screenshots

### Ghost Structure Setup
[Screenshot placeholder: Initial ghost structure setup]

### Cloth Simulation in Action
[Screenshot placeholder: Cloth simulation progress]

### Final Rendered Ghost
[Screenshot placeholder: Final rendered result]

### Animation Frames
[Screenshot placeholder: Key animation frames]

## Project Files

The project includes:
- Blender source file (.blend)
- Texture assets
- Animation keyframes
- Render settings configuration

## Requirements

- Blender 3.0 or higher( I used 4.2.2 LTS)
- Minimum 8GB RAM recommended
- Graphics card with OpenGL 4.0 support

## Usage

1. Open the .blend file in Blender
2. Adjust cloth simulation parameters if needed
3. Modify animation keyframes as desired
4. Configure render settings
5. Export final animation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Special thanks to:
- Computer Animation & Modeling course instructors
- Blender community for cloth physics documentation
- Fellow students for feedback and suggestions
