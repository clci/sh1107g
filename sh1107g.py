
# based on SeeedGrayOLED.cpp for Arduino. SeeedGrayOLED.cpp is Copyright (c) 2011 seeed technology inc.

import framebuf

DISPLAY_I2C_ADDRESS = const(0x3C)
COMMAND_MODE = const(0x80)
DATA_MODE = const(0x40)
CMD_DISPLAY_OFF = const(0xAE)
CMD_DISPLAY_ON = const(0xAF)
CMD_NORMAL_DISPLAY = const(0xA6)
CMD_REVERSE_DISPLAY = const(0xA7)
CMD_SET_CONTRASTLEVEL = const(0x81)


class SH1107G(framebuf.FrameBuffer):

    def __init__(self, i2c):

        self.i2c = i2c
        self.image_buffer = bytearray(128//8 * 128)   # 128x128 dot matrix
        self.visible_buffer = bytearray(128//8 * 128)
        super().__init__(self.image_buffer, 128, 128, framebuf.MONO_VLSB)

        self.cmd_data = bytearray([COMMAND_MODE, 0])

        # display initialization
        init_data = [
            CMD_DISPLAY_OFF,
            0xd5,  # Set Dclk
            0x50,  # 100Hz
            0x20,  # Set row address
            CMD_SET_CONTRASTLEVEL,
            0x80,
            0xa0,  # Segment remap
            0xa4,  # Set Entire Display ON
            CMD_NORMAL_DISPLAY,
            0xad,  # Set external VCC
            0x80,
            0xc0,  # Set Common scan direction
            0xd9,  # Set phase leghth
            0x1f,
            0xdb,  # Set Vcomh voltage
            0x27,
            0xb0,
            0x00,
            0x11
        ]
        self._send_command(init_data)

        self.update_all()
        self.set_power(True)


    @micropython.native
    def _send_command(self, data):

        addr = DISPLAY_I2C_ADDRESS
        cmd = self.cmd_data
        writeto = self.i2c.writeto

        for b in data:
            cmd[1] = b
            writeto(addr, cmd)


    @micropython.native
    def _send_data(self, data):

        block = bytearray([DATA_MODE])
        block[1:] = data
        self.i2c.writeto(DISPLAY_I2C_ADDRESS, block)


    @micropython.native
    def _set_cursor(self, page, col):

        sc = self._send_command
        sc([0xB0 + (page & 0x0F)])
        sc([0x00 + (col & 0x0F)])
        sc([0x10 + ((col & 0x70) >> 4)])


    def set_power(self, status):
        self._send_command([CMD_DISPLAY_ON if status else CMD_DISPLAY_OFF])


    def set_contrast(self, level):
        self._send_command([CMD_SET_CONTRASTLEVEL, level & 0xFF])


    def set_reverse_mode(self, inverse):

        self._send_command(
            [CMD_REVERSE_DISPLAY if inverse else CMD_NORMAL_DISPLAY]
        )


    @micropython.native
    def update(self):

        img = memoryview(self.image_buffer)
        vis = memoryview(self.visible_buffer)
        set_cursor = self._set_cursor
        send_data = self._send_data

        for data_idx in range(0, 2048, 128):   # page beginning indexes
            stop_idx = data_idx + 128
            diff_idx = -1       # start index of image difference, -1 means no diff found
            while data_idx < stop_idx:
                a = img[data_idx]
                b = vis[data_idx]
                if a != b and diff_idx == -1:
                    diff_idx = data_idx
                elif a == b and diff_idx != -1:
                    set_cursor(diff_idx >> 7, diff_idx & 0x7F)
                    send_data(img[diff_idx : data_idx])
                    diff_idx = -1

                data_idx += 1

            if diff_idx != -1:
                set_cursor(diff_idx >> 7, diff_idx & 0x7F)
                send_data(img[diff_idx : data_idx])

        vis[:] = img


    def update_all(self):

        data = memoryview(self.image_buffer)
        set_cursor = self._set_cursor
        send_data = self._send_data
        size = len(data)
        idx = 0
        page = 0
        while idx < size:
            set_cursor(page, 0)
            send_data(data[idx : idx + 128])
            idx += 128
            page += 1

        self.visible_buffer[:] = data


