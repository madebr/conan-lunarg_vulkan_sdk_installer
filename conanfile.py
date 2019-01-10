# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools


class LunarGVulkanSDKConan(ConanFile):
    name = 'lunarg_vulkan_sdk'
    version = '1.1.92.1'
    description = 'The LunarG Vulkan SDK provides the development and runtime components required to build, run, and debug Vulkan applications.'
    url = 'https://github.com/bincrafters/conan-lunarg_vulkan_sdk'
    homepage = 'https://vulkan.lunarg.com/sdk/home'
    author = 'bincrafters <bincrafters@gmail.com>'

    license = 'Various'
    exports = ['LICENSE.md']

    settings = 'os', 'arch'

    def source(self):
        prefix_url = 'https://sdk.lunarg.com/sdk/download/{version}'.format(version=self.version)
        win_url = '{prefix}/windows/VulkanSDK-{version}-Installer.exe'.format(prefix=prefix_url, version=self.version)
        win_sha256 = '601c019b8dca1ecece47be279c7a77056fe081d2b5f1804ac9c5d80b7bef7fea'
        mac_url = '{prefix}/mac/vulkansdk-macos-{version}.tar.gz'.format(prefix=prefix_url, version=self.version)
        mac_sha256 = '1dc5c758ba83cc0b1e3baa533a5b2052afa378df87a84ee3e56ab6d97df12865'
        lin_url = '{prefix}/linux/vulkansdk-linux-x86_64-{version}.tar.gz'.format(prefix=prefix_url, version=self.version)
        lin_sha256 = 'bbbdce02334e078e54bd1d796a1d983073054f57379ecfb89aa4194020ad4c32'

        if self.settings.os == 'Windows':
            tools.download(win_url, 'vulkan-installer.exe')
            tools.check_sha256('vulkan-installer.exe', win_sha256)
        else:
            if self.settings.os == 'Linux':
                url = lin_url
                sha256 = lin_sha256
            elif self.settings.os == 'Macos':
                url = mac_url
                sha256 = mac_sha256
            tools.get(url, sha256=sha256, keep_permissions=True)

    def build(self):
        if self.settings.os == 'Windows':
            self.run('"{}" /S'.format(os.path.join(self.source_folder, 'vulkan-installer.exe')))

    def package(self):
        if self.settings.os == 'Windows':
            location = 'C:\\VulkanSDK\\{version}'.format(version=self.version)
            lic_folder = location
            lic_name = 'LICENSE.txt'
            inc_folder = os.path.join(location, 'Include')
            if self.settings.arch == 'x86':
                lib_folder = os.path.join(location, 'Lib32')
            elif self.settings.arch == 'x86_64':
                lib_folder = os.path.join(location, 'Lib')
        else:
            lic_folder = self.source_folder
            lic_name = 'LICENSE'
            inc_folder = os.path.join(self.source_folder, 'include')
            if self.settings.arch == 'x86':
                lib_folder = os.path.join(self.source_folder, 'lib32')
            elif self.settings.arch == 'x86_64':
                lib_folder = os.path.join(self.source_folder, 'lib')

        self.copy(pattern=lic_name, dst='licenses', src=lic_folder)
        self.copy(pattern='*', dst='include', src=inc_folder)
        self.copy(pattern='*', dst='lib', src=lib_folder)

    def package_info(self):
        self.cpp_info.libs = ['vulkan-1']
