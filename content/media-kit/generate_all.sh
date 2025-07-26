#!/bin/bash

# Comprehensive Logo Generation Script for Post Fiat Media Kit
# This script generates PNG logos and favicon.ico files from the SVG source

set -e  # Exit on any error

# Check if required tools are installed
if ! command -v rsvg-convert &> /dev/null; then
    echo "Error: rsvg-convert is required but not installed."
    echo "Install with: brew install librsvg"
    exit 1
fi

if ! command -v magick &> /dev/null; then
    echo "Error: ImageMagick is required but not installed."
    echo "Install with: brew install imagemagick"
    exit 1
fi

# Parse command line arguments
GENERATE_PNG=true
GENERATE_FAVICON=true
BASIC_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --png-only)
            GENERATE_FAVICON=false
            shift
            ;;
        --favicon-only)
            GENERATE_PNG=false
            shift
            ;;
        --basic)
            BASIC_ONLY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --png-only      Generate only PNG files"
            echo "  --favicon-only  Generate only favicon files"
            echo "  --basic         Generate only basic sizes (192x192, 512x512, 1280x640)"
            echo "  --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Generate everything"
            echo "  $0 --basic            # Generate basic PNG sizes + favicon"
            echo "  $0 --png-only         # Generate all PNG files only"
            echo "  $0 --favicon-only     # Generate favicon only"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Define dimensions (width x height)
if [ "$BASIC_ONLY" = true ]; then
    declare -a dimensions=(
        "192x192"
        "512x512"
        "1280x640"
    )
else
    declare -a dimensions=(
        "192x192"
        "512x512"
        "1280x640"
        "1024x1024"    # Common app icon size
        "2048x2048"    # High-res app icon
        "256x256"      # Windows favicon
        "32x32"        # Small favicon
        "16x16"        # Tiny favicon
        "180x180"      # Apple touch icon
        "1920x1080"    # HD background
        "800x400"      # Social media banner
        "1200x630"     # Facebook Open Graph
        "1500x500"     # Twitter header
    )
fi

# Define color combinations (logo_color-background_color)
declare -a color_combinations=(
    "black-transparent"
    "white-transparent"
    "black-white"
    "white-black"
)

# Source SVG file
SVG_FILE="logo.svg"

# Function to create a colored version of the SVG with proper aspect ratio
create_colored_svg() {
    local color=$1
    local bg_color=$2
    local width=$3
    local height=$4
    local temp_file=$5
    
    # Calculate the viewBox to maintain aspect ratio
    local viewbox_width=200
    local viewbox_height=200
    
    if [ "$width" != "$height" ]; then
        # For non-square dimensions, we need to adjust the viewBox
        if [ "$width" -gt "$height" ]; then
            # Landscape: increase width, keep height
            viewbox_width=$((200 * width / height))
        else
            # Portrait: increase height, keep width
            viewbox_height=$((200 * height / width))
        fi
    fi
    
    # Create a temporary SVG with the specified colors and proper aspect ratio
    cat > "$temp_file" << EOF
<svg viewBox="0 0 $viewbox_width $viewbox_height" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .logo-path { stroke: $color; stroke-width: 20; stroke-linecap: round; fill: none; }
            .logo-line { stroke: $color; stroke-width: 20; stroke-linecap: round; }
        </style>
    </defs>
    <rect width="$viewbox_width" height="$viewbox_height" fill="$bg_color"/>
    <g transform="translate($((viewbox_width/2)), $((viewbox_height/2)))">
        <path d="M-60 -60 60 60m0-120L-60 60" class="logo-path"/>
        <line x1="-60" y1="60" x2="60" y2="60" class="logo-line"/>
    </g>
</svg>
EOF
}

# Function to generate PNG from SVG
generate_png() {
    local width=$1
    local height=$2
    local logo_color=$3
    local bg_color=$4
    local output_file=$5
    local temp_svg=$6
    
    echo "Generating: $output_file (${width}x${height}, $logo_color on $bg_color)"
    
    # Set background color for rsvg-convert
    local bg_arg=""
    if [ "$bg_color" != "transparent" ]; then
        bg_arg="--background-color=$bg_color"
    fi
    
    # Generate PNG
    rsvg-convert \
        --width="$width" \
        --height="$height" \
        $bg_arg \
        --format=png \
        "$temp_svg" \
        --output="$output_file"
}

