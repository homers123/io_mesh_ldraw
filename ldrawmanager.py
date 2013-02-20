'''
Created on 06.12.2011

@author: Daniel Toplak
'''

import os
import io
import sys
import math
import re
import traceback

import bpy
import mathutils
from mathutils import Vector
from bpy_extras.io_utils import unpack_list, unpack_face_list


class LdrawManager:
    def __init__(self, context):
        self._ldrawLibraryPath = context.scene['ldrawtools_librarypath']
        self._context = context
        self._scaleFactor = 0.0004
        #self._scaleFactor = 1.0
        
        # store the blender objects in a dictonary
        #self._blObjects = {}
        # store the blender meshes in a dictonary
        #self._blMeshes = {}
        
        self._vertexlist = []
        self._facelist = []
        
        self._partnames = []
        self._regex = re.compile("\[([0-9a-zA-Z]+)\]$")
                
    def _findFile(self, datfile):
        if sys.platform == 'win32':
            datfile = datfile.replace('/', '\\')
        else:
            datfile = datfile.replace('\\', '/')
        # ensure we have only the filename
        datfile = os.path.basename(datfile)
        # and it is lowercase
        datfile = datfile.lower()
        
        # high res over low res
        #searchpaths = ['parts', 'p/48', 'p', 'parts/s']
        # low res over high res 
        searchpaths = ['parts', 'p', 'p/48', 'parts/s']
        
        for searchpath in searchpaths:
            complete_path = os.path.join(self._ldrawLibraryPath, searchpath, datfile)
            if os.path.exists(complete_path):
                return complete_path        
        
        return ''
    
    def _isPartFile(self, datfile):
        # ensure we have only the filename
        datfile = os.path.basename(datfile)
        
        # check if exists in the part directory
        if os.path.exists(os.path.join(self._ldrawLibraryPath, 'parts', datfile)):
            return True
        return False
    
    def _getDatName(self, datfile):
        # ensure we have only the filename
        datfile = os.path.basename(datfile)
        splitext = os.path.splitext(datfile)
        return splitext[0]
    
    def _getOrCreateVertex(self, vertexarray, vertex):
        
        counter = len(vertexarray)
        '''
        counter = 0
        for vert in vertexarray:
            if vert == vertex:
                return counter
            counter += 1
        '''    
        vertexarray.append(vertex)
        
        return counter   
    
    def _parseFile(self, datfile, mat = mathutils.Matrix()):
        try:
            fh = open(datfile, 'r')
        except:
            tb = traceback.format_exc()
            print(tb)
             
        lines = fh.readlines()
        counter = 0
        for line in lines:
            # strip whitespaces
            line = line.strip()         
            
            if len(line) == 0:
                continue   # skip empty lines
            
            pos = line.find(' ') # search first space
            if pos == -1:
                continue 
            linetype = int(line[0:pos])
            linedata = line[pos+1:]
            
            if linetype == 0:    # Comment or META Command
                items = linedata.split()
                if counter == 0: # first line
                    # check if string is longer then 50 chars
                    partname = linedata;
                    if len(partname) > 50:
                        partname = partname[0:49]
                    self._partnames.append(partname)
                pass
            
            elif linetype == 1:  # Sub-file reference  
                items = linedata.split()              
                submat = mathutils.Matrix()
                x = float(items[ 1])
                y = float(items[ 2])
                z = float(items[ 3])
                a = float(items[ 4])
                b = float(items[ 5])
                c = float(items[ 6])
                d = float(items[ 7])
                e = float(items[ 8])
                f = float(items[ 9])
                g = float(items[10])
                h = float(items[11])
                i = float(items[12])
                subfile = items[13]
                '''
                submat[0] = [a, b, c, x]
                submat[1] = [d, e, f, y]
                submat[2] = [g, h, i, z]
                submat[3] = [0.0, 0.0, 0.0, 1.0]
                '''
                submat[0] = [a, d, g, 0.0]
                submat[1] = [b, e, h, 0.0]
                submat[2] = [c, f, i, 0.0]
                submat[3] = [x, y, z, 1.0]
                
                print('subfile: ' + subfile)
                self._parseFile(self._findFile(subfile), submat * mat)
                #verts.extend(subverts)
                #faces.extend(subfaces)
            
            elif linetype == 2:  # Line  
                pass
            
            elif linetype == 3:  # Triangle
                items = linedata.split()
                v1 = mathutils.Vector( (float(items[ 1]), float(items[ 2]), float(items[ 3])) )
                v2 = mathutils.Vector( (float(items[ 4]), float(items[ 5]), float(items[ 6])) )
                v3 = mathutils.Vector( (float(items[ 7]), float(items[ 8]), float(items[ 9])) )                
                
                if mat != mathutils.Matrix():
                    v1 = v1 * mat
                    v2 = v2 * mat
                    v3 = v3 * mat              
                
                v1ID = self._getOrCreateVertex(self._vertexlist, v1[:])
                v2ID = self._getOrCreateVertex(self._vertexlist, v2[:])
                v3ID = self._getOrCreateVertex(self._vertexlist, v3[:])                                           
                self._facelist.append( (v1ID, v2ID, v3ID) )
            
            elif linetype == 4:  # Quad
                items = linedata.split()
                v1 = mathutils.Vector( (float(items[ 1]), float(items[ 2]), float(items[ 3])) )
                v2 = mathutils.Vector( (float(items[ 4]), float(items[ 5]), float(items[ 6])) )
                v3 = mathutils.Vector( (float(items[ 7]), float(items[ 8]), float(items[ 9])) )
                v4 = mathutils.Vector( (float(items[10]), float(items[11]), float(items[12])) )
                
                if mat != mathutils.Matrix():
                    v1 = v1 * mat
                    v2 = v2 * mat
                    v3 = v3 * mat
                    v4 = v4 * mat
                
                v1ID = self._getOrCreateVertex(self._vertexlist, v1[:])
                v2ID = self._getOrCreateVertex(self._vertexlist, v2[:])
                v3ID = self._getOrCreateVertex(self._vertexlist, v3[:])               
                v4ID = self._getOrCreateVertex(self._vertexlist, v4[:])
                self._facelist.append( (v1ID, v2ID, v3ID, v4ID) )
                             
                
            elif linetype == 5:  # Optional Line
                pass
            
            
            counter += 1
        fh.close()
        #return verts, faces
        
    def replace(self, objName):
        print('replace: ' + objName)
        objObject = bpy.data.objects.get(objName)
        if objObject == None:
            return # not found
        
        # name of object looks like: 'Brick 2x 2 [3003]
        # we must parse out the number of the datfile (3003) in this case
        r = self._regex.search(objName)
        if r == None:
            return # the objName is invalid
        
        ldraw_id = r.group(1)
        
        # set 3d cursor to obj location
        bpy.context.scene.cursor_location = objObject.location
        
        # remove object and mesh
        self._context.scene.objects.unlink(objObject)
        bpy.data.objects.remove(objObject)
        objMesh = bpy.data.meshes[objName]
        objMesh.user_clear()
        bpy.data.meshes.remove(objMesh)
        
        # load new object
        self.load(ldraw_id)
        
            
    def load(self, ldraw_part_id):
        print('load: ' + ldraw_part_id)
        # clear
        self._vertexlist = []
        self._facelist = []        
        self._partnames = []
        
        # deselect all
        if bpy.ops.object.select_all.poll():
            bpy.ops.object.select_all(action='DESELECT')
        
        filename = ldraw_part_id + '.dat'
        
        # get the current scene
        scene = self._context.scene
        
        # get the absolute file path of path if it is empty, then it must be 
        # an external model or something
        abs_path = self._findFile(filename)
        #'''
        if abs_path != '':
        
            # if it is a part file then add part/object
            # else 
            if self._isPartFile(filename):
                #now parse the file
                self._parseFile(abs_path)
                
                # create a blender object and its mesh 
                # with the name
                objName = self._partnames[0] + ' [' + self._getDatName(filename) + ']'
                
                # check if object already exists                
                objObject = bpy.data.objects.get(objName)
                if objObject != None:
                    return #already exists
                
                
                
                objMesh = bpy.data.meshes.new(objName)
                objObject = bpy.data.objects.new(objName, objMesh)     
                # link to scene
                scene.objects.link(objObject)           
                
                # place object on to 3d cursor postion
                objObject.location = bpy.context.scene.cursor_location.copy()
                
                ''' special properties '''
                objObject.data.luxrender_mesh.instancing_mode = 'always'
                #objMesh.show_double_sided = False
                
                
                
                objMesh.from_pydata(self._vertexlist, [], self._facelist)
                
                
                objMesh.validate()
                objMesh.update()     
                
                
                
                
                #select our created objec
                objObject.select = True
                bpy.context.scene.objects.active = objObject
                
                # add and apply remesh modifier
                #bpy.ops.object.modifier_add(type='REMESH')
                #bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Remesh")
                
                
                objMesh.validate()
                objMesh.update()
                
                # go into edit mode
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
                
                # select all in mesh
                bpy.ops.mesh.select_all(action='SELECT')
                    
                # remove doubles                    
                bpy.ops.mesh.remove_doubles(threshold=0.1)
                # recalc normals
                bpy.ops.mesh.normals_make_consistent()
                # make smooth
                bpy.ops.mesh.faces_shade_smooth()
                
                
                # go back into object mode
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=True)
                
                
                # add bevel operator
                
                bpy.ops.object.modifier_add(type='BEVEL')
                bevel_mod = objObject.modifiers['Bevel']
                bevel_mod.limit_method = 'ANGLE'
                bevel_mod.width = 0.00005
                
                
                # add edge split modifier
                bpy.ops.object.modifier_add(type='EDGE_SPLIT')
                
                
                #scale down and fix coordinate system
                #objMatrix = objObject.matrix_local
                scaleMatrix = mathutils.Matrix.Scale(self._scaleFactor, 4)
                
                # fix object rotation
                # rotate x -90° and then apply rotation
                rotationMatrix = mathutils.Matrix.Rotation(math.radians(-90), 4, 'X')                
                
                #objObject.matrix_local = scaleMatrix * objMatrix
                objMesh.transform(rotationMatrix * scaleMatrix)
                
                
                objMesh.validate()
                objMesh.update()
                
                # settings for the grid, to get snap to grid working
                for a in bpy.context.screen.areas:
                    if a.type == 'VIEW_3D':
                        bpy.types.SpaceView3D(a.spaces[0]).grid_lines = 800
                        bpy.types.SpaceView3D(a.spaces[0]).grid_scale = 0.160
                
                bpy.context.tool_settings.snap_element = 'INCREMENT'
                bpy.context.tool_settings.use_snap = True
                         
            else:
                pass
            
        else: # handle an external model or multipart file
            pass
        
        
        ''' testing to add a object to the scene '''
        '''
        # create a mesh
        mesh = bpy.data.meshes.new('myMesh')
        vertices = [ (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1), (0,0,1) ]
        edges    = [ (3,2), (2,1), (1,0), (0,3), (0,4), (1,4), (2,4), (3,4) ]
        faces    = [ (3,2,1,0), (0,1,4), (1,2,4), (2,3,4), (3,0,4) ]
        #faces    = []
        
        mesh.from_pydata(vertices, [], faces)
        
        #mesh.vertices.add(len(vertices))
        #mesh.vertices.foreach_set        
        #mesh.faces.add(len(faces))
        
        mesh.validate()
        mesh.update()
        # create a object
        obj = bpy.data.objects.new('myObj', mesh)
        
        # link to scene
        scene.objects.link(obj)
        '''
        
        # update the scene
        scene.update()
