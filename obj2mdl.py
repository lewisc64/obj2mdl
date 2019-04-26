try:
    from PIL import Image
except ImportError:
    print("Can't import Pillow. Image conversions will not function.")
import sys
import subprocess
import json
import os
import shutil
import re
import math

file = open("config.json", "r")
config = json.loads(file.read())
file.close()

class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __iter__(self):
        return iter([self.x, self.y, self.z])

class Shape:
    def __init__(self):
        self.vertices = []
        self.normal_vertices = []
        self.faces = []
        self.texture_faces = []
        self.texture_coordinates = []
        self.face_materials = []
        self.face_normals = []

    def assign_materials(self, name):
        while len(self.face_materials) < len(self.faces):
            self.face_materials.append(name)

def get_filename(path):
    return re.search(r"([^.\\/]+)\.", path).group(1)

def remove_extension(path):
    return path.split(".")[0]

def get_qc_path(path):
    return remove_extension(path) + ".qc"

def next_power(n, p):
    out = 1
    while out < n:
        out *= p
    return out

def load_obj(path, model_config):
    
    file = open(path, "r")
    lines = file.readlines()
    file.close()
    
    out = Shape()
    current_material = ""
    
    for line in lines:
        
        data = line.split()
        if len(data) == 0:
            continue
        
        if data[0] == "usemtl":
            current_material = data[1]
            
        elif data[0] == "v":
            out.vertices.append(Vertex(*[float(x) for x in data[1:]]))
            
        elif data[0] == "vt":
            out.texture_coordinates.append([float(x) for x in data[1:]])
            
        elif data[0] == "vn":
            out.normal_vertices.append(Vertex(*[float(x) for x in data[1:]]))
            
        elif data[0] == "f":
            
            faces_points = [data[1:]]
            
            if len(faces_points[0]) == 4: # split quad into triangles
                point = faces_points.pop()
                faces_points.append(point[:-1])
                faces_points.append([point[0]] + point[-2:])

            for points in faces_points:
                
                face = []
                texture_face = []
                face_normal = []
                
                for point in points:
                    
                    values = point.split("/")
                    
                    face.append(int(values[0]) - 1)
                    
                    if len(values) >= 2 and values[1] != "":
                        texture_face.append(int(values[1]) - 1)
                    else:
                        texture_face.append(None)
                        
                    if len(values) >= 3 and values[2] != "":
                        face_normal.append(int(values[2]) - 1)
                    else:
                        face_normal.append(None)
                        
                out.faces.append(face)
                out.texture_faces.append(texture_face)
                out.face_normals.append(face_normal)
                
                if model_config["material"]["use_file"]:
                    out.face_materials.append(current_material)
    
    return out

def generate_smd(shape):
    out = [
        "version 1",
        "nodes",
        "0 \"root\" -1",
        "end",
        "skeleton",
        "time 0",
        "0 0 0 0 0 0 0",
        "end",
        "triangles"
    ]

    for face, texture_face, face_normal, material_name in zip(shape.faces, shape.texture_faces, shape.face_normals, shape.face_materials):
        out.append(material_name)
        for v, vt, vn in zip(face, texture_face, face_normal):
            vertex = shape.vertices[v]
            if vn is None:
                normal = Vertex(0, 0, 0)
            else:
                normal = shape.normal_vertices[vn]
            
            out_point = shape.texture_coordinates[vt]
            out_vertex = [vertex.x, -vertex.z, vertex.y]
            out_normal = [normal.x, -normal.z, normal.y]
            
            out.append("0 {} {} {}".format("{} {} {}".format(*out_vertex), "{} {} {}".format(*out_normal), "{} {}".format(*out_point)))

    out.append("end")
    return "\n".join(out)

def save_smd(shape, path):

    file = open(path, "w")
    file.write(generate_smd(shape))
    file.close()

def stringify_qc(qc):
    out = []
    for key, value in qc.items():
        if isinstance(value, str):
            if value == "":
                out.append("${}".format(key))
            else:
                out.append("${} \"{}\"".format(key, value))
        elif isinstance(value, int):
            out.append("${} {}".format(key, value))
        elif isinstance(value, list):
            out.append(stringify_qc({key: value[0]}))
            out.append(stringify_qc({0:value[1]}))
        elif isinstance(value, dict):
            out.append("{")
            out.append(stringify_qc(value))
            out.append("}")
    return "\n".join(out)

def set_qc_property(qc, property_name, value):
    if isinstance(value, bool):
        if value:
            qc[property_name] = ""
    else:
        qc[property_name] = value

def configure_qc_property(qc, model_config, property_name, default):
    if property_name in model_config["qc"]:
        set_qc_property(qc, property_name, model_config["qc"][property_name])
    else:
        set_qc_property(qc, property_name, default)

def generate_qc(model_config):
    name = model_config["name"]
    qc = {
        "modelname": "{}/{}.mdl".format(name, name),
        "body studio": "{}.smd".format(name),
        "surfaceprop": model_config["qc"]["surfaceprop"],
        "CDMaterials": "models/{}/".format(name),
        "sequence idle": "{}.smd".format(name),
        "collisionmodel": [
            "{}.smd".format(name),
            {}
        ]
    }

    configure_qc_property(qc, model_config, "staticprop", True)
    configure_qc_property(qc, model_config, "scale", 2)
    configure_qc_property(qc["collisionmodel"][1], model_config, "automass", True)
    configure_qc_property(qc["collisionmodel"][1], model_config, "concave", False)
    
    return stringify_qc(qc)

def save_qc(model_config, path):
    file = open(path, "w")
    file.write(generate_qc(model_config))
    file.close()

def png_to_tga(png_path, output_path):
    img = Image.open(png_path)
    img = img.resize((next_power(img.width, 2), next_power(img.height, 2)), Image.ANTIALIAS)
    img.save(output_path, "TGA")

def tga_to_vtf(name):
    subprocess.run([config["engine_path"] + "/vtex.exe", "-game", config["game_path"], "-shader", "LightmappedGeneric", "-vmtparam", "$surfaceprop", config["surfaceprop"], "-dontusegamedir", name])

def png_to_vtf(path):
    name = get_filename(path)

    png_to_tga(path, "{}.tga".format(name))
    tga_to_vtf(name)

def build_mdl(qc_path):
    subprocess.run([config["engine_path"] + "/studiomdl.exe", "-game", config["game_path"], "-nop4", "-verbose", qc_path])

def obj_to_mdl(path, model_config):
    
    name = model_config["name"]
    qc_path = remove_extension(path) + ".qc"
    smd_path = remove_extension(path) + ".smd"
    
    shape = load_obj(path, model_config)
    shape.assign_materials(model_config["material"]["name"])
    save_smd(shape, smd_path)

    if model_config["auto_generate_qc"]:
        save_qc(model_config, qc_path)
    
    build_mdl(qc_path)

    try:
        subprocess.check_call(["explorer", config["game_path"] + "\\models\\" + name])
    except:
        pass

if __name__ == "__main__":

    halt = False

    if "-help" in sys.argv or "-usage" in sys.argv:
        print("Example usage:")
        print("obj2mdl model.obj\n")
        print("Optional flags:")
        print("    -nopause")
        halt = True

    if not halt:

        for item in sys.argv[1:]:
            if item[0] != "-":
                path = item
                break
        else:
            path = input("Path to OBJ: ")

        config_path = remove_extension(path) + ".json"

        try:
            file = open(config_path, "r")
            model_config = json.loads(file.read())
            file.close()
        except FileNotFoundError:
            print("Please create the config file '{}'.".format(config_path))
            halt = True

        if not halt:
            obj_to_mdl(path, model_config)

    if "-nopause" not in sys.argv:
        input("Press enter to exit...")


