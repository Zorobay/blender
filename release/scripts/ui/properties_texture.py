# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
import bpy
from rna_prop_ui import PropertyPanel


class TEXTURE_MT_specials(bpy.types.Menu):
    bl_label = "Texture Specials"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        layout.operator("texture.slot_copy", icon='COPYDOWN')
        layout.operator("texture.slot_paste", icon='PASTEDOWN')


class TEXTURE_MT_envmap_specials(bpy.types.Menu):
    bl_label = "Environment Map Specials"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        layout.operator("texture.envmap_save", icon='IMAGEFILE')
        layout.operator("texture.envmap_clear", icon='FILE_REFRESH')
        layout.operator("texture.envmap_clear_all", icon='FILE_REFRESH')

from properties_material import active_node_mat


def context_tex_datablock(context):
    idblock = context.material
    if idblock:
        return active_node_mat(idblock)

    idblock = context.lamp
    if idblock:
        return idblock

    idblock = context.world
    if idblock:
        return idblock

    idblock = context.brush
    return idblock


class TextureButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    @classmethod
    def poll(cls, context):
        tex = context.texture
        return tex and (tex.type != 'NONE' or tex.use_nodes) and (context.scene.render.engine in cls.COMPAT_ENGINES)


class TEXTURE_PT_context_texture(TextureButtonsPanel, bpy.types.Panel):
    bl_label = ""
    bl_show_header = False
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        return ((context.material or context.world or context.lamp or context.brush or context.texture)
            and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        layout = self.layout
        slot = context.texture_slot
        node = context.texture_node
        space = context.space_data
        tex = context.texture
        idblock = context_tex_datablock(context)
        tex_collection = space.pin_id == None and type(idblock) != bpy.types.Brush and not node

        if tex_collection:
            row = layout.row()

            row.template_list(idblock, "texture_slots", idblock, "active_texture_index", rows=2)

            col = row.column(align=True)
            col.operator("texture.slot_move", text="", icon='TRIA_UP').type = 'UP'
            col.operator("texture.slot_move", text="", icon='TRIA_DOWN').type = 'DOWN'
            col.menu("TEXTURE_MT_specials", icon='DOWNARROW_HLT', text="")

        split = layout.split(percentage=0.65)
        col = split.column()

        if tex_collection:
            col.template_ID(idblock, "active_texture", new="texture.new")
        elif node:
            col.template_ID(node, "texture", new="texture.new")
        elif idblock:
            col.template_ID(idblock, "texture", new="texture.new")

        if space.pin_id:
            col.template_ID(space, "pin_id")

        col = split.column()

        if not space.pin_id:
            col.prop(space, "show_brush_texture", text="Brush", toggle=True)

        if tex:
            split = layout.split(percentage=0.2)

            if tex.use_nodes:

                if slot:
                    split.label(text="Output:")
                    split.prop(slot, "output_node", text="")

            else:
                split.label(text="Type:")
                split.prop(tex, "type", text="")


class TEXTURE_PT_preview(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Preview"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        slot = getattr(context, "texture_slot", None)
        idblock = context_tex_datablock(context)

        if idblock:
            layout.template_preview(tex, parent=idblock, slot=slot)
        else:
            layout.template_preview(tex, slot=slot)


class TEXTURE_PT_colors(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Colors"
    bl_default_closed = True
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "use_color_ramp", text="Ramp")
        if tex.use_color_ramp:
            layout.template_color_ramp(tex, "color_ramp", expand=True)

        split = layout.split()

        col = split.column()
        col.label(text="RGB Multiply:")
        sub = col.column(align=True)
        sub.prop(tex, "factor_red", text="R")
        sub.prop(tex, "factor_green", text="G")
        sub.prop(tex, "factor_blue", text="B")

        col = split.column()
        col.label(text="Adjust:")
        col.prop(tex, "intensity")
        col.prop(tex, "contrast")
        col.prop(tex, "saturation")

# Texture Slot Panels #


class TextureSlotPanel(TextureButtonsPanel):
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "texture_slot"):
            return False

        engine = context.scene.render.engine
        return TextureButtonsPanel.poll(self, context) and (engine in cls.COMPAT_ENGINES)


class TEXTURE_PT_mapping(TextureSlotPanel, bpy.types.Panel):
    bl_label = "Mapping"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        idblock = context_tex_datablock(context)
        if type(idblock) == bpy.types.Brush and not context.sculpt_object:
            return False

        if not getattr(context, "texture_slot", None):
            return False

        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        idblock = context_tex_datablock(context)

        tex = context.texture_slot
        # textype = context.texture

        if type(idblock) != bpy.types.Brush:
            split = layout.split(percentage=0.3)
            col = split.column()
            col.label(text="Coordinates:")
            col = split.column()
            col.prop(tex, "texture_coords", text="")

            if tex.texture_coords == 'ORCO':
                """
                ob = context.object
                if ob and ob.type == 'MESH':
                    split = layout.split(percentage=0.3)
                    split.label(text="Mesh:")
                    split.prop(ob.data, "texco_mesh", text="")
                """
            elif tex.texture_coords == 'UV':
                split = layout.split(percentage=0.3)
                split.label(text="Layer:")
                ob = context.object
                if ob and ob.type == 'MESH':
                    split.prop_object(tex, "uv_layer", ob.data, "uv_textures", text="")
                else:
                    split.prop(tex, "uv_layer", text="")

            elif tex.texture_coords == 'OBJECT':
                split = layout.split(percentage=0.3)
                split.label(text="Object:")
                split.prop(tex, "object", text="")

        if type(idblock) == bpy.types.Brush:
            if context.sculpt_object:
                layout.label(text="Brush Mapping:")
                layout.prop(tex, "map_mode", expand=True)

                row = layout.row()
                row.active = tex.map_mode in ('FIXED', 'TILED')
                row.prop(tex, "angle")
        else:
            if type(idblock) == bpy.types.Material:
                split = layout.split(percentage=0.3)
                split.label(text="Projection:")
                split.prop(tex, "mapping", text="")

                split = layout.split()

                col = split.column()
                if tex.texture_coords in ('ORCO', 'UV'):
                    col.prop(tex, "use_from_dupli")
                elif tex.texture_coords == 'OBJECT':
                    col.prop(tex, "use_from_original")
                else:
                    col.label()

                col = split.column()
                row = col.row()
                row.prop(tex, "mapping_x", text="")
                row.prop(tex, "mapping_y", text="")
                row.prop(tex, "mapping_z", text="")

        split = layout.split()

        col = split.column()
        col.prop(tex, "offset")

        col = split.column()

        col.prop(tex, "scale")


class TEXTURE_PT_influence(TextureSlotPanel, bpy.types.Panel):
    bl_label = "Influence"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        idblock = context_tex_datablock(context)
        if type(idblock) == bpy.types.Brush:
            return False

        if not getattr(context, "texture_slot", None):
            return False

        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):

        layout = self.layout

        idblock = context_tex_datablock(context)

        # textype = context.texture
        tex = context.texture_slot

        def factor_but(layout, active, toggle, factor, name):
            row = layout.row(align=True)
            row.prop(tex, toggle, text="")
            sub = row.row()
            sub.active = active
            sub.prop(tex, factor, text=name, slider=True)

        if type(idblock) == bpy.types.Material:
            if idblock.type in ('SURFACE', 'HALO', 'WIRE'):
                split = layout.split()

                col = split.column()
                col.label(text="Diffuse:")
                factor_but(col, tex.use_map_diffuse, "use_map_diffuse", "diffuse_factor", "Intensity")
                factor_but(col, tex.use_map_color_diffuse, "use_map_color_diffuse", "diffuse_color_factor", "Color")
                factor_but(col, tex.use_map_alpha, "use_map_alpha", "alpha_factor", "Alpha")
                factor_but(col, tex.use_map_translucency, "use_map_translucency", "translucency_factor", "Translucency")

                col.label(text="Specular:")
                factor_but(col, tex.use_map_specular, "use_map_specular", "specular_factor", "Intensity")
                factor_but(col, tex.use_map_color_spec, "use_map_color_spec", "specular_color_factor", "Color")
                factor_but(col, tex.use_map_hardness, "use_map_hardness", "hardness_factor", "Hardness")

                col = split.column()
                col.label(text="Shading:")
                factor_but(col, tex.use_map_ambient, "use_map_ambient", "ambient_factor", "Ambient")
                factor_but(col, tex.use_map_emit, "use_map_emit", "emit_factor", "Emit")
                factor_but(col, tex.use_map_mirror, "use_map_mirror", "mirror_factor", "Mirror")
                factor_but(col, tex.use_map_raymir, "use_map_raymir", "raymir_factor", "Ray Mirror")

                col.label(text="Geometry:")
                # XXX replace 'or' when displacement is fixed to not rely on normal influence value.
                factor_but(col, (tex.use_map_normal or tex.use_map_displacement), "use_map_normal", "normal_factor", "Normal")
                factor_but(col, tex.use_map_warp, "use_map_warp", "warp_factor", "Warp")
                factor_but(col, tex.use_map_displacement, "use_map_displacement", "displacement_factor", "Displace")

                #sub = col.column()
                #sub.active = tex.use_map_translucency or tex.map_emit or tex.map_alpha or tex.map_raymir or tex.map_hardness or tex.map_ambient or tex.map_specularity or tex.map_reflection or tex.map_mirror
                #sub.prop(tex, "default_value", text="Amount", slider=True)
            elif idblock.type == 'VOLUME':
                split = layout.split()

                col = split.column()
                factor_but(col, tex.use_map_density, "use_map_density", "density_factor", "Density")
                factor_but(col, tex.use_map_emission, "use_map_emission", "emission_factor", "Emission")
                factor_but(col, tex.use_map_scatter, "use_map_scattering", "scattering_factor", "Scattering")
                factor_but(col, tex.use_map_reflect, "use_map_reflection", "reflection_factor", "Reflection")

                col = split.column()
                col.label(text=" ")
                factor_but(col, tex.use_map_color_emission, "use_map_color_emission", "emission_color_factor", "Emission Color")
                factor_but(col, tex.use_map_color_transmission, "use_map_color_transmission", "transmission_color_factor", "Transmission Color")
                factor_but(col, tex.use_map_color_reflection, "use_map_color_reflection", "reflection_color_factor", "Reflection Color")

        elif type(idblock) == bpy.types.Lamp:
            split = layout.split()

            col = split.column()
            factor_but(col, tex.use_map_color, "map_color", "color_factor", "Color")

            col = split.column()
            factor_but(col, tex.use_map_shadow, "map_shadow", "shadow_factor", "Shadow")

        elif type(idblock) == bpy.types.World:
            split = layout.split()

            col = split.column()
            factor_but(col, tex.use_map_blend, "use_map_blend", "blend_factor", "Blend")
            factor_but(col, tex.use_map_horizon, "use_map_horizon", "horizon_factor", "Horizon")

            col = split.column()
            factor_but(col, tex.use_map_zenith_up, "use_map_zenith_up", "zenith_up_factor", "Zenith Up")
            factor_but(col, tex.use_map_zenith_down, "use_map_zenith_down", "zenith_down_factor", "Zenith Down")

        layout.separator()

        split = layout.split()

        col = split.column()
        col.prop(tex, "blend_type", text="Blend")
        col.prop(tex, "use_rgb_to_intensity")
        sub = col.column()
        sub.active = tex.use_rgb_to_intensity
        sub.prop(tex, "color", text="")

        col = split.column()
        col.prop(tex, "invert", text="Negative")
        col.prop(tex, "use_stencil")

        if type(idblock) in (bpy.types.Material, bpy.types.World):
            col.prop(tex, "default_value", text="DVar", slider=True)

