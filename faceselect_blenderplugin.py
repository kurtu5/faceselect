# Modfied from https://developer.blender.org/T31926

import math
import bpy
import mathutils
from bpy.props import EnumProperty

bl_info = \
    {
        "name" : "Face Selection",
        "author" : "kurtu5",
        "version" : (1, 0, 0),
        "blender" : (2, 70, 0),
        "location" : "Properties > Object data > Face info / select",
        "description" : "Face selection for custom face types",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "support" : "Testing",
        "category" : "Mesh",
    }

smallFaces = []
def selectSmallFaces(ob):
    global smallFaces
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)    
    
    print("selectSmallFaces")
    for face in smallFaces:
        print("Face idx: %i set to selected", face)
        ob.data.polygons[face].select = True
        for vert in ob.data.polygons[face].vertices:
            print("Vert idx: %i set to selected", vert)
            
            ob.data.vertices[vert].select = True
    #context.tool_settings.mesh_select_mode = context.tool_settings.mesh_select_mode
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)


class FaceSelectionPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_category = "Tools"
    bl_label = "Face Selection"

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == 'MESH'


    def draw(self, context):
        TheCol = self.layout.column(align=True)

        ob = context.active_object

        info_str = ""
        info2_str = ""
        global smallFaces
        smallFaces = []
        tris = quads = ngons = tgtsize = 0

        for p in ob.data.polygons:

            if context.scene.face_min_area <= p.area and p.area <= context.scene.face_max_area:
                tgtsize += 1
                smallFaces.append(p.index)
                #print("Indexs of small is %i", (p.index))
                
            count = p.loop_total
            if count == 3:
                tris += 1
            elif count == 4:
                quads += 1
            else:
                ngons += 1

        info_str = "  Ngons: %i Quads: %i Tris: %i Small: %i" % (ngons, quads, tris, tgtsize)

        for s in smallFaces:
            info2_str += ", %i" % (s)


        #TheCol.label("Found smalls at %s" % (info2_str))

        #col = layout.column()
        TheCol.label(info_str, icon='MESH_DATA')
        #bpy.context.scene.face_max_area.step=2
        TheCol.prop(context.scene, "face_min_area")
        TheCol.prop(context.scene, "face_max_area")
        TheCol.prop(context.scene, "face_step_area")
        #col = layout.column()
        TheCol.label("Select faces by type:")

        #row = layout.row()
        TheCol.operator("mesh.face_selection", text="Ngons").face_type = "5"
        TheCol.operator("mesh.face_selection", text="Quads").face_type = "4"
        TheCol.operator("mesh.face_selection", text="Tris").face_type = "3"
        TheCol.operator("mesh.face_selection", text="Smalls").face_type = "6"
      
    #end draw
        scene = context.scene


#end FaceSelectionPanel
class FaceSelectionByType(bpy.types.Operator):
    bl_idname = "mesh.face_selection"
    bl_label = "Face Selection"
    bl_options = {"UNDO"}

    face_type = EnumProperty(
        name="Select faces:",
        items=(("3", "Triangles", "Faces made up of 3 vertices"),
               ("4", "Quads", "Faces made up of 4 vertices"),
               ("5", "Ngons", "Faces made up of 5 and more vertices"),
               ("6", "Smalls", "Faces that are small")),
        default="3")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (False, False, True)

        if self.face_type == "3":
            bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
        elif self.face_type == "4":
            bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
        elif self.face_type == "6":
            selectSmallFaces(context.active_object)
        else:
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
        return {"FINISHED"}
#end FaceSelectionByType


def updateDynamicProperties(scene, context):
    step = float(scene.face_step_area) * 100.0
    print("new step size", step)
    registerDynamicProperties(step)
# end updateDynamicProperties

def registerDynamicProperties(step):
    bpy.types.Scene.face_min_area = bpy.props.FloatProperty \
      (
        name = "Minimum Size",
        description = "Minimun size of face",
        precision = 6,
        step= step,
        min = 0.0,
        default = 0.0
      )
    bpy.types.Scene.face_max_area = bpy.props.FloatProperty \
      (
        name = "Maximum Size",
        description = "Maximum size of face",
        precision = 6,        
        step = step,
        min = 0.0,
        default = 0.01
      )
# end registerDynamicProperties

def registerStaticProperties():
    items=[]
    for item in reversed("10 1 .1 .01 .001 .0001 .00001 .000001".split()):
        items.append((item, item, item))
    bpy.types.Scene.face_step_area = bpy.props.EnumProperty \
      (
        name = "Size Step",
        description = "Size step",
        items = items,        
        update = updateDynamicProperties
      )
# end registerStaticProperties

def register():
    #bpy.utils.register_class(FaceSelection)
    bpy.utils.register_class(FaceSelectionByType)
    bpy.utils.register_class(FaceSelectionPanel)
    registerStaticProperties()
    registerDynamicProperties(0.0001)
#end register

def unregister():
    #bpy.utils.unregister_class(FaceSelection)
    bpy.utils.unregister_class(FaceSelectionByType)
    bpy.utils.unregister_class(FaceSelectionPanel)
    del bpy.types.Scene.face_min_area
    del bpy.types.Scene.face_max_area
    del bpy.types.Scene.face_step_area
#end unregister

if __name__ == "__main__":
    register()
#end if