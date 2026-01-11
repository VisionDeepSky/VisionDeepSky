from PIL import Image
import os
import math
import sys

def divide_image_into_patches(image_path, target_N=9, output_dir=None):
    """
    Divide an image into N square patches (P×P) and save them.
    Targets a specific number of patches (default: 9 for a 3x3 grid).
    
    Args:
        image_path: Path to the input image
        target_N: Target number of patches (default: 9)
        output_dir: Directory to save patches
    
    Returns:
        Number of patches created (N)
    """
    # Check if image file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image file not found: {image_path}\n"
            f"Please ensure the image file exists at the specified path."
        )
    
    # Load the image
    img = Image.open(image_path)
    width, height = img.size
    
    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = os.path.dirname(image_path) or '.'
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Find the best grid arrangement for target_N patches
    # For target_N = 9, we want a 3x3 grid
    # Find factors of target_N to determine grid dimensions
    best_arrangement = None
    best_score = float('inf')
    
    # Try different grid arrangements (num_patches_y x num_patches_x = target_N)
    for num_patches_y in range(1, int(math.sqrt(target_N)) + 2):
        if target_N % num_patches_y == 0:
            num_patches_x = target_N // num_patches_y
            
            # Calculate patch dimensions for this arrangement
            patch_h = height // num_patches_y
            patch_w = width // num_patches_x
            
            # We want square patches P×P, so use the minimum to ensure square patches
            patch_size_candidate = min(patch_h, patch_w)
            
            # Verify this gives exactly target_N patches
            actual_num_x = width // patch_size_candidate
            actual_num_y = height // patch_size_candidate
            actual_N = actual_num_x * actual_num_y
            
            # Score: prefer exact match, then prefer square patches
            if actual_N == target_N:
                score = abs(patch_h - patch_w)  # Prefer square patches when N matches
            else:
                score = abs(actual_N - target_N) * 1000 + abs(patch_h - patch_w)  # Heavily penalize wrong N
            
            if score < best_score and patch_size_candidate > 0:
                best_score = score
                best_arrangement = (num_patches_y, num_patches_x, patch_size_candidate)
    
    if best_arrangement is None:
        # Fallback: use 3x3 grid for 9 patches
        num_patches_y = 3
        num_patches_x = 3
        # For 3x3, calculate patch dimensions and use the smaller for square patches
        patch_w = width // 3
        patch_h = height // 3
        patch_size = min(patch_w, patch_h)
    else:
        num_patches_y, num_patches_x, patch_size = best_arrangement
    
    # For exactly target_N patches, force the grid dimensions
    # For 9 patches, use 3x3 grid with square patches
    if target_N == 9:
        num_patches_y = 3
        num_patches_x = 3
        # Calculate patch dimensions for 3x3 grid
        patch_w = width // num_patches_x
        patch_h = height // num_patches_y
        # Use the minimum to ensure square patches (3x3 = 9 patches)
        patch_size = min(patch_w, patch_h)
    
    # Extract and save exactly target_N patches
    patch_count = 0
    for i in range(num_patches_y):
        for j in range(num_patches_x):
            # Stop if we've created enough patches
            if patch_count >= target_N:
                break
                
            # Calculate crop coordinates for square patches
            left = j * patch_size
            top = i * patch_size
            right = min(left + patch_size, width)
            bottom = min(top + patch_size, height)
            
            # Crop the patch
            patch = img.crop((left, top, right, bottom))
            
            # Resize to exact square if needed
            if patch.size[0] != patch_size or patch.size[1] != patch_size:
                patch = patch.resize((patch_size, patch_size), Image.Resampling.LANCZOS)
            
            # Save the patch
            patch_filename = f"{base_name}_patch_{i}_{j}.png"
            patch_path = os.path.join(output_dir, patch_filename)
            patch.save(patch_path)
            
            patch_count += 1
        
        if patch_count >= target_N:
            break
    
    print(f"Created {patch_count} square patches from image ({width}x{height})")
    print(f"N = {patch_count} (target: {target_N})")
    print(f"Patch size P = {patch_size}x{patch_size} pixels")
    print(f"Patch layout: {num_patches_y}x{num_patches_x} = {num_patches_y * num_patches_x} patches")
    print(f"Verification: N = (H//P) * (W//P) = ({height}//{patch_size}) * ({width}//{patch_size}) = {num_patches_y} * {num_patches_x} = {num_patches_y * num_patches_x}")
    
    return patch_count


if __name__ == "__main__":
    # Configuration
    image_path = "drone_01.JPG"
    target_N = 9  # Target number of patches (3x3 grid)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_full_path = os.path.join(script_dir, image_path)
    
    # Check if image exists before proceeding
    print(f"Looking for image at: {image_full_path}")
    if not os.path.exists(image_full_path):
        print(f"ERROR: Image file not found at: {image_full_path}")
        print(f"Please ensure 'drone_01.JPG' exists in the DenseUAV directory.")
        sys.exit(1)
    
    # Create patch directory
    patch_dir = os.path.join(script_dir, "patch")
    
    # Divide image into square patches (targeting exactly target_N patches)
    patches_created = divide_image_into_patches(image_full_path, target_N=target_N, output_dir=patch_dir)
    
    print(f"\nTotal square patches created: {patches_created} (target: {target_N})")