# Texture Type Panels #


class TextureTypePanel(TextureButtonsPanel):

    @classmethod
    def poll(cls, context):
        tex = context.texture
        engine = context.scene.render.engine
        return tex and ((tex.type == cls.tex_type and not tex.use_nodes) and (engine in cls.COMPAT_ENGINES))


class TEXTURE_PT_clouds(TextureTypePanel, bpy.types.Panel):
    bl_label = "Clouds"
    tex_type = 'CLOUDS'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "cloud_type", expand=True)
        layout.label(text="Noise:")
        layout.prop(tex, "noise_type", text="Type", expand=True)
        layout.prop(tex, "noise_basis", text="Basis")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")
        col.prop(tex, "noise_depth", text="Depth")

        col = split.column()
        col.prop(tex, "nabla", text="Nabla")


class TEXTURE_PT_wood(TextureTypePanel, bpy.types.Panel):
    bl_label = "Wood"
    tex_type = 'WOOD'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "noisebasis_2", expand=True)
        layout.prop(tex, "wood_type", expand=True)

        col = layout.column()
        col.active = tex.wood_type in ('RINGNOISE', 'BANDNOISE')
        col.label(text="Noise:")
        col.row().prop(tex, "noise_type", text="Type", expand=True)
        layout.prop(tex, "noise_basis", text="Basis")

        split = layout.split()
        split.active = tex.wood_type in ('RINGNOISE', 'BANDNOISE')

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")
        col.prop(tex, "turbulence")

        col = split.column()
        col.prop(tex, "nabla")


