import unittest

from rmmglp.protocol import EP3, EVENTS, POLLING_PACKETS, RGB_CAPTURED, RGB_NAMED, build_full_packets


class ProtocolTests(unittest.TestCase):
    def test_ep3_lengths(self):
        self.assertEqual([len(x) for x in EP3], [32] * 8)

    def test_dpi_encoding(self):
        for dpi, expected in ((200, 0x02), (800, 0x08), (1200, 0x0C), (1600, 0x10), (16000, 0xA0)):
            _, reports = build_full_packets(dpi, 1000, *RGB_NAMED["green"])
            self.assertEqual(reports[2][0], expected)

    def test_polling_packets(self):
        self.assertEqual(POLLING_PACKETS[500], bytes.fromhex("27 2B DD FF 00 1D 96 76"))
        self.assertEqual(POLLING_PACKETS[1000], bytes.fromhex("27 2B DD FF E8 25 96 76"))

    def test_rgb_capture_count(self):
        self.assertEqual(len(RGB_CAPTURED), 46)

    def test_full_transaction_shape(self):
        ctrls, reports = build_full_packets(1600, 1000, *RGB_NAMED["green"])
        self.assertEqual(len(ctrls), 14)
        self.assertTrue(all(len(x) == 8 for x in ctrls))
        self.assertEqual(len(reports), 8)
        self.assertTrue(all(len(x) == 32 for x in reports))
        self.assertEqual(reports[2][:8], bytes.fromhex("10 10 05 3D 4F D0 50 F8"))

    def test_event_order(self):
        self.assertEqual(EVENTS[0][:2], ("ctrl", 0))
        self.assertEqual(EVENTS[1][0], "get")
        self.assertEqual(EVENTS[-1][:2], ("ctrl", 13))


if __name__ == "__main__":
    unittest.main()
