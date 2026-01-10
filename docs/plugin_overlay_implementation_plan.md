# Plugin Overlay Feature - Detailed Implementation Plan

## Overview

This document provides a detailed implementation plan for the **Composite Plugin** approach (Approach 1 from the research document). This plan is ready for implementation once approved.

## Implementation Phases

### Phase 1: Core Utilities (Foundation)

**Goal**: Create reusable image composition utilities that can be used by any plugin.

#### 1.1 Add Composition Functions to `utils/image_utils.py`

```python
def calculate_overlay_dimensions(base_dimensions, region_config):
    """
    Calculate overlay dimensions based on region configuration.
    
    Args:
        base_dimensions: (width, height) tuple of base image
        region_config: dict with 'width' and 'height' (can be int or percentage string)
    
    Returns:
        (width, height) tuple for overlay
    
    Examples:
        >>> calculate_overlay_dimensions((1000, 800), {"width": 400, "height": 300})
        (400, 300)
        
        >>> calculate_overlay_dimensions((1000, 800), {"width": "40%", "height": "30%"})
        (400, 240)
    """

def calculate_overlay_position(base_dimensions, overlay_dimensions, position, margin=20):
    """
    Calculate (x, y) coordinates for overlay placement.
    
    Args:
        base_dimensions: (width, height) tuple of base image
        overlay_dimensions: (width, height) tuple of overlay image
        position: string ('top-left', 'top-right', 'bottom-left', 'bottom-right', 'center')
        margin: pixel margin from edges
    
    Returns:
        (x, y) tuple for overlay position
    """

def composite_images(base, overlay, position='bottom-left', region=None, 
                    opacity=1.0, margin=20, background_color=None):
    """
    Composite overlay image onto base image.
    
    Args:
        base: PIL Image (base/background)
        overlay: PIL Image to overlay
        position: Position string or (x, y) tuple
        region: Optional dict with width/height for resizing overlay
        opacity: Float 0.0-1.0 for overlay transparency
        margin: Pixel margin from edges when using position strings
        background_color: Optional background color for overlay (for transparency)
    
    Returns:
        PIL Image with overlay composited
    """
```

**Tests**: Create `tests/test_image_utils.py` with comprehensive test cases.

---

### Phase 2: Composite Plugin Implementation

**Goal**: Create a new composite plugin that combines multiple child plugins.

#### 2.1 Directory Structure

```
src/plugins/composite/
├── composite.py          # Main plugin class
├── icon.png              # Plugin icon
├── settings.html         # Configuration UI
├── plugin-info.json      # Plugin metadata
└── render/               # Optional HTML/CSS for preview
    └── preview.html
```

#### 2.2 Plugin Info (`plugin-info.json`)

```json
{
    "display_name": "Composite",
    "id": "composite",
    "class": "CompositePlugin"
}
```

#### 2.3 Core Plugin Class (`composite.py`)

```python
from plugins.base_plugin.base_plugin import BasePlugin
from plugins.plugin_registry import get_plugin_instance
from utils.image_utils import composite_images, calculate_overlay_dimensions
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class CompositePlugin(BasePlugin):
    """
    Composite plugin that overlays multiple plugins onto a base image.
    
    Configuration format:
    {
        "base_plugin": {
            "plugin_id": "image_album",
            "plugin_settings": {...}
        },
        "overlays": [
            {
                "plugin_id": "weather",
                "plugin_settings": {...},
                "position": "bottom-left",
                "region": {"width": "40%", "height": "30%"},
                "opacity": 0.9,
                "margin": 20,
                "background_color": "#ffffff"
            }
        ]
    }
    """
    
    def generate_image(self, settings, device_config):
        # Validate configuration
        if 'base_plugin' not in settings:
            raise RuntimeError("Base plugin configuration is required.")
        
        # Generate base image
        base_image = self._generate_child_plugin_image(
            settings['base_plugin'], 
            device_config
        )
        
        # Apply overlays
        overlays = settings.get('overlays', [])
        for i, overlay_config in enumerate(overlays):
            try:
                overlay_image = self._generate_child_plugin_image(
                    overlay_config, 
                    device_config
                )
                
                base_image = composite_images(
                    base=base_image,
                    overlay=overlay_image,
                    position=overlay_config.get('position', 'bottom-left'),
                    region=overlay_config.get('region'),
                    opacity=overlay_config.get('opacity', 1.0),
                    margin=overlay_config.get('margin', 20),
                    background_color=overlay_config.get('background_color')
                )
            except Exception as e:
                logger.error(f"Failed to apply overlay {i}: {str(e)}")
                # Continue with other overlays even if one fails
        
        return base_image
    
    def _generate_child_plugin_image(self, plugin_config, device_config):
        """Generate image from a child plugin configuration."""
        plugin_id = plugin_config.get('plugin_id')
        if not plugin_id:
            raise RuntimeError("Plugin ID is required in child configuration.")
        
        # Get plugin instance
        plugin_meta = device_config.get_plugin(plugin_id)
        if not plugin_meta:
            raise RuntimeError(f"Plugin '{plugin_id}' not found.")
        
        plugin = get_plugin_instance(plugin_meta)
        
        # Generate image with settings
        plugin_settings = plugin_config.get('plugin_settings', {})
        return plugin.generate_image(plugin_settings, device_config)
```