class TEXTURE_PT_marble(TextureTypePanel, bpy.types.Panel):
    bl_label = "Marble"
    tex_type = 'MARBLE'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "marble_type", expand=True)
        layout.prop(tex, "noisebasis_2", expand=True)
        layout.label(text="Noise:")
        layout.prop(tex, "noise_type", text="Type", expand=True)
        layout.prop(tex, "noise_basis", text="Basis")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")
        col.prop(tex, "noise_depth", text="Depth")

        col = split.column()
        col.prop(tex, "turbulence")
        col.prop(tex, "nabla")


class TEXTURE_PT_magic(TextureTypePanel, bpy.types.Panel):
    bl_label = "Magic"
    tex_type = 'MAGIC'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_depth", text="Depth")

        col = split.column()
        col.prop(tex, "turbulence")


class TEXTURE_PT_blend(TextureTypePanel, bpy.types.Panel):
    bl_label = "Blend"
    tex_type = 'BLEND'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "progression")

        sub = layout.row()

        sub.active = (tex.progression in ('LINEAR', 'QUADRATIC', 'EASING', 'RADIAL'))
        sub.prop(tex, "use_flip_axis", expand=True)


class TEXTURE_PT_stucci(TextureTypePanel, bpy.types.Panel):
    bl_label = "Stucci"
    tex_type = 'STUCCI'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "stucci_type", expand=True)
        layout.label(text="Noise:")
        layout.prop(tex, "noise_type", text="Type", expand=True)
        layout.prop(tex, "noise_basis", text="Basis")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")

        col = split.column()
        col.prop(tex, "turbulence")


