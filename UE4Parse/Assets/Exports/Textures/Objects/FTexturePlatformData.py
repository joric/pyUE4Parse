from typing import Tuple

from UE4Parse.BinaryReader import BinaryStream
from UE4Parse.Assets.Objects.EPixelFormat import EPixelFormat
from UE4Parse.Readers.FAssetReader import FAssetReader
from UE4Parse.Versions.EUEVersion import GAME_UE4, EUEVersion
from UE4Parse.Assets.Exports.Textures.Objects.FTexture2DMipMap import FTexture2DMipMap
from UE4Parse.Assets.Exports.Textures.Objects.FVirtualTextureBuiltData import FVirtualTextureBuiltData


class FTexturePlatformData:
    SizeX: int
    SizeY: int
    NumSlices: int
    PixelFormat: EPixelFormat
    Mips: Tuple[FTexture2DMipMap]
    VirtualData = None
    bIsVirtual = False
    FirstMipToSerialize: int
    VTData: FVirtualTextureBuiltData

    def __init__(self, reader: FAssetReader, ubulk: BinaryStream, ubulkOffset: int):
        self.deserialize(reader, ubulk, ubulkOffset)

    def deserialize(self, reader: FAssetReader, ubulk: BinaryStream, ubulkOffset: int):
        if reader.game >= EUEVersion.GAME_UE5_0 and reader.is_filter_editor_only:
            reader.seek(16) # PlaceholderDerivedDataSize

        self.SizeX = reader.readInt32()
        self.SizeY = reader.readInt32()
        self.NumSlices = reader.readInt32()  # 1 for normal textures
        self.PixelFormat = EPixelFormat[reader.readFString()]

        first_mip = reader.readInt32()
        self.FirstMipToSerialize = first_mip-1 if first_mip > 0 else first_mip
        self.Mips = reader.readTArray(FTexture2DMipMap, reader, ubulk, ubulkOffset)
        if reader.game >= GAME_UE4(23):
            self.bIsVirtual = reader.readInt32() != 0
            if self.bIsVirtual:
                LODBias = 0 #Owner.GetOrDefault<int>("LODBias"); # TODO Owner
                self.VTData = FVirtualTextureBuiltData(reader, self.FirstMipToSerialize - LODBias)

    def GetValue(self):
        return {
            "PixelFormat": self.PixelFormat.name,
            "FirstMip": self.FirstMipToSerialize,
            "NumSlices": self.NumSlices,
            "Size": {
                "X": self.SizeX,
                "Y": self.SizeY
            },
            "IsVirtual": self.bIsVirtual,
            "Mips": [x.GetValue() for x in self.Mips],
            "VTData": self.VTData.GetValue() if hasattr(self, 'VTData') else {},
        }
