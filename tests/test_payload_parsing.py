import io
import ipaddress
import unittest

from haproxyspoa.spoa_data_types import write_string, write_typed_autodetect
from haproxyspoa.spoa_payloads import write_kv_list, parse_kv_list, parse_list_of_messages


class TestPayloadParsing(unittest.TestCase):

    def test_write_read_list_of_messages(self):
        buffer = io.BytesIO()

        message_name = "solar_system_communication"
        num_args = 4
        args = {
            "mercury": write_typed_autodetect(ipaddress.IPv4Address("192.168.1.23")),
            "venus": write_typed_autodetect(123456789),
            "earth": write_typed_autodetect("looks like a marble"),
            "mars": write_typed_autodetect(True),
        }

        buffer.write(write_string(message_name))
        buffer.write(bytes([num_args]))
        buffer.write(write_kv_list(args))

        self.assertEqual(
            buffer.getvalue(),
            b'\x1asolar_system_communication\x04\x07mercury\x06\xc0\xa8\x01\x17\x05venus\x04\xf5\xc2\xf8\xd5\x02'
            b'\x05earth\x08\x13looks like a marble\x04mars\x04\x01',
        )

        buffer.seek(0)
        messages = parse_list_of_messages(buffer)

        self.assertEqual(messages, {
            "solar_system_communication": {
                "mercury": ipaddress.IPv4Address("192.168.1.23"),
                "venus": 123456789,
                "earth": "looks like a marble",
                "mars": 1
            }
        })


if __name__ == '__main__':
    unittest.main()
