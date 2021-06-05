from electroncash.address import Script, Address, ScriptOutput

LOKAD_ID = b'\xd1\x01\xd4\x00'

class Event:

    def build_hashdragon_op_return(self, command, input_index, output_index, dest_address):

        script = bytearray()
        script.append(0x6a)
        script.extend(Script.push_data(LOKAD_ID))

        if command == 'wander':
            script.extend(Script.push_data(b'\xd2'))
            script.extend(Script.push_data((input_index).to_bytes(8, byteorder='big')))
            script.extend(Script.push_data((output_index).to_bytes(8, byteorder='big')))
        # elif command == 'rescue':
        #     script.extend(Script.push_data(b'\xd2'))
        elif command == 'hibernate':
            script.extend(Script.push_data(b'\xd3'))
            script.extend(Script.push_data((input_index).to_bytes(8, byteorder='big')))
            script.extend(Script.push_data((output_index).to_bytes(8, byteorder='big')))
        else:
            raise Exception('Unsupported command.')


        return ScriptOutput.protocol_factory(bytes(script))



#event = Event()
#print(event.build_hashdragon_op_return('wander'))
