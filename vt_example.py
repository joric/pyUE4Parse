import os,sys

from UE4Parse.Versions import EUEVersion
from UE4Parse.BinaryReader import BinaryStream
from UE4Parse.Assets.PackageReader import IoPackageReader
from UE4Parse.Assets.Exports.Textures.Objects.FTexturePlatformData import FTexturePlatformData

export_dir = 'C:/Temp/Exports'

#fname = 'Stalker2/Content/GameLite/FPS_Game/UIRemaster/UITextures/PDA/WorldMap/T_WorldMap_UDIM.uexp'
fname = 'MyProject/Content/stalker2_map_joric_8k_mod2.uasset'

fname = os.path.join(export_dir, fname)
reader = BinaryStream(open(fname, 'rb'))
ubulk_stream = BinaryStream(open(os.path.splitext(fname)[0] + '.ubulk', 'rb'))

if fname.endswith('.uexp'):
    pos = 60 # uexp (larger files): starts from 60
else:
    # uasset: locate first PF_DXT1, then locate second and step back a little
    b = reader.read(1024)
    pos = b.find(b'PF_DXT1')
    pos = b.find(b'PF_DXT1', pos+1)-32

print(f'start offset: {pos} (0x{pos:x})')
reader.seek(pos, os.SEEK_SET)

reader.game = EUEVersion.LATEST
reader.is_filter_editor_only = True
reader.has_unversioned_properties = True
reader.version = reader.game
reader.getmappings = lambda:MappingProvider()
reader.get_name_map = lambda:[]
reader.ubulk_stream =  ubulk_stream
reader.bulk_offset = 0

reader.Owner = IoPackageReader if fname.endswith('.uexp') else None

data = FTexturePlatformData(reader, reader.ubulk_stream, reader.bulk_offset)

#print(json.dumps(data.GetValue(), indent=2))
#print(data.GetValue())

print(data.GetValue()['VTData']['Chunks'])
