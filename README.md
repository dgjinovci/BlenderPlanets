# BlenderPlanets

This plugin generates IcoSphere based mesh and evaluates gradient from [hetero terrain noise](https://docs.blender.org/api/current/mathutils.noise.html#mathutils.noise.hetero_terrain "hetero terrain noise")

After installing, You can find the panel in Right Sidebar (default shortcut key N):

![Panel](img/panel.png?raw=true "Panel")

By switching in "Viewport Shading" the result will be as shown:
![Panel](img/planet.png?raw=true "Planet")


## Shader
Plugin also generates a default shader

Alpha of VertexColor node is the gradient of elevation (0, 1). You can use this value to apply shader nodes. 

Example of default shader uses a RampColor fed with VertexColor Alpha value as Fac:  
![Panel](img/shader.png?raw=true "Shader")
