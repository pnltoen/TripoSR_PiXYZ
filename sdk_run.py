import pxz
from pxz import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--import-format",
    default="glb",
    type=str,
    choices=["obj", "glb"],
    help="Format to optimize the imported mesh. Default: 'glb'",
)

parser.add_argument(
    "--export-format",
    default="gltf",
    type=str,
    help="Format to export the mesh. Default: 'gtf'",
)

parser.add_argument(
    "--import-dir",
    default="output\\glb\\0\\mesh.glb",
    type=str,
    help="The object path to import"
)
args = parser.parse_args()

import_format = args.import_format
export_format = args.export_format
import_dir = args.import_dir

pxz.initialize()
core.configureLicenseServer("Your server", "port number", True)
core.getLicenseServer()

def replace_path(windows_path):
    windows_path = windows_path.replace('\\', '\\\\')
    return windows_path

# set log level to INFO so you can see the logs in the console
core.configureInterfaceLogger(True, True, True)
core.addConsoleVerbose(core.Verbose.INFO)

# add all tokens
for token in pxz.core.listTokens():
    core.addWantedToken(token)
    print(token)

'''
root = [scene.getRoot()]
a = scene.getPolygonCount(root, False, False, False)
algo.retopologize(root, a, True, False, -1)
'''

# Importing a model
import_dir = replace_path(import_dir)
io.importScene(import_dir, 0)

# Cleaning a hierarchy
root = scene.getRoot()
if import_format == "glb" or import_format == "gltf":
    default = scene.findOccurrencesByProperty('Name', 'geometry_0')
    core.setProperty(default[0], "Name", "default")
else:
    default = scene.findOccurrencesByProperty('Name', 'default')

scene.moveOccurrences(default, root)
scene.deleteEmptyOccurrences(root)

# Applying new transformation matrices
SCALE = 50
aabb = scene.getAABB([root])
centerX = (aabb.high.x + aabb.low.x)/2
centerY = (aabb.high.y + aabb.low.y)/2
centerZ = (aabb.high.z + aabb.low.z)/2
translation = geom.Point3(-centerX, -centerY, -centerZ)
rotation = geom.Point3(-120, -43, 39)
zero = geom.Point3(0, 0, 0)
scale = geom.Point3(SCALE, SCALE, SCALE)
translationMatrix = geom.fromTRS(translation, zero, geom.Point3(1,1,1))
rotationMatrix = geom.fromTRS(zero, rotation, geom.Point3(1,1,1))
scaleMatrix = geom.fromTRS(zero, zero, scale)
scene.applyTransformation(default[0], translationMatrix)
scene.applyTransformation(default[0], rotationMatrix)
scene.applyTransformation(default[0], scaleMatrix)

#Aligning pivot point to world
pxz.scene.alignPivotPointToWorld(default, False)

#Reparing a CAD
algo.repairMesh(default, 0.1, True, True)

#Decimating a CAD
if import_format == "glb":
    algo.decimateTarget(default, ["ratio", 3])
else:
    algo.decimateTarget(default, ["ratio", 50])

#Creating and applying a material
if import_format == "glb":
    pass
else:
    image = material.importImage("output\\obj\\texture.png")
    matDef = material.MaterialDefinition()
    matDef.name = "TripoSR_mat"
    matDef.albedo = ["texture", material.Texture(image, 0, geom.Point2(0, 0), geom.Point2(1, 1))]
    matDef.normal = ["color", [0,0,0]]
    matDef.metallic = ["coeff", 0.05]
    matDef.roughness = ["coeff", 0.35]
    matDef.ao = ["coeff", 1]
    matDef.opacity = ["coeff", 1]
    matDef.emissive = ["color", [0,0,0]]
    mat = material.createMaterialFromDefinition(matDef)
    core.setProperty(default[0], "Material", str(mat))

#exporting as fbx
export_name = export_format + "." + export_format
io.exportScene(export_name, 0)
#pxz.studio.uploadSceneToUnityCloudAssetManager("14569343989872", "a435a9d0-7748-4792-9fe8-54d72d4fe2e5", 1, export_name, True, True) Need to replace with SDK one