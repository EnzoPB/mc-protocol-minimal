from .mc_native_type import MCNativeType
from .mc_special_type import MCSpecialType

from .boolean import Boolean
from .int import Byte, UByte, Short, UShort, Int, UInt, Long, ULong
from .float import Float, Double
from .varnum import VarInt, VarLong
from .string import String
from .json import Json
from .uuid import UUID

from .container import Container
from .switch import Switch
from .option import Option
from .buffer import Buffer
from .array import Array
from .bitfield import BitField

from ..errors import *

types_names = {
    'bool': Boolean,
    'i8': Byte,
    'u8': UByte,
    'i16': Short,
    'u16': UShort,
    'i32': Int,
    'u32': UInt,
    'i64': Long,
    'u64': ULong,
    'f32': Float,
    'f64': Double,
    'varint': VarInt,
    'varlong': VarLong,
    'string': String,
    'json': Json,
    'UUID': UUID,

    'container': Container,
    'switch': Switch,
    'option': Option,
    'buffer': Buffer,
    'array': Array,
    'bitfield': BitField
}


def encode_field(data: dict, data_part: dict | list) -> bytearray:  # automatically decode a field
    # eg. data_part = ['container', [{'type': 'i64', 'name': 'field'}, ...]]
    if isinstance(data_part, list):  # if datapart is a list, it is a container (or an array? or something else)
        if data_part[0] == 'container':  # a container is just a list of different items (usually contained inside a condition)
            buffer = bytearray()
            for item in data_part[1]:
                buffer.extend(encode_field(data, item))
            return buffer

    # eg. data_part = 'UUID'
    if isinstance(data_part, str):
        if data_part in types_names:
            var_type: MCNativeType = types_names[data_part]  # get the corresponding type class
        else:
            raise UnknownType(f'Tried to encode unknown type: {data_part}')

        return var_type.encode(data)

    # eg. data_part = {'type': 'i64', 'name': 'field'}
    elif isinstance(data_part, dict):
        if isinstance(data_part['type'], str):  # type can either be a string (native type)
            if data_part['type'] in types_names:
                var_type: MCNativeType = types_names[data_part['type']]  # get the corresponding type class
            else:
                raise UnknownType(f'Tried to encode unknown type: {data_part["type"]}')

            if data_part['name'] in data:
                return var_type.encode(data[data_part['name']])
            else:
                raise InvalidPacketStructure(f'Cannot find key "{data_part["name"]}" in packet data {data}')

        elif isinstance(data_part['type'], list):  # or type can be a list (more complex type)
            if data_part['type'][0] in types_names:
                var_type: MCSpecialType = types_names[data_part['type'][0]]  # get the corresponding type class
            else:
                raise UnknownType(f'Tried to encode unknown type: {data_part["type"]}')

            if data_part['name'] in data:
                return var_type.encode(data[data_part['name']], data_part['type'])
            else:
                raise InvalidPacketStructure(f'Cannot find key "{data_part["name"]}" in packet data {data}')

        else:
            raise InvalidPacketStructure(f'Field type if of invalid type "{data_part["type"]}"')
