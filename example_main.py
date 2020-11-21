
import sys, time, collections
from math import sin, cos, radians
from machine import Pin, I2C
import framebuf

import sh1107g


class Matrix(collections.namedtuple('Matrix', 'a b c d e f')):

    @micropython.native
    def __mul__(self, obj):

        if isinstance(obj, Matrix):

            a11, a21, a12, a22, a13, a23 = obj
            b11, b21, b12, b22, b13, b23 = self

            a31 = a32 = b31 = b32 = 0
            a33 = b33 = 1

            return Matrix(
                a11*b11 + a12*b21 + a13*b31, a21*b11 + a22*b21 + a23*b31,
                a11*b12 + a12*b22 + a13*b32, a21*b12 + a22*b22 + a23*b32,
                a11*b13 + a12*b23 + a13*b33, a21*b13 + a22*b23 + a23*b33
            )

        elif isinstance(obj, tuple):
            x, y = obj

            return (
                self.a * x + self.c * y + self.e,
                self.b * x + self.d * y + self.f
            )

        else:
            raise AssertionError


    @staticmethod
    def translate(dx, dy):
        return Matrix(1, 0, 0, 1, dx, dy)


    @staticmethod
    def rotate(deg):

        rad = radians(deg)
        c = cos(rad); s = sin(rad)
        return Matrix(c, s, -s, c, 0, 0)


    @staticmethod
    def scale(sx, sy):
        return Matrix(sx, 0, 0, sy, 0, 0)


hand_type_1 = (
    (0.0, -5.0, 0.0, 57.0), (0.0, -5.0, 3.0, -8.0), (0.0, -5.0, -3.0, -8.0)
)

hand_type_2 = (
    (-1.0, 0.0, 0.0, 10.0), (0.0, 0.0, 0.0, 10.0), (1.0, 0.0, 0.0, 10.0),
    (-2.0, 0.0, 0.0, 10.0), (2.0, 0.0, 0.0, 10.0)
)

hour_mark = (
    (-2, 61, 2, 61), (2, 61, 0, 55), (0, 55, -2, 61)
)


@micropython.native
def draw_thing(fb, drawing, matrix, draw_border):

    segments = []
    for x1, y1, x2, y2 in drawing:
        x1, y1 = matrix * (x1, y1)
        x2, y2 = matrix * (x2, y2)
        segments.append((int(x1), int(y1), int(x2), int(y2)))

    if draw_border:
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            for x1, y1, x2, y2 in segments:
                fb.line(x1 + ox, y1 + oy, x2 + ox, y2 + oy, 0)

    for x1, y1, x2, y2 in segments:
        fb.line(x1, y1, x2, y2, 1)


def draw_clock(fb, time_secs, text):

    center = Matrix.translate(64, 64)
    fb.fill_rect(0, 0, 128, 118, 0)

    # hour marks
    for ang in range(0, 360, 30):
        draw_thing(fb, hour_mark, Matrix.rotate(ang - time_secs / 50.0) * center, False)

    display.fill_rect(0, 118, 128, 10, 1)
    display.text(text, 64 - len(text)*8//2, 119, 0)

    hour, secs = time_secs / 3600, time_secs % 3600
    minute, secs = secs / 60, secs % 60

    # hour hand
    m = Matrix.scale(1.0, 3.0) * Matrix.rotate(-180 + hour / 12 * 360) * center
    draw_thing(fb, hand_type_2, m, False)

    # minute hand
    m = Matrix.scale(1.0, 4.3) * Matrix.rotate(-180 + minute / 60 * 360) * center
    draw_thing(fb, hand_type_2, m, False)

    # second hand
    m = Matrix.rotate(-180 + secs / 60 * 360) * center
    draw_thing(fb, hand_type_1, m, True)


if __name__ == '__main__':

    i2c = I2C(freq=400000, scl=Pin(22), sda=Pin(21))
    display = sh1107g.SH1107G(i2c)
    display.set_contrast(50)

    while True:

        t = time.localtime()

        draw_clock(
            display,
            time.ticks_ms() / 1000,
            '{:2d}{}{:02d}'.format(t[3], ':' if t[5] % 2 else ' ', t[4])
        )
        display.update()

        time.sleep(0.1)


