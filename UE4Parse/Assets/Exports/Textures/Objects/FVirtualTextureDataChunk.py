from typing import Tuple, List, Optional, TYPE_CHECKING

from UE4Parse.BinaryReader import BinaryStream
from UE4Parse.Assets.Objects.EPixelFormat import EPixelFormat
from UE4Parse.Versions.EUEVersion import GAME_UE4, GAME_UE5, EUEVersion
from UE4Parse.Assets.Objects.FByteBulkData import FByteBulkData
from UE4Parse.PakFile.PakObjects.FSHAHash import FSHAHash
from enum import IntEnum, auto

class EVirtualTextureCodec(IntEnum):
    Black = 0                   # Special case codec, always outputs black pixels 0,0,0,0
    OpaqueBlack = 1             # Special case codec, always outputs opaque black pixels 0,0,0,255
    White = 2                   # Special case codec, always outputs white pixels 255,255,255,255
    Flat = 3                    # Special case codec, always outputs 128,125,255,255 (flat normal map)
    RawGPU = 4                  # Uncompressed data in an GPU-ready format (e.g R8G8B8A8, BC7, ASTC, ...)
    ZippedGPU_DEPRECATED = 5    # Same as RawGPU but with the data zipped
    Crunch_DEPRECATED = 6       # Use the Crunch library to compress data
    Max = auto()                # Add new codecs before this entry

class FVirtualTextureDataChunk:
    def __init__(self, reader: BinaryStream, numLayers: int):
        self.deserialize(reader, numLayers)

    def deserialize(self, reader: BinaryStream, numLayers: int):
        self.CodecType = []
        self.CodecPayloadOffset = []

        if reader.game >= GAME_UE5(0):
            self.Hash = FSHAHash(reader)

        self.SizeInBytes = reader.readUInt32();
        self.CodecPayloadSize = reader.readUInt32();

        for layerIndex in range(numLayers):
            self.CodecType.append(reader.readUInt8())
            self.CodecPayloadOffset.append(reader.readUInt32() if reader.game >= GAME_UE4(27) else reader.readInt16())

        self.BulkData = FByteBulkData(reader, reader.ubulk_stream, reader.bulk_offset);

    def GetValue(self):
        return {
            'SizeInBytes' : self.SizeInBytes,
            'CodecPayloadSize': self.CodecPayloadSize,
            'CodecType': [EVirtualTextureCodec(x).name if x in EVirtualTextureCodec else 'Unknown' for x in self.CodecType],
            'CodecPayloadOffset': self.CodecPayloadOffset,
        }
