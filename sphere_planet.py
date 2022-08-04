bl_info = {
    "name": "Planet Generation",
    "blender": (2, 93, 10),
    "category": "Object",
    "author": "Dardan Gjinovci",
    "version": (1, 0),
    "doc_url": "https://github.com/dgjinovci/BlenderPlanets/blob/main/README.md"
}


import bpy
import bmesh
from math import *
from mathutils import *
from random import uniform

import asyncio
loop = asyncio.get_event_loop()


class PLANET_OT_options(bpy.types.Operator):
    bl_idname = "planet.options"
    bl_label = "Create"
    #bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        
        props = context.scene.planet_props
        self.generate('Planet', props.radius, props.resolution, props.height_scale, props.roughness\
        , props.lacunarity, props.octaves, props.height_offset, props.seed)
        #loop.run_until_complete(self.massive_work(props))
 
        return {'FINISHED'}
    
    #async def massive_work(self, props):
    #    self.generate('Planet', props.radius, props.resolution, props.height_scale)
    
        
    def generate(self, NAME, RADIUS, RESOLUTION, NOISE_HEIGHT_SCALE, ROUGHNESS, LACUNARITY,\
     OCTAVES, HEIGHT_OFFSET, SEED):

        mesh = bpy.data.objects.get(NAME)
        if mesh:
            bpy.data.objects.remove(mesh)
            
        material = bpy.data.materials.get("PlanetMaterial")
        if not material:
            material = bpy.data.materials.new("PlanetMaterial")
            
        material.use_nodes = True
        principledBSDF = material.node_tree.nodes.get('Principled BSDF')


        vt_color = material.node_tree.nodes.get('vertex_color')
        color_ramp = material.node_tree.nodes.get('color_ramp')

        if not vt_color:
            vt_color = material.node_tree.nodes.new('ShaderNodeVertexColor')
            vt_color.name='vertex_color'
            vt_color.location = (-500, 320)
            
        
        if not color_ramp:
            color_ramp = material.node_tree.nodes.new('ShaderNodeValToRGB')
            color_ramp.name='color_ramp'
            color_ramp.location = (-300, 220)
            clen = len(color_ramp.color_ramp.elements)
            if clen > 1:
                color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[clen-1])
                
            color_ramp.color_ramp.elements.new(position=0.7)
            color_ramp.color_ramp.elements.new(position=1.0)
            color_ramp.color_ramp.elements[0].position=0.3
            color_ramp.color_ramp.elements[0].color=(0,0,1,1)
            color_ramp.color_ramp.elements[1].color=(0.5,0.3,0,1)
            color_ramp.color_ramp.elements[2].color=(0,1,0,1)
          
               
        material.node_tree.links.new(vt_color.outputs[1], color_ramp.inputs[0])
        material.node_tree.links.new(color_ramp.outputs[0], principledBSDF.inputs["Base Color"])


        new_mesh = bpy.data.meshes.new('new_mesh')
        new_object = bpy.data.objects.new(NAME, new_mesh)
        bpy.context.view_layer.active_layer_collection.collection.objects.link(new_object)
        new_object.data.materials.append(material)
        #new_mesh.select = True 











        # make mesh
        vertices = []
        vertex_colors = []
        edges = []
        faces = []


        t = (1.0 + sqrt(5.0)) / 2.0 

        # Y axis. Z normal up plane
        vertices.append(Vector((-1, t, 0)))
        vertices.append(Vector((1, t, 0)))
        vertices.append(Vector((-1, -t, 0)))
        vertices.append(Vector((1, -t, 0)))

        # Z axis, X normal up plane
        vertices.append(Vector((0, -1, t)))
        vertices.append(Vector((0, 1, t)))
        vertices.append(Vector((0, -1, -t)))
        vertices.append(Vector((0, 1, -t)))

        # X axis, Y normal up plane
        vertices.append(Vector((t, 0, -1)))
        vertices.append(Vector((t, 0, 1)))
        vertices.append(Vector((-t, 0, -1)))
        vertices.append(Vector((-t, 0, 1)))


        # from point 0
        faces.append((0, 11, 5))
        faces.append((0, 5, 1))
        faces.append((0, 1, 7))
        faces.append((0, 7, 10))
        faces.append((0, 10, 11))

        # 5 adjacent faces
        faces.append((1, 5, 9))
        faces.append((5, 11, 4))
        faces.append((11, 10, 2))
        faces.append((10, 7, 6))
        faces.append((7, 1, 8))

        # from point 3
        faces.append((3, 9, 4))
        faces.append((3, 4, 2))
        faces.append((3, 2, 6))
        faces.append((3, 6, 8))
        faces.append((3, 8, 9))

        # 5 adjacent faces
        faces.append((4, 9, 5))
        faces.append((2, 4, 11))
        faces.append((6, 2, 10))
        faces.append((8, 6, 7))
        faces.append((9, 8, 1))





        cache_mid_point = dict()

        def get_mid_point(ia, ib):
            
            a,b = (ia,ib) if ia<ib else (ib,ia)
            i = (a<<32)+b 
            
            if i in cache_mid_point:
                return cache_mid_point[i] # return cached vert_index
            
            va = vertices[ia]
            vb = vertices[ib]
                
            x = (va.x + vb.x) / 2.0
            y = (va.y + vb.y) / 2.0    
            z = (va.z + vb.z) / 2.0    
            
            vert = Vector((x,y,z))
            
            # add new to verts and chache
            vert_index = len(vertices) 
            vertices.append(vert)
            cache_mid_point[i] = vert_index 
            
            return vert_index



        for i in range(RESOLUTION):
            lod_faces = []
            for face in faces:
                
                
        #        bpy.ops.mesh.primitive_cone_add(
        #        depth=1, 
        #        location=mid,
        #        scale=(0.05, 0.05, 0.05),
        #        rotation=(0,radians(-90),0)
        #        )
              
                ia = get_mid_point(face[0], face[1])
                ib = get_mid_point(face[1], face[2])
                ic = get_mid_point(face[2], face[0])
                
                lod_faces.append((face[0], ia, ic))   
                lod_faces.append((face[1], ib, ia))   
                lod_faces.append((face[2], ic, ib))
                lod_faces.append((ia, ib, ic))       
                
            faces = lod_faces
            


        print("Vertices:", len(vertices), " Faces:", len(faces))



        bm = bmesh.new()

        # noise Parameters
        # position (mathutils.Vector) – The position to evaluate the selected noise function.
        # H (float) – The fractal dimension of the roughest areas.
        # lacunarity (float) – The gap between successive frequencies.
        # octaves (int) – The number of different noise frequencies used.
        # offset (float) – The height of the terrain above ‘sea level’.
        # gain (float) – Scaling applied to the values.
        # noise_basis (string) – Enumerator in [‘BLENDER’, ‘PERLIN_ORIGINAL’, ‘PERLIN_NEW’, ‘VORONOI_F1’, ‘VORONOI_F2’, ‘VORONOI_F3’, ‘VORONOI_F4’, ‘VORONOI_F2F1’, ‘VORONOI_CRACKLE’, ‘CELLNOISE’].


        bmverts=[]
        elevations=dict()
        for i in range(len(vertices)): 
            v = vertices[i].normalized() * RADIUS
            v = v.normalized()
            seedv = Vector((1, 0, 0)) * SEED
            elev = noise.hetero_terrain(v + seedv, ROUGHNESS, LACUNARITY, OCTAVES, HEIGHT_OFFSET) #, 2.4)
            v = v * (RADIUS * (elev * NOISE_HEIGHT_SCALE) + RADIUS)
            bv = bm.verts.new(v)
            bmverts.append(bv)
            
            #elev = elev * 0.5 + 0.5
            elevations[bv] = elev
            
            
        color_layer = bm.loops.layers.color.new("color")
        uv_layer = bm.loops.layers.uv.new("uv0")
 
 
        PI = 3.14159
        idx = 0
        for f in faces:
            v1 = bmverts[f[0]]
            v2 = bmverts[f[1]]
            v3 = bmverts[f[2]]
            face = bm.faces.new([v1, v2, v3])
            face.smooth = True
            
            for loop in face.loops:
                # vertex color mapping. Alpha represents elevation
                e = elevations[loop.vert]
                loop[color_layer] = ((e, e, e, e))
                
                # UV mapping equilinear 
                n = loop.vert.co.normalized()
                u = atan2(n.y, n.x) / (PI * 2) + 0.5;
                v = acos(n.z) / PI;
                loop[uv_layer].uv = (u, v)
               
        
       
        bm.to_mesh(new_mesh)  
        new_mesh.update()
        bm.free()

        bpy.data.objects[NAME].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[NAME]


    # make collection
    #new_collection = bpy.data.collections.new('new_collection')
    #bpy.context.scene.collection.children.link(new_collection)
    # add object to scene collection
    #new_collection.objects.link(new_object)






    

