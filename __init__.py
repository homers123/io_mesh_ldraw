'''
Created on 05.12.2011

@author: Daniel Toplak
'''

'''
@todo: make the meshes non manifold
@todo: put the lego letters on the stud (f.e. displacement)
@todo: part replacement
@todo: material handling
'''

bl_info = {
    "name": "Ldraw format",
    "description": "Load Ldraw format",
    "author": "Daniel Toplak",
    "version": (1,0),
    "blender": (2, 5, 9),
    "api": 42438,
    "location": "File > Import-Export > Ldraw",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}


import os
import sys


''' 
this is for debugging only
please adjust the PYDEV_SOURCE_DIR
'''

'''
# PYDEV_DEBUGGING_BEGIN
#PYDEV_SOURCE_DIR = ''
if sys.platform == 'win32':
    PYDEV_SOURCE_DIR = 'X:\eclipse_4.2\plugins\org.python.pydev_2.7.1.2012100913\pysrc'
else:
    PYDEV_SOURCE_DIR = '/home/daniel/eclipse/plugins/org.python.pydev.debug_2.5.0.2012030114/pysrc'
    
sys.path.append(PYDEV_SOURCE_DIR)
import pydevd
pydevd.settrace(host=None, stdoutToServer=True, stderrToServer=True, port=5678, suspend=False, trace_only_current_thread=True)
# PYDEV_DEBUGGING_END
'''


import bpy
#from bpy_extras.io_utils import ImportHelper
from bpy.props import *
from . import ldrawmanager


def initSceneProperties(scn):
    bpy.types.Scene.ldrawtools_librarypath = StringProperty(name = 'Library path',
                                                            subtype = 'DIR_PATH')
    bpy.types.Scene.ldrawtools_import_part_id = StringProperty(name = 'Import ID')
    scn['ldrawtools_import_part_id'] = ""
    return

initSceneProperties(bpy.context.scene)

class LdrawToolsPanel(bpy.types.Panel):
    bl_idname = "ldrawtools.panel"
    bl_label = "LDraw Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout #Panel layout to draw on
        scn = context.scene
        
        row = layout.row() #Create new row        
        row.prop(scn, 'ldrawtools_librarypath')
        
        row = layout.row() #Create new row
        row.prop(scn, 'ldrawtools_import_part_id')
        row = layout.row() #Create new row
        row.operator('ldrawtools.ldrawpart_import')
        
        row = layout.row() #Create new row
        row.operator('ldrawtools.ldrawpart_replace')
        sel_objs = context.selected_objects
        if len(sel_objs) >= 1:
            row.enabled = True
        else:
            row.enabled = False
        

class ImportLdraw(bpy.types.Operator):
    '''Load Ldraw dat file'''
    bl_idname = "ldrawtools.ldrawpart_import"
    bl_label = "Import"
    bl_description = "Import LDraw part"
    bl_option = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        ldrawMgr = ldrawmanager.LdrawManager(context)
        ldrawMgr.load(context.scene['ldrawtools_import_part_id'])
        context.scene['ldrawtools_import_part_id'] = ""
        return {'FINISHED'}        

class LdrawPartReplace(bpy.types.Operator):
    bl_idname = "ldrawtools.ldrawpart_replace"
    bl_label = "Replace"
    bl_description = "replace the selected ldraw part"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # store the location of current 3d cursor  
        saved_location = bpy.context.scene.cursor_location.copy()  # returns a copy of the vector
        ldrawMgr = ldrawmanager.LdrawManager(context)        
        for obj in context.selected_objects:
            ldrawMgr.replace(obj.name)
        
        # set 3dcursor location back to the stored location  
        bpy.context.scene.cursor_location = saved_location
        return {'FINISHED'}


#def menu_import(self, context):
#    self.layout.operator(ImportLdraw.bl_idname, text="Ldraw (.dat)").filepath = "*.dat"

def register():    
    bpy.utils.register_module(__name__)
    #bpy.types.INFO_MT_file_import.append(menu_import)
    #bpy.utils.register_class(LdrawPartReplace)
    #bpy.utils.register_class(LdrawToolsPanel)


def unregister():    
    bpy.utils.unregister_module(__name__)
    #bpy.types.INFO_MT_file_import.remove(menu_import)
    
if __name__ == "__main__":    
    register()
    