class TEXTURE_PT_image(TextureTypePanel, bpy.types.Panel):
    bl_label = "Image"
    tex_type = 'IMAGE'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.template_image(tex, "image", tex.image_user)


def texture_filter_common(tex, layout):
    layout.label(text="Filter:")
    layout.prop(tex, "filter_type", text="")
    if tex.use_mipmap and tex.filter_type in ('AREA', 'EWA', 'FELINE'):
        if tex.filter_type == 'FELINE':
            layout.prop(tex, "filter_probes", text="Probes")
        else:
            layout.prop(tex, "filter_eccentricity", text="Eccentricity")

    layout.prop(tex, "filter_size")
    layout.prop(tex, "use_filter_size_min")


class TEXTURE_PT_image_sampling(TextureTypePanel, bpy.types.Panel):
    bl_label = "Image Sampling"
    bl_default_closed = True
    tex_type = 'IMAGE'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        # slot = context.texture_slot

        split = layout.split()

        col = split.column()
        col.label(text="Alpha:")
        col.prop(tex, "use_alpha", text="Use")
        col.prop(tex, "use_calculate_alpha", text="Calculate")
        col.prop(tex, "invert_alpha", text="Invert")
        col.separator()
        col.prop(tex, "use_flip_axis", text="Flip X/Y Axis")

        col = split.column()

        col.prop(tex, "use_normal_map")
        row = col.row()
        row.active = tex.use_normal_map
        row.prop(tex, "normal_space", text="")

        col.prop(tex, "use_mipmap")
        row = col.row()
        row.active = tex.use_mipmap
        row.prop(tex, "use_mipmap_gauss")
        col.prop(tex, "use_interpolation")

        texture_filter_common(tex, col)


