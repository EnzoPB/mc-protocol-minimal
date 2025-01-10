from .mc_special_type import MCSpecialType
import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader


class Array(MCSpecialType):
    @staticmethod
    def decode(stream: io.IOBase, structure: dict, packet: 'PacketReader'):
        # import this here (not at top) to avoid circular import loop
        from . import types_names

        # first we read the count (length of the array)
        # either it is given directly with countType
        if 'countType' in structure:
            count = types_names[structure['countType']].decode(stream)
        # or the count is given in a field earlier
        elif 'count' in structure:
            count = packet.dict_relative_path_get(packet.data, packet.current_path, structure['count'])
        array = []
        # decode each element of the array
        for i in range(count):
            packet.current_path.append(i)
            print('array enter', i, packet.current_path)
            array.append(packet.decode_field(stream, structure['type']))
            packet.current_path.pop()
            print('array exit', i, packet.current_path)
