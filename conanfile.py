# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.util.env_reader import get_env
import tempfile


class LunarGVulkanSDKInstallerConan(ConanFile):
    name = 'vulkan_lunarg_installer'
    version = '1.1.97.0'
    description = 'The LunarG Vulkan SDK provides the development and runtime components required to build, run, and debug Vulkan applications.'
    url = 'https://github.com/bincrafters/conan-lunarg_vulkan_sdk'
    homepage = 'https://vulkan.lunarg.com/sdk/home'
    topics = ('conan', 'vulkan', 'vk', 'rendering', 'metal', 'moltenvk')
    author = 'bincrafters <bincrafters@gmail.com>'
    no_copy_source = True

    license = 'Various'
    exports = ['LICENSE.md']

    settings = 'os_build', 'arch_build'

    def build(self):
        prefix_url = 'https://sdk.lunarg.com/sdk/download/{version}'.format(version=self.version)
        win_name = 'VulkanSDK-{version}-Installer.exe'.format(version=self.version)
        win_url = '{prefix}/windows/{name}'.format(prefix=prefix_url, name=win_name)
        win_sha256 = 'c46584e9df78b40dd3cddda006ebace9917be25353961472f479c7bd0abd13ee'
        mac_name = 'vulkansdk-macos-{arch}-{version}.tar.gz'.format(arch=self.settings.arch_build, version=self.version)
        mac_url = '{prefix}/mac/{name}'.format(prefix=prefix_url, name=mac_name)
        mac_sha256 = 'a84a6432e049bb7621a6bf2bf643fa19c863fa4f3d8e6ddac9a102036c461edd'
        lin_name = 'vulkansdk-linux-{arch}-{version}.tar.gz'.format(arch=self.settings.arch_build, version=self.version)
        lin_url = '{prefix}/linux/{name}'.format(prefix=prefix_url, name=lin_name)
        lin_sha256 = '9430951ca2fa4d9daca3b4394c15465727de0d31290cd7b5e686cdd6dc47dc8d'

        if self.settings.os_build == 'Windows':
            url = win_url
            name = win_name
            sha256 = win_sha256
        elif self.settings.os_build == 'Linux':
            url = lin_url
            sha256 = lin_sha256
            name = lin_name
        elif self.settings.os_build == 'Macos':
            url = mac_url
            sha256 = mac_sha256
            name = mac_name

        targetdlfn = os.path.join(tempfile.gettempdir(), name)

        # cache downloads because lunarg has rate limit of 5 downloads per url per 24h
        # (this ratelimit can be overridden by adding "?Human=true" to the url
        if get_env('LUNARG_HUMAN', False):
            url += '?Human=true'
        if os.path.exists(targetdlfn) and not get_env('LUNARG_FORCE_DOWNLOAD', False):
            self.output.info('Skipping download. Using cached {}'.format(targetdlfn))
        else:
            self.output.info('Downloading sdk from {} to {}'.format(url, targetdlfn))
            tools.download(url, targetdlfn)
        tools.check_sha256(targetdlfn, sha256)

        if self.settings.os_build == 'Windows':
            self.run('"{}" /S'.format(targetdlfn))
        else:
            tools.untargz(targetdlfn, self.build_folder)
            if self.settings.os_build == 'Linux':
                os.rename(self.version, 'vulkansdk')
            else:
                os.rename('vulkansdk-macos-{version}'.format(version=self.version), 'vulkansdk')

        if self.settings.os_build == 'Macos':
            possible_broken_symlink = os.path.join(self.build_folder, 'vulkansdk', 'macOS', 'lib', 'libshaderc_shared.dylib')
            if not os.path.exists(possible_broken_symlink):
                try:
                    os.remove(possible_broken_symlink)
                except FileNotFoundError:
                    pass
                
    def package(self):
        if self.settings.os_build == 'Windows':
            base_folder = 'C:\\VulkanSDK\\{version}'.format(version=self.version)
            if self.settings.arch_build == 'x86':
                bin_folder = os.path.join(base_folder, 'Bin32')
                tools_folder = os.path.join(base_folder, 'Tools32')
            elif self.settings.arch_build == 'x86_64':
                bin_folder = os.path.join(base_folder, 'Bin')
                tools_folder = os.path.join(base_folder, 'Tools')
            self.copy(pattern='*.exe', dst='bin', src=bin_folder)
            self.copy(pattern='*', dst='bin/tools', src=tools_folder)
            self.copy(pattern='LICENSE.txt', dst='licenses', src=base_folder)
        elif self.settings.os_build == 'Linux':
            base_folder = os.path.join(self.build_folder, 'vulkansdk')
            self.copy(pattern='LICENSE.txt', dst='licenses', src=base_folder)
            bin_folder = os.path.join(base_folder, str(self.settings.arch_build), 'bin')
            self.copy(pattern='*', dst='bin', src=bin_folder)
        elif self.settings.os_build == 'Macos':
            base_folder = os.path.join(self.build_folder, 'vulkansdk', 'macOS')
            self.copy(pattern='*', dst='bin', src=os.path.join(base_folder, 'bin'))


    def package_info(self):
        if self.settings.os_build != 'Windows' and self.settings.arch_build != 'x86_64':
            raise ConanInvalidConfiguration('LunarG Vulkan SDK only supports 64-bit')

        self.cpp_info.bindirs = ['bin']
        if self.settings.os_build == 'Windows':
            self.cpp_info.bindirs.append('bin/tools')

        for bindir in self.cpp_info.bindirs:
            self.output.info('Appending PATH environment variable: {}'.format(bindir))
            self.env_info.PATH.append(bindir)
