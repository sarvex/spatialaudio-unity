# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#!/usr/bin/env python3
import sys
# Prevent Python from generating .pyc files
sys.dont_write_bytecode = True

import argparse
import constants
import githelpers
import os
import oshelpers
import stage
import subprocess

def create_unity_package(unity_path, project_dir, package_location, plugin_name, package_version):
    git_root = oshelpers.fixpath(githelpers.get_root())
    unity_project_full_path = oshelpers.fixpath(git_root, project_dir)
    unity_package_full_path = oshelpers.fixpath(
        package_location, f"{plugin_name}.{package_version}.unitypackage"
    )
    unity_package_creation_command = f"{unity_path} -BatchMode -Quit -ProjectPath {unity_project_full_path} -ExportPackage Assets {unity_package_full_path}"
    result = subprocess.run(unity_package_creation_command)
    print(">>>> Unity LOG <<<<")
    editorLog = os.path.join(os.environ['userprofile'], "AppData", "Local", "Unity", "Editor", "Editor.Log")
    with open(editorLog, 'r') as myfile:
        data = myfile.read()
    print(data)
    print(editorLog)
    if (result.returncode != 0):
        print("Package generation failed!")
        print(result.stdout)
        print(result.stderr)
    else:
        print(f"Package successfully generated: {unity_package_full_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--unitydir", help="Directory where Unity.exe is located")
    parser.add_argument("-s", "--stage", help="Copies built spatializer binaries from passed artifacts directory to Unity project locations", type=str.lower)
    parser.add_argument("-o", "--output", help="Output location, will use default build/unity location if unspecified", type=str.lower)
    parser.add_argument("-v", "--version", help="Semantic version string for the package", type=str.lower)
    args = parser.parse_args()

    # Copy plugin binaries to project location
    stage.stage_binaries_crossplatform(args.stage)

    git_root = oshelpers.fixpath(githelpers.get_root())

    # Default output path is under build/unity
    unity_package_location = oshelpers.fixpath(git_root, constants.build_root, "unity")
    if args.output:
        unity_package_location = args.output

    if not args.unitydir:
        sys.exit("Must specify Unity location")

    unity_exe_path = oshelpers.fixpath(os.path.join(args.unitydir, "unity.exe"))
    if not os.path.isfile(unity_exe_path):
        sys.exit("Invalid Unity path")

    if not os.path.isdir(unity_package_location):
        os.mkdir(unity_package_location)

    create_unity_package(unity_exe_path, constants.crossplatform_unity_project_dir, unity_package_location, constants.crossplatform_spatializer_plugin_name, args.version)

if __name__ == '__main__':
    main()