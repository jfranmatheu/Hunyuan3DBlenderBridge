import os
import re
from pathlib import Path

PYTHON_VERSION = "3.13"
REQUIREMENTS = (
    "imageio",
    "numpy",
    "pillow",
)
PLATFORMS = (
    "win_amd64",
    "macosx_11_0_arm64",
    "manylinux_2_28_x86_64",
    "win_amd64",
    "macosx_10_13_x86_64"
)


def download_requirements():
    # Download wheels for each requirement
    for req in REQUIREMENTS:
        for platform in PLATFORMS:
            os.system(f"pip download {req} --dest ./hunyuan3d_blender/wheels --only-binary=:all: --python-version={PYTHON_VERSION} --platform={platform}")

def update_manifest():
    # Setup paths relative to this script
    script_dir = Path(__file__).parent
    manifest_path = script_dir / "hunyuan3d_blender" / "blender_manifest.toml"
    wheels_dir = script_dir / "hunyuan3d_blender" / "wheels"

    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        return

    if not wheels_dir.exists():
        print(f"Error: Wheels directory not found at {wheels_dir}")
        return

    # Get all .whl files
    wheels = sorted([f.name for f in wheels_dir.glob("*.whl")])
    
    if not wheels:
        print("Warning: No wheels found.")
    
    # Format for TOML
    # The manifest is in 'hunyuan3d_blender/', wheels are in 'hunyuan3d_blender/wheels/'
    # So relative path is './wheels/'
    wheel_lines = []
    for wheel in wheels:
        wheel_lines.append(f'  "./wheels/{wheel}",')
    
    new_wheels_content = "wheels = [\n" + "\n".join(wheel_lines) + "\n]"

    # Read manifest
    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace wheels section using regex
    # Matches wheels = [ ... ] across multiple lines
    # We use non-greedy match .*? to find the closing bracket
    pattern = r"wheels\s*=\s*\[.*?\]"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        new_content = re.sub(pattern, new_wheels_content, content, flags=re.DOTALL)
        print("Updated existing wheels section.")
    else:
        # If not found, append it
        print("Wheels section not found, appending to end of file...")
        new_content = content.rstrip() + "\n\n" + new_wheels_content + "\n"

    # Write back
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"Successfully updated {manifest_path} with {len(wheels)} wheels:")
    for w in wheels:
        print(f" - {w}")

if __name__ == "__main__":
    download_requirements()
    update_manifest()