class PlanetProps(bpy.types.PropertyGroup):
    radius: bpy.props.FloatProperty(name='Radius', default=2)
    resolution: bpy.props.IntProperty(name='Resolution', default=5)
    height_scale: bpy.props.FloatProperty(name='Height Scale', default=0.02)
    roughness: bpy.props.FloatProperty(name='Roughness', default=0.46)
    lacunarity: bpy.props.FloatProperty(name='Lacunarity', default=3.0)
    octaves: bpy.props.IntProperty(name='Octaves', default=7)
    height_offset: bpy.props.FloatProperty(name='Height Offset', default=0.1)
    seed: bpy.props.IntProperty(name='Seed', default=6)
    
    
class PLANET_PT_main_panel(bpy.types.Panel):
    bl_label = "Planet Panel"
    bl_idname = "PLANET_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Planet"

    def draw(self, context):
        layout = self.layout
        
        props = context.scene.planet_props
        
        #props.radius = 1
        #props.resolution = 2
        #props.height_scale = 0.04
        
        layout.prop(props, "radius")
        layout.prop(props, "resolution")
        layout.prop(props, "height_scale")
        layout.prop(props, "roughness")
        layout.prop(props, "lacunarity")
        layout.prop(props, "octaves")
        layout.prop(props, "height_offset")
        layout.prop(props, "seed")
        layout.operator("planet.options")



def register():
    bpy.utils.register_class(PlanetProps)
    bpy.utils.register_class(PLANET_OT_options)
    bpy.utils.register_class(PLANET_PT_main_panel)
    bpy.types.Scene.planet_props = bpy.props.PointerProperty(type=PlanetProps)

def unregister():
    bpy.utils.unregister_class(PlanetProps)
    bpy.utils.unregister_class(PLANET_OT_options)
    bpy.utils.unregister_class(PLANET_PT_main_panel)
    del bpy.types.Scene.planet_props
    
 
if __name__ == "__main__":
    register()