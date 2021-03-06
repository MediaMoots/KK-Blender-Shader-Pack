'''
IMPORT TEXTURES SCRIPT
- Loads in the textures received from Grey's Mesh Exporter
Usage:
- Click the button and choose the folder that contains the textures
'''

import bpy
import os
from pathlib import Path

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

class import_Textures(bpy.types.Operator):
    bl_idname = "kkb.importtextures"
    bl_label = "Import textures folder"
    bl_description = "Open the folder containing all the textures"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory = StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob = StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):
        print('Getting textures from: ' + self.directory)
        fileList = Path(self.directory).glob('*.*')
        files = [file for file in fileList if file.is_file()]
        
        for image in files:
            bpy.ops.image.open(filepath=str(image))
            bpy.data.images[image.name].pack()
        
            #Add all textures to the correct places in the body template
        currentObj = bpy.data.objects['Body']
        def imageLoad(mat, group, node, image, raw = False):
            try:
                currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image]
                if raw:
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image.colorspace_settings.name = 'Raw'
            except:
                print('File not found, skipping: ' + image)
            
        imageLoad('Template Body', 'BodyTextures', 'BodyMC', 'cf_body_00_mc-RGB24.tga', True)
        imageLoad('Template Body', 'BodyTextures', 'BodyMD', 'cf_m_body_DetailMask.png', True)
        imageLoad('Template Body', 'BodyTextures', 'BodyLine', 'cf_m_body_LineMask.png', True)
        #imageLoad('BodyOptional', '')
        
        imageLoad('Template Body', 'NippleTextures', 'NipR', 'cf_m_body_overtex1.png')
        imageLoad('Template Body', 'NippleTextures', 'NipL', 'cf_m_body_overtex1.png')
        
        currentObj.material_slots['Template Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].node_tree.nodes['AlphaBody'].image = bpy.data.images['cf_m_body_AlphaMask.png']
        
        imageLoad('Template Face', 'FaceTextures', 'FaceMC', 'cf_face_00_mc-BC7.dds', True)
        imageLoad('Template Face', 'FaceTextures', 'FaceMD', 'cf_m_face_00_DetailMask.png', True)
        imageLoad('Template Face', 'FaceTextures', 'BlushMask', 'cf_m_face_00_overtex2.png')
        
        imageLoad('Template Eyebrows (mayuge)', 'BrowTextures', 'Eyebrow', 'cf_m_mayuge_00_MainTex.png')
        imageLoad('Template Nose', 'Nose', 'Nose', 'cf_m_noseline_00_MainTex.png')
        imageLoad('Template Teeth (tooth)', 'Teeth', 'Teeth', 'cf_m_tooth_MainTex.png')
        imageLoad('Template Eyewhites (sirome)', 'EyewhiteTex', 'Eyewhite', 'cf_m_sirome_00_MainTex.png')
        
        imageLoad('Template Eyeline up', 'Eyeline', 'EyelineUp', 'cf_m_eyeline_00_up_MainTex.png')
        imageLoad('Template Eyeline up', 'Eyeline', 'EyelineDown', 'cf_m_eyeline_down_MainTex.png')
        
        imageLoad('Template Eye (hitomi)', 'EyeTex', 'eyeAlpha', 'cf_m_hitomi_00_MainTex.png')
        imageLoad('Template Eye (hitomi)', 'EyeTex', 'EyeHU', 'cf_m_hitomi_00_overtex1.png')
        imageLoad('Template Eye (hitomi)', 'EyeTex', 'EyeHD', 'cf_m_hitomi_00_overtex2.png')
        #imageLoad('Template Eye (hitomi)', 'EyeTex', 'eyeAlpha', 'cf_m_hitomi_00_MainTex.png')
        #imageLoad('Template Eye (hitomi)', 'EyeTex', 'eyeAlpha', 'cf_m_hitomi_00_MainTex.png')
        
        imageLoad('Template Tongue', 'Gentex', 'Maintex', 'cf_m_tang_ColorMask.png') #done on purpose
        imageLoad('Template Tongue', 'Gentex', 'MainCol', 'cf_m_tang_ColorMask.png')
        imageLoad('Template Tongue', 'Gentex', 'MainDet', 'cf_m_tang_DetailMask.png')
        imageLoad('Template Tongue', 'Gentex', 'MainNorm', 'cf_m_tang_NormalMap.png')
        
        ##################################
        
        #for each material slot in the hair object, load in the hair detail mask, colormask
        currentObj = bpy.data.objects['Hair']
        
        for hairMat in currentObj.material_slots:
            hairType = hairMat.name.replace('Template ','')
            
            #make a copy of the node group, use it to replace the current node group and rename it so each piece of hair has it's own unique hair texture group
            newNode = hairMat.material.node_tree.nodes['HairTextures'].node_tree.copy()
            hairMat.material.node_tree.nodes['HairTextures'].node_tree = newNode
            newNode.name = hairType + ' Textures'
            
            imageLoad(hairMat.name, 'HairTextures', 'hairDetail', hairType+'_DetailMask.png')
            imageLoad(hairMat.name, 'HairTextures', 'hairFade', hairType+'_ColorMask.png')
            imageLoad(hairMat.name, 'HairTextures', 'hairShine', hairType+'_HairGloss.png')
        
        
        ##################################
        
        
        # Loop through each material in the general object and load the textures, if any, into unique node groups
        # also make unique shader node groups so all materials are unique
        
        # make a copy of the node group, use it to replace the current node group
        for object in bpy.context.view_layer.objects:
            if  object.type == 'MESH' and object.name != 'Hair' and object.name != 'Body':
                
                currentObj = object
                
                for genMat in currentObj.material_slots:
                    genType = genMat.name.replace('Template ','')
                    
                    #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique texture group
                    newNode = genMat.material.node_tree.nodes['Gentex'].node_tree.copy()
                    genMat.material.node_tree.nodes['Gentex'].node_tree = newNode
                    newNode.name = genType + ' Textures'
                    
                    imageLoad(genMat.name, 'Gentex', 'Maintex', genType+'_MainTex.png', True)
                    imageLoad(genMat.name, 'Gentex', 'MainCol', genType+'_ColorMask.png', True)
                    imageLoad(genMat.name, 'Gentex', 'MainDet', genType+'_DetailMask.png', True)
                    imageLoad(genMat.name, 'Gentex', 'MainNorm', genType+'_NormalMap.png', True)
                    
                    MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                    #ColorImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['MainCol'].image
                         
                    #Also, make a copy of the General shader node group, as it's unlikely everything using it will be the same color
                    newNode = genMat.material.node_tree.nodes['KKShader'].node_tree.copy()
                    genMat.material.node_tree.nodes['KKShader'].node_tree = newNode
                    newNode.name = genType + ' Shader'
                    
                    #If no main image was loaded in, there's no alpha channel being fed into the KK Shader.
                    #Unlink the input node and make the alpha channel pure white
                    if  MainImage == None:
                        getOut = genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['GeneralOut'].inputs['Alpha'].links[0]
                        genMat.material.node_tree.nodes['KKShader'].node_tree.links.remove(getOut)
                        
                        genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['GeneralOut'].inputs['Alpha'].default_value = 1        
        
        #Add body outline and load in the clothes transparency mask
        ob = bpy.context.view_layer.objects['Body']
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        mod = ob.modifiers[3]
        mod.thickness = 0.003
        mod.offset = 0
        mod.material_offset = 100
        mod.use_flip_normals = True
        mod.use_rim = False
        ob.data.materials.append(bpy.data.materials['Template Body Outline'])
        bpy.data.materials['Template Body Outline'].node_tree.nodes['BodyMask'].image = bpy.data.images['cf_m_body_AlphaMask.png']
                
        #Give the hair a unique outline group
        ob = bpy.context.view_layer.objects['Hair']
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        mod = ob.modifiers[1]
        mod.thickness = 0.003
        mod.offset = 0
        mod.material_offset = 100
        mod.use_flip_normals = True
        hairOutlineMat = bpy.data.materials['Template Outline'].copy()
        hairOutlineMat.name = 'Hair Outline'
        ob.data.materials.append(hairOutlineMat)
         
        #Add a standard outline to all other objects
        for ob in bpy.context.view_layer.objects:
            if  ob.type == 'MESH' and ob.name != 'Body' and ob.name != 'Hair' and 'Widget' not in ob.name:
                bpy.context.view_layer.objects.active = ob
                bpy.ops.object.modifier_add(type='SOLIDIFY')
                mod = ob.modifiers[1]
                mod.thickness = 0.003
                mod.offset = 0
                mod.material_offset = 100
                mod.use_flip_normals = True
                ob.data.materials.append(bpy.data.materials['Template Outline'])
                    
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
