from typing import List

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

    def GetTileOffset(self, inAddress:int) -> int:
        blockIndex = 0
        if self.Addresses:
            for i in range(len(self.Addresses)):
                if self.Addresses[i] > inAddress:
                    blockIndex = i - 1;
                    break;
                if i == len(self.Addresses) and blockIndex == 0:
                    blockIndex = len(self.Addresses) - 1

        baseOffset = self.Offsets[blockIndex]
        if baseOffset == 0xFFFFFFFF:
            return baseOffset

        baseAddress = self.Addresses[blockIndex]
        localOffset = inAddress - baseAddress
        return baseOffset + localOffset

    def GetValue(self):
        return {
            'Width': self.Width,
            'Height': self.Height,
            'MaxAddress': self.MaxAddress,
            'Addresses': self.Addresses,
            'Offsets': self.Offsets,
        }

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
        self.TileDataOffsetPerLayer = reader.readTArray(reader.readInt32) if reader.game >= GAME_UE5(0) else []

        self.NumMips = self.Width = self.Height = 0
        self.ChunkIndexPerMip = []
        self.BaseOffsetPerMip = []
        self.TileOffsetData = []
        self.TileIndexPerChunk = []
        self.TileIndexPerMip = []
        self.TileOffsetInChunk = []
        self.LayerTypes = []
        self.LayerFallbackColors = []
        self.Chunks = []

        if not bStripMips:
             self.NumMips = reader.readInt32()
             self.Width = reader.readInt32()
             self.Height = reader.readInt32()

             if reader.game >= GAME_UE5(0):
                 self.ChunkIndexPerMip = reader.readTArray(reader.readInt32);
                 self.BaseOffsetPerMip = reader.readTArray(reader.readInt32);
                 self.TileOffsetData = reader.readTArray(FVirtualTextureTileOffsetData, reader)

             self.TileIndexPerChunk = reader.readTArray(reader.readInt32);
             self.TileIndexPerMip = reader.readTArray(reader.readInt32);
             self.TileOffsetInChunk = reader.readTArray(reader.readInt32);
             self.LayerTypes = [EPixelFormat[x] for x in reader.readTArray2(reader.readFString, self.NumLayers)]
             self.LayerFallbackColors = reader.readTArray2(FLinearColor, self.NumLayers, reader) if reader.game >= GAME_UE5(0) else []
             self.Chunks = reader.readTArray(FVirtualTextureDataChunk, reader, self.NumLayers);

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