# Function to generate favicon.ico
generate_favicon() {
    local logo_color=$1
    local bg_color=$2
    local output_file=$3
    local temp_svg=$4
    
    echo "Generating: $output_file ($logo_color on $bg_color)"
    
    # Generate high-res PNG first (32x32 for better quality)
    rsvg-convert \
        --width="32" \
        --height="32" \
        --background-color="$bg_color" \
        --format=png \
        "$temp_svg" \
        --output="temp_32x32.png"
    
    # Generate 16x16 PNG
    rsvg-convert \
        --width="16" \
        --height="16" \
        --background-color="$bg_color" \
        --format=png \
        "$temp_svg" \
        --output="temp_16x16.png"
    
    # Create ICO file with multiple sizes
    magick temp_16x16.png temp_32x32.png "$output_file"
    
    # Clean up temporary PNGs
    rm -f temp_16x16.png temp_32x32.png
}

# Main generation loop
echo "Starting comprehensive logo generation..."
echo "========================================"

if [ "$GENERATE_PNG" = true ]; then
    echo ""
    echo "Generating PNG files..."
    echo "----------------------"
    
    for dimension in "${dimensions[@]}"; do
        # Parse width and height
        IFS='x' read -r width height <<< "$dimension"
        
        for combo in "${color_combinations[@]}"; do
            # Parse color combination
            IFS='-' read -r logo_color bg_color <<< "$combo"
            
            # Create output filename
            if [ "$bg_color" = "transparent" ]; then
                output_file="logo${width}x${height}-${logo_color}fill.png"
            else
                output_file="logo${width}x${height}-${logo_color}on${bg_color}.png"
            fi
            
            # Create colored SVG with current colors and proper aspect ratio
            create_colored_svg "$logo_color" "$bg_color" "$width" "$height" "temp_png.svg"
            
            # Generate PNG
            generate_png "$width" "$height" "$logo_color" "$bg_color" "$output_file" "temp_png.svg"
        done
    done
    
    # Clean up temporary PNG SVG file
    rm -f temp_png.svg
fi

if [ "$GENERATE_FAVICON" = true ]; then
    echo ""
    echo "Generating favicon files..."
    echo "--------------------------"
    
    # Define color combinations for favicons
    declare -a favicon_combinations=(
        "white-black"      # White logo on black background (primary)
        "black-white"      # Black logo on white background (alternative)
    )
    
    for combo in "${favicon_combinations[@]}"; do
        # Parse color combination
        IFS='-' read -r logo_color bg_color <<< "$combo"
        
        # Create output filename
        if [ "$logo_color" = "white" ] && [ "$bg_color" = "black" ]; then
            output_file="favicon.ico"
        else
            output_file="favicon-${logo_color}on${bg_color}.ico"
        fi
        
        # Create colored SVG for favicon
        create_colored_svg "$logo_color" "$bg_color" "32" "32" "temp_favicon.svg"
        
        # Generate favicon
        generate_favicon "$logo_color" "$bg_color" "$output_file" "temp_favicon.svg"
    done
    
    # Clean up temporary favicon SVG file
    rm -f temp_favicon.svg
    
    # Copy primary favicon to site root
    if [ -f "favicon.ico" ]; then
        cp favicon.ico ../../
        echo "Copied favicon.ico to site root directory"
    fi
fi

# Summary
echo ""
echo "Generation complete!"
if [ "$GENERATE_PNG" = true ]; then
    echo "Generated $((${#dimensions[@]} * ${#color_combinations[@]})) PNG files"
fi
if [ "$GENERATE_FAVICON" = true ]; then
    echo "Generated 2 ICO files"
fi

echo ""
echo "Files created:"
if [ "$GENERATE_PNG" = true ]; then
    ls -la logo*.png | sort
fi
if [ "$GENERATE_FAVICON" = true ]; then
    echo ""
    ls -la *.ico | sort
fi

echo ""
echo "Usage:"
if [ "$GENERATE_FAVICON" = true ]; then
    echo "- favicon.ico: Standard favicon (white on black)"
    echo "- favicon-blackonwhite.ico: Alternative favicon (black on white)"
    echo ""
    echo "Place favicon.ico in your website root directory for automatic detection."
fi 