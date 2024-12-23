from typing import Tuple, List, Optional, TYPE_CHECKING

from UE4Parse.BinaryReader import BinaryStream
from UE4Parse.Assets.Objects.EPixelFormat import EPixelFormat
from UE4Parse.Readers.FAssetReader import FAssetReader
from UE4Parse.Versions.EUEVersion import GAME_UE5, EUEVersion
from UE4Parse.Assets.Exports.Textures.Objects.FTexture2DMipMap import FTexture2DMipMap
from UE4Parse.Assets.Objects.Structs.Colors import FLinearColor
from UE4Parse.Assets.Exports.Textures.Objects.FVirtualTextureDataChunk import FVirtualTextureDataChunk

class FVirtualTextureTileOffsetData:
    Width: int
    Height: int
    MaxAddress: int
    Addresses: List[int]
    Offsets: List[int]

    def __init__(self, reader: BinaryStream):
        self.deserialize(reader)

    def deserialize(self, reader):
        self.Width = reader.readInt32()
        self.Height = reader.readInt32()
        self.MaxAddress = reader.readInt32()
        self.Addresses = reader.readTArray(reader.readInt32)
        self.Offsets = reader.readTArray(reader.readInt32)
        #print(type(self).__name__, self.Width, self.Height, self.MaxAddress, self.Addresses, self.Offsets)

    def GetValue(self):
        return {
            'Width': self.Width,
            'Height': self.Height,
            'MaxAddress': self.MaxAddress,
            'Addresses': self.Addresses,
            'Offsets': self.Offsets,
        }

    def GetTileOffset(self, inAddress:int) -> int:
        return 0
        '''
            var blockIndex = 0;
            if (Addresses != null)
            {
                for (var i = 0; i < Addresses.Length; i++)
                {
                    if (Addresses[i] > inAddress)
                    {
                        blockIndex = i - 1;
                        break;
                    }
                    if (i == Addresses.Length - 1 && blockIndex == 0)
                    {
                        blockIndex = Addresses.Length - 1;
                    }
                }
            }

            var baseOffset = Offsets[blockIndex];
            if (baseOffset == ~0u)
            {
                return ~0u;
            }

            uint baseAddress = Addresses[blockIndex];
            uint localOffset = inAddress - baseAddress;
            return baseOffset + localOffset;
        }
        '''

class FVirtualTextureBuiltData:
    NumLayers: int
    NumMips: int
    Width: int
    Height: int
    WidthInBlocks: int
    HeightInBlocks: int
    TileSize: int
    ChunkIndexPerMip: List[int]

    def __init__(self, reader: FAssetReader, firstMip: int):
        self.deserialize(reader, firstMip)

    def deserialize(self, reader: FAssetReader, firstMip: int):
        bStripMips = firstMip > 0;
        bCooked = reader.readBool()
        self.NumLayers = reader.readInt32()
        self.WidthInBlocks = reader.readInt32()
        self.HeightInBlocks = reader.readInt32()
        self.TileSize = reader.readInt32()
        self.TileBorderSize = reader.readInt32()

        if reader.game >= GAME_UE5(0):
            self.TileDataOffsetPerLayer = reader.readTArray(reader.readInt32)
            #print('tiledataoffsetperlayer:', self.TileDataOffsetPerLayer)

        if not bStripMips:
             self.NumMips = reader.readInt32()
             self.Width = reader.readInt32()
             self.Height = reader.readInt32()

             #print('mips, w, h:', self.NumMips, self.Width, self.Height)

             if reader.game >= GAME_UE5(0):
                 self.ChunkIndexPerMip = reader.readTArray(reader.readInt32);
                 self.BaseOffsetPerMip = reader.readTArray(reader.readInt32);
                 self.TileOffsetData = reader.readTArray(FVirtualTextureTileOffsetData, reader)

             self.TileIndexPerChunk = reader.readTArray(reader.readInt32);
             self.TileIndexPerMip = reader.readTArray(reader.readInt32);
             self.TileOffsetInChunk = reader.readTArray(reader.readInt32);

             #print( self.TileIndexPerChunk, self.TileIndexPerMip, self.TileOffsetInChunk )
             #print('===', json.dumps(self.GetValue(),indent=2))

             #print('ofs', f'0x{reader.position:X}')

             self.LayerTypes = []
             for i in range(self.NumLayers):
                pixelFormat = EPixelFormat[reader.readFString()]
                self.LayerTypes.append(pixelFormat)

             self.LayerFallbackColors = []
             if reader.game >= GAME_UE5(0):
                 self.LayerFallbackColors = [FLinearColor(reader) for _ in range(self.NumLayers)]

             count = reader.readInt32()
             self.Chunks = [FVirtualTextureDataChunk(reader, self.NumLayers) for _ in range(count)]

    def GetValue(self):
        return {
            "NumLayers": self.NumLayers,
            "WidthInBlocks": self.WidthInBlocks,
            "HeightInBlocks": self.HeightInBlocks,
            "TileSize": self.TileSize,
            "TileBorderSize": self.TileBorderSize,
            "TileDataOffsetPerLayer": self.TileDataOffsetPerLayer,
            "ChunkIndexPerMip": self.ChunkIndexPerMip,
            "BaseOffsetPerMip": self.BaseOffsetPerMip,
            "TileOffsetData": [x.GetValue() for x in self.TileOffsetData],
            "LayerTypes": [x.value for x in self.LayerTypes],
            "FallbackColors": [x.GetValue() for x in self.LayerFallbackColors],
            "Chunks": [x.GetValue() for x in self.Chunks],
        }