class TEXTURE_PT_image_mapping(TextureTypePanel, bpy.types.Panel):
    bl_label = "Image Mapping"
    bl_default_closed = True
    tex_type = 'IMAGE'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "extension")

        split = layout.split()

        if tex.extension == 'REPEAT':
            col = split.column(align=True)
            col.label(text="Repeat:")
            col.prop(tex, "repeat_x", text="X")
            col.prop(tex, "repeat_y", text="Y")

            col = split.column(align=True)
            col.label(text="Mirror:")
            col.prop(tex, "use_mirror_x", text="X")
            col.prop(tex, "use_mirror_y", text="Y")
            layout.separator()

        elif tex.extension == 'CHECKER':
            col = split.column(align=True)
            row = col.row()
            row.prop(tex, "use_checker_even", text="Even")
            row.prop(tex, "use_checker_odd", text="Odd")

            col = split.column()
            col.prop(tex, "checker_distance", text="Distance")

            layout.separator()

        split = layout.split()

        col = split.column(align=True)
        #col.prop(tex, "crop_rectangle")
        col.label(text="Crop Minimum:")
        col.prop(tex, "crop_min_x", text="X")
        col.prop(tex, "crop_min_y", text="Y")

        col = split.column(align=True)
        col.label(text="Crop Maximum:")
        col.prop(tex, "crop_max_x", text="X")
        col.prop(tex, "crop_max_y", text="Y")


class TEXTURE_PT_envmap(TextureTypePanel, bpy.types.Panel):
    bl_label = "Environment Map"
    tex_type = 'ENVIRONMENT_MAP'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        env = tex.environment_map


        row = layout.row()
        row.prop(env, "source", expand=True)
        row.menu("TEXTURE_MT_envmap_specials", icon='DOWNARROW_HLT', text="")

        if env.source == 'IMAGE_FILE':
            layout.template_ID(tex, "image", open="image.open")
            layout.template_image(tex, "image", tex.image_user, compact=True)
        else:
            layout.prop(env, "mapping")
            if env.mapping == 'PLANE':
                layout.prop(env, "zoom")
            layout.prop(env, "viewpoint_object")

            split = layout.split()

            col = split.column()
            col.prop(env, "layers_ignore")
            col.prop(env, "resolution")
            col.prop(env, "depth")

            col = split.column(align=True)

            col.label(text="Clipping:")
            col.prop(env, "clip_start", text="Start")
            col.prop(env, "clip_end", text="End")


class TEXTURE_PT_envmap_sampling(TextureTypePanel, bpy.types.Panel):
    bl_label = "Environment Map Sampling"
    bl_default_closed = True
    tex_type = 'ENVIRONMENT_MAP'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        texture_filter_common(tex, layout)


class TEXTURE_PT_musgrave(TextureTypePanel, bpy.types.Panel):
    bl_label = "Musgrave"
    tex_type = 'MUSGRAVE'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "musgrave_type")

        split = layout.split()

        col = split.column()
        col.prop(tex, "dimension_max", text="Dimension")
        col.prop(tex, "lacunarity")
        col.prop(tex, "octaves")

        col = split.column()
        if (tex.musgrave_type in ('HETERO_TERRAIN', 'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL')):
            col.prop(tex, "offset")
        if (tex.musgrave_type in ('RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL')):
            col.prop(tex, "gain")
            col.prop(tex, "noise_intensity", text="Intensity")

        layout.label(text="Noise:")

        layout.prop(tex, "noise_basis", text="Basis")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")

        col = split.column()
        col.prop(tex, "nabla")


class TEXTURE_PT_voronoi(TextureTypePanel, bpy.types.Panel):
    bl_label = "Voronoi"
    tex_type = 'VORONOI'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        split = layout.split()

        col = split.column()
        col.label(text="Distance Metric:")
        col.prop(tex, "distance_metric", text="")
        sub = col.column()
        sub.active = tex.distance_metric == 'MINKOVSKY'
        sub.prop(tex, "minkovsky_exponent", text="Exponent")
        col.label(text="Coloring:")
        col.prop(tex, "color_mode", text="")
        col.prop(tex, "noise_intensity", text="Intensity")

        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Feature Weights:")
        sub.prop(tex, "weight_1", text="1", slider=True)
        sub.prop(tex, "weight_2", text="2", slider=True)
        sub.prop(tex, "weight_3", text="3", slider=True)
        sub.prop(tex, "weight_4", text="4", slider=True)

        layout.label(text="Noise:")

        split = layout.split()

        col = split.column()
        col.prop(tex, "noise_scale", text="Size")

        col = split.column()
        col.prop(tex, "nabla")