#### 2.4 Settings Template (`settings.html`)

This will be a comprehensive UI allowing users to:
- Select base plugin from dropdown
- Configure base plugin settings (dynamic form)
- Add/remove overlay layers
- Configure each overlay (plugin, position, size, opacity)
- Preview the composite (optional, advanced)

**Note**: This is the most complex part and may need iteration based on UX feedback.

---

### Phase 3: Testing

**Goal**: Ensure reliability and correctness of the composite plugin.

#### 3.1 Unit Tests (`tests/test_composite_plugin.py`)

```python
import pytest
from PIL import Image
from src.plugins.composite.composite import CompositePlugin

class TestCompositePlugin:
    def test_basic_composition(self):
        """Test basic two-layer composition."""
        # Setup
        # Create test images
        # Configure composite settings
        # Generate image
        # Verify result
        
    def test_multiple_overlays(self):
        """Test compositing multiple overlays."""
        
    def test_overlay_positioning(self):
        """Test different position options."""
        
    def test_overlay_opacity(self):
        """Test opacity blending."""
        
    def test_region_sizing(self):
        """Test percentage and absolute sizing."""
        
    def test_missing_base_plugin(self):
        """Test error handling for missing base."""
        
    def test_invalid_overlay_plugin(self):
        """Test graceful handling of invalid overlay."""
```

#### 3.2 Integration Tests

Test with actual plugins:
- Weather + Image Gallery
- Clock + Background Image
- Multiple overlays

---

### Phase 4: Documentation

**Goal**: Enable users to create and configure composite plugins.

#### 4.1 Update `docs/building_plugins.md`

Add new section:

```markdown
## Creating Composite Layouts

The Composite plugin allows you to overlay multiple plugins onto a single display.

### Basic Example

Create a weather overlay on gallery images:

1. Add Composite plugin to playlist
2. Configure base plugin (Image Gallery)
3. Add overlay (Weather plugin)
4. Set position (bottom-left)
5. Adjust size (40% width, 30% height)
6. Set opacity (0.9 for slight transparency)

### Configuration Options

...
```

#### 4.2 Create Example Configurations

Add to documentation:
- Weather + Gallery
- Clock + Background
- Multi-info Dashboard

---

## Implementation Timeline

### Week 1: Core Utilities
- Day 1-2: Implement composition utilities
- Day 3: Unit tests for utilities
- Day 4-5: Code review and refinement

### Week 2: Composite Plugin
- Day 1-2: Implement CompositePlugin class
- Day 3-4: Create settings UI template
- Day 5: Integration testing

### Week 3: Testing & Documentation
- Day 1-2: Comprehensive testing
- Day 3-4: Documentation updates
- Day 5: Final review and polish

## Success Criteria

1. ✅ Utilities can composite images with all position options
2. ✅ Utilities support percentage and absolute sizing
3. ✅ Utilities handle opacity correctly
4. ✅ CompositePlugin can load and combine multiple child plugins
5. ✅ Error handling prevents crashes from invalid configurations
6. ✅ Settings UI allows easy configuration of composite layouts
7. ✅ Tests achieve >80% code coverage
8. ✅ Documentation includes clear examples
9. ✅ Example: Weather overlay on gallery images works as expected
10. ✅ Performance: Compositing adds <2 seconds to refresh time

## Alternative Quick Start (MVP)

If full implementation is too ambitious, start with a simplified version:

### Minimal Viable Product (MVP)

**Scope**: Single overlay only, fixed positions only, no UI configuration

1. Hardcode a "WeatherGallery" plugin
2. Support only bottom-left and bottom-right positions
3. Fixed overlay size (400x300)
4. No settings UI - use JSON configuration only
5. Test with weather + gallery only

This can be implemented in 2-3 days and validate the approach before investing in the full solution.

## Open Questions

1. **Caching**: Should we cache child plugin outputs when they haven't changed?
2. **Refresh Control**: How do we handle different refresh intervals for base vs overlays?
3. **Preview**: Should settings UI show a live preview of the composite?
4. **Templates**: Should we provide pre-built composite templates?
5. **Migration**: How do we help users migrate from single plugins to composites?

## Dependencies

- PIL/Pillow (already installed)
- No new external dependencies required

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Complex UI | Start with simple JSON config, iterate on UI |
| Performance issues | Profile and optimize composition utilities |
| Child plugin errors | Wrap in try/catch, continue with other overlays |
| User confusion | Provide clear documentation and examples |
| Over-engineering | Implement MVP first, gather feedback |

## Next Steps

1. Review this plan with team
2. Get approval on approach
3. Create feature branch
4. Implement Phase 1 (utilities)
5. Get feedback after each phase
6. Iterate based on user testing

---

**Document Status**: Ready for Review
**Last Updated**: 2026-01-10
**Author**: Copilot Agent
