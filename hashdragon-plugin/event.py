from electroncash.address import Script, Address, ScriptOutput

LOKAD_ID = b'\xd1\x01\xd4\x00'
INDEX_BYTE_SIZE = 4


class Event:

    @staticmethod
    def build_hashdragon_op_return(command, input_index, output_index, dest_address, second_input=None, second_output=None, third_output=None):

        script = bytearray()
        script.append(0x6a)
        script.extend(Script.push_data(LOKAD_ID))

        if command == 'wander':
            script.extend(Script.push_data(b'\xd2'))
            script.extend(Script.push_data(input_index.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))
            script.extend(Script.push_data(output_index.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))
        # elif command == 'rescue':
        #     script.extend(Script.push_data(b'\xd2'))
        elif command == 'hibernate':
            script.extend(Script.push_data(b'\xd3'))
            script.extend(Script.push_data(input_index.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))
            script.extend(Script.push_data(output_index.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))

        elif command == 'breed':
            script.extend(Script.push_data(b'\xd4'))
            # First hashdragon
            script.extend(Script.push_data(input_index.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))
            script.extend(Script.push_data(output_index.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))
            # Second hashdragon
            script.extend(Script.push_data(second_input.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))
            script.extend(Script.push_data(second_output.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))
            # Spawn output index.
            script.extend(Script.push_data(third_output.to_bytes(INDEX_BYTE_SIZE, byteorder='big')))
        else:
            raise Exception('Unsupported command.')

        return ScriptOutput.protocol_factory(bytes(script))



#event = Event()
#print(event.build_hashdragon_op_return('wander'))
