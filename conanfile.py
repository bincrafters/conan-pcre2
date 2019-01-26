#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class PCREConan(ConanFile):
    name = "pcre2"
    version = "10.32"
    url = "https://github.com/bincrafters/conan-pcre2"
    homepage = "https://www.pcre.org/"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Perl Compatible Regular Expressions"
    license = "BSD"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_bzip2": [True, False],
        "build_pcre2_8": [True, False],
        "build_pcre2_16": [True, False],
        "build_pcre2_32": [True, False],
        "support_jit": [True, False]
    }
    default_options = ("shared=False",
                       "fPIC=True",
                       "with_bzip2=True",
                       "build_pcre2_8=True",
                       "build_pcre2_16=True",
                       "build_pcre2_32=True",
                       "support_jit=True")
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    requires = "zlib/1.2.11@conan/stable"

    def source(self):
        source_url = "https://ftp.pcre.org"
        tools.get("{0}/pub/pcre/pcre2-{1}.tar.gz".format(source_url, self.version),
                  sha256="9ca9be72e1a04f22be308323caa8c06ebd0c51efe99ee11278186cafbc4fe3af")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_bzip2:
            self.requires.add("bzip2/1.0.6@conan/stable")

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PCRE2_BUILD_TESTS"] = False
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            runtime = not self.options.shared and "MT" in self.settings.compiler.runtime
            cmake.definitions["PCRE2_STATIC_RUNTIME"] = runtime
        cmake.definitions["PCRE2_DEBUG"] = self.settings.build_type == "Debug"
        cmake.definitions["PCRE2_BUILD_PCRE2_8"] = self.options.build_pcre2_8
        cmake.definitions["PCRE2_BUILD_PCRE2_16"] = self.options.build_pcre2_16
        cmake.definitions["PCRE2_BUILD_PCRE2_32"] = self.options.build_pcre2_32
        cmake.definitions["PCRE2_SUPPORT_JIT"] = self.options.support_jit
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()
        cmake.patch_config_paths()
        self.copy(pattern="LICENCE", dst="licenses", src=self.source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("PCRE2_STATIC")
