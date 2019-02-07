# -*- coding: utf-8 -*-

from bincrafters import build_shared

import os
import platform

if __name__ == "__main__":
    builder = build_shared.get_builder()
    os.environ['LUNARG_HUMAN'] = '1'
    if platform.system() == 'Windows':
        builder.add(settings={'arch_build': 'x86'})
    builder.add(settings={'arch_build': 'x86_64'})
    builder.run()