class TEXTURE_PT_distortednoise(TextureTypePanel, bpy.types.Panel):
    bl_label = "Distorted Noise"
    tex_type = 'DISTORTED_NOISE'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture

        layout.prop(tex, "noise_distortion")
        layout.prop(tex, "noise_basis", text="Basis")

        split = layout.split()

        col = split.column()
        col.prop(tex, "distortion", text="Distortion")
        col.prop(tex, "noise_scale", text="Size")

        col = split.column()
        col.prop(tex, "nabla")


class TEXTURE_PT_voxeldata(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Voxel Data"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        tex = context.texture
        engine = context.scene.render.engine
        return tex and (tex.type == 'VOXEL_DATA' and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        vd = tex.voxel_data

        layout.prop(vd, "file_format")
        if vd.file_format in ('BLENDER_VOXEL', 'RAW_8BIT'):
            layout.prop(vd, "filepath")
        if vd.file_format == 'RAW_8BIT':
            layout.prop(vd, "resolution")
        elif vd.file_format == 'SMOKE':
            layout.prop(vd, "domain_object")
            layout.prop(vd, "smoke_data_type")
        elif vd.file_format == 'IMAGE_SEQUENCE':
            layout.template_ID(tex, "image", open="image.open")
            layout.template_image(tex, "image", tex.image_user, compact=True)
            #layout.prop(vd, "frame_duration")

        layout.prop(vd, "use_still_frame")
        row = layout.row()
        row.active = vd.use_still_frame
        row.prop(vd, "still_frame")

        layout.prop(vd, "interpolation")
        layout.prop(vd, "extension")
        layout.prop(vd, "intensity")


class TEXTURE_PT_pointdensity(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Point Density"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        tex = context.texture
        engine = context.scene.render.engine
        return tex and (tex.type == 'POINT_DENSITY' and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        pd = tex.point_density

        layout.prop(pd, "point_source", expand=True)

        split = layout.split()

        col = split.column()
        if pd.point_source == 'PARTICLE_SYSTEM':
            col.label(text="Object:")
            col.prop(pd, "object", text="")

            sub = col.column()
            sub.enabled = bool(pd.object)
            if pd.object:
                sub.label(text="System:")
                sub.prop_object(pd, "particle_system", pd.object, "particle_systems", text="")
            sub.label(text="Cache:")
            sub.prop(pd, "particle_cache_space", text="")
        else:
            col.label(text="Object:")
            col.prop(pd, "object", text="")
            col.label(text="Cache:")
            col.prop(pd, "vertex_cache_space", text="")

        col.separator()

        col.label(text="Color Source:")
        col.prop(pd, "color_source", text="")
        if pd.color_source in ('PARTICLE_SPEED', 'PARTICLE_VELOCITY'):
            col.prop(pd, "speed_scale")
        if pd.color_source in ('PARTICLE_SPEED', 'PARTICLE_AGE'):
            layout.template_color_ramp(pd, "color_ramp", expand=True)

        col = split.column()
        col.label()
        col.prop(pd, "radius")
        col.label(text="Falloff:")
        col.prop(pd, "falloff", text="")
        if pd.falloff == 'SOFT':
            col.prop(pd, "falloff_soft")


class TEXTURE_PT_pointdensity_turbulence(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Turbulence"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        tex = context.texture
        engine = context.scene.render.engine
        return tex and (tex.type == 'POINT_DENSITY' and (engine in cls.COMPAT_ENGINES))

    def draw_header(self, context):
        layout = self.layout

        tex = context.texture
        pd = tex.point_density

        layout.prop(pd, "use_turbulence", text="")

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        pd = tex.point_density
        layout.active = pd.use_turbulence

        split = layout.split()

        col = split.column()
        col.label(text="Influence:")
        col.prop(pd, "turbulence_influence", text="")
        col.label(text="Noise Basis:")
        col.prop(pd, "noise_basis", text="")

        col = split.column()
        col.label()
        col.prop(pd, "turbulence_scale")
        col.prop(pd, "turbulence_depth")
        col.prop(pd, "turbulence_strength")


class TEXTURE_PT_custom_props(TextureButtonsPanel, PropertyPanel, bpy.types.Panel):
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}
    _context_path = "texture"


def register():
    pass


def unregister():
    pass

if __name__ == "__main__":
    register()
