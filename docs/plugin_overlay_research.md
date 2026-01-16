# Plugin Image Overlay Feature - Research Document

## Problem Statement

Enable different plugin images to be overlayed over existing images. For example, overlaying the weather plugin result over the lower left part of images from the image gallery plugin.

## Current Architecture Analysis

### Image Generation Flow
1. **RefreshTask** determines which plugin to refresh based on active playlists
2. **Plugin.generate_image()** creates a full-screen PIL Image
3. **DisplayManager.display_image()** sends the image to the e-ink display
4. Each plugin generates a complete image that fills the entire display

### Existing Composition Patterns
- **Clock plugin** uses `Image.alpha_composite()` to layer text over backgrounds
- **Image utilities** provide `pad_image_blur()` for compositing images
- PIL/Pillow fully supports alpha blending and image composition

### Current Limitations
- Plugins operate independently, each generating full images
- No mechanism to combine outputs from multiple plugins
- Playlist system shows one plugin at a time
- No concept of layers or regions in the display

## Use Cases

### Primary Use Case
**Weather Overlay on Gallery Images**
- Background: Random image from gallery plugin
- Overlay: Weather information in corner/region
- Position: Lower left, lower right, top left, or top right
- Benefits: Aesthetic backgrounds with functional information

### Additional Use Cases
1. **Clock + Background Image**: Time display over artwork
2. **Calendar + Weather**: Combined information dashboard
3. **RSS + Stock Ticker**: Multiple information streams
4. **Todo List + Motivational Image**: Productivity display

## Implementation Approaches

### Approach 1: Composite Plugin Type

**Description**: Create a new "composite" plugin type that combines multiple child plugins.

**Architecture**:
```python
class CompositePlugin(BasePlugin):
    def generate_image(self, settings, device_config):
        # Generate base layer from first plugin
        base_image = self._generate_child_plugin(settings['base_plugin'])
        
        # Generate and overlay additional layers
        for overlay in settings['overlays']:
            overlay_image = self._generate_child_plugin(overlay['plugin'])
            overlay_image = self._resize_for_region(overlay_image, overlay['region'])
            base_image = self._composite(base_image, overlay_image, overlay['position'])
        
        return base_image
```

**Configuration Example**:
```json
{
    "plugin_id": "composite",
    "name": "Weather + Gallery",
    "plugin_settings": {
        "base_plugin": {
            "plugin_id": "image_album",
            "settings": {...}
        },
        "overlays": [
            {
                "plugin_id": "weather",
                "settings": {...},
                "region": {"width": "40%", "height": "30%"},
                "position": "bottom-left",
                "opacity": 0.9
            }
        ]
    }
}
```

**Pros**:
- Clean separation of concerns
- Reuses existing plugins without modification
- Flexible - can combine any plugins
- Easy to add new composite types

**Cons**:
- Requires creating a new plugin type
- More complex configuration
- May need to instantiate multiple plugins per refresh

---

### Approach 2: Plugin Settings Enhancement

**Description**: Extend BasePlugin to support optional overlay capabilities.

**Architecture**:
```python
class BasePlugin:
    def generate_image(self, settings, device_config):
        # Existing implementation
        image = self._create_main_image(settings, device_config)
        
        # New overlay support
        if 'overlays' in settings:
            for overlay_config in settings['overlays']:
                overlay = self._load_overlay_plugin(overlay_config)
                overlay_image = overlay.generate_image(...)
                image = self._apply_overlay(image, overlay_image, overlay_config)
        
        return image
```

**Configuration Example**:
```json
{
    "plugin_id": "image_album",
    "name": "Gallery with Weather",
    "plugin_settings": {
        "album": "Nature",
        "overlays": [
            {
                "plugin_id": "weather",
                "plugin_settings": {...},
                "layout": {
                    "position": "bottom-left",
                    "width": 400,
                    "height": 300,
                    "opacity": 0.85,
                    "padding": 20
                }
            }
        ]
    }
}
```

**Pros**:
- Extends existing plugin system naturally
- Can be added to any plugin
- Backwards compatible (overlays are optional)
- Simpler user configuration

**Cons**:
- Adds complexity to BasePlugin
- Every plugin inherits overlay logic (even if unused)
- May cause recursive plugin loading issues

---

### Approach 3: Post-Processing Pipeline

**Description**: Add a post-processing step in RefreshTask to apply overlays after image generation.

**Architecture**:
```python
class RefreshTask:
    def _apply_post_processing(self, image, plugin_instance, device_config):
        # Check for overlay configuration
        overlay_config = plugin_instance.settings.get('post_overlays')
        if not overlay_config:
            return image
        
        # Apply each overlay in sequence
        for overlay in overlay_config:
            overlay_plugin = get_plugin_instance(overlay['plugin_config'])
            overlay_image = overlay_plugin.generate_image(...)
            image = composite_images(image, overlay_image, overlay['layout'])
        
        return image
```

**Configuration Example**:
```json
{
    "plugin_id": "image_album",
    "plugin_settings": {
        "album": "Nature",
        "post_overlays": [
            {
                "plugin_id": "weather",
                "plugin_config_name": "default_weather",
                "region": "bottom-left",
                "size": {"width": 400, "height": 300},
                "margin": 20
            }
        ]
    }
}
```

**Pros**:
- Separates overlay logic from plugin implementation
- Centralized in RefreshTask
- No plugin changes required
- Easy to add global overlay features

**Cons**:
- RefreshTask becomes more complex
- Harder to preview overlays in plugin settings
- Less flexible per-plugin customization

---

### Approach 4: Layout System (Advanced)

**Description**: Implement a grid/region-based layout system inspired by the roadmap "Modular layouts to mix and match plugins".

**Architecture**:
```python
class LayoutManager:
    def render_layout(self, layout_config, device_config):
        canvas = Image.new('RGB', device_config.get_resolution())
        
        for region in layout_config['regions']:
            plugin = get_plugin_instance(region['plugin_config'])
            plugin_image = plugin.generate_image(region['settings'], device_config)
            plugin_image = resize_to_region(plugin_image, region['bounds'])
            canvas.paste(plugin_image, region['position'])
        
        return canvas
```

**Configuration Example**:
```json
{
    "layout_type": "grid",
    "regions": [
        {
            "id": "main",
            "bounds": {"x": 0, "y": 0, "width": "100%", "height": "100%"},
            "plugin_id": "image_album",
            "z_index": 0
        },
        {
            "id": "weather",
            "bounds": {"x": 20, "y": "70%", "width": 400, "height": 300},
            "plugin_id": "weather",
            "z_index": 1
        }
    ]
}
```

**Pros**:
- Most flexible and powerful approach
- Aligns with roadmap vision
- Supports complex layouts
- Clear separation of layout from plugins

**Cons**:
- Most complex to implement
- Requires significant refactoring
- Steeper learning curve for users
- May be overkill for simple overlay use case

---

## Comparison Matrix

| Criteria | Approach 1: Composite Plugin | Approach 2: Plugin Enhancement | Approach 3: Post-Processing | Approach 4: Layout System |
|----------|----------------------------|------------------------------|----------------------------|-------------------------|
| **Complexity** | Medium | Low-Medium | Medium | High |
| **Flexibility** | High | Medium | Medium | Very High |
| **Backwards Compat** | Yes | Yes | Yes | No (major change) |
| **Code Changes** | New plugin + utils | BasePlugin + utils | RefreshTask + utils | Major refactor |
| **User Experience** | Good | Very Good | Good | Excellent (after learning) |
| **Maintenance** | Easy | Medium | Easy | Complex |
| **Performance** | Good | Good | Good | Good |
| **Testing** | Easy | Medium | Easy | Complex |
| **Roadmap Alignment** | Partial | No | No | Full |

## Recommended Approach

### Primary Recommendation: **Approach 1 - Composite Plugin**

**Reasoning**:
1. **Clean Architecture**: Keeps concerns separated - existing plugins unchanged
2. **Incremental**: Can be implemented without touching core infrastructure
3. **Flexible**: Supports the primary use case and future extensions
4. **Low Risk**: New code doesn't affect existing functionality
5. **Testable**: Easy to unit test composite behavior
6. **Foundation for Future**: Can evolve toward Approach 4 (Layout System) later

### Implementation Plan

#### Phase 1: Core Composite Plugin
1. Create `CompositePlugin` class in `src/plugins/composite/`
2. Implement image composition utilities in `utils/image_utils.py`
3. Support basic positioning (corners, center)
4. Add opacity/alpha blending support

#### Phase 2: Configuration & UI
1. Create settings template for configuring composite plugins
2. Add child plugin selection UI
3. Implement region/position selectors
4. Add preview capability

#### Phase 3: Testing & Documentation
1. Unit tests for composition logic
2. Integration tests with weather + image gallery
3. Update plugin building documentation
4. Add example configurations

### Technical Specifications

#### Image Composition Utility Functions

```python
def composite_images(base: Image, overlay: Image, position: str, 
                    region: dict = None, opacity: float = 1.0) -> Image:
    """
    Composite overlay image onto base image.
    
    Args:
        base: Background image
        overlay: Image to overlay
        position: Position string ('top-left', 'bottom-right', etc.)
        region: Optional dict with width/height for overlay sizing
        opacity: Overlay opacity (0.0 to 1.0)
    
    Returns:
        Composited image
    """
```

#### Position Calculations

```python
POSITIONS = {
    'top-left': lambda base_size, overlay_size, margin: (margin, margin),
    'top-right': lambda base_size, overlay_size, margin: 
        (base_size[0] - overlay_size[0] - margin, margin),
    'bottom-left': lambda base_size, overlay_size, margin: 
        (margin, base_size[1] - overlay_size[1] - margin),
    'bottom-right': lambda base_size, overlay_size, margin: 
        (base_size[0] - overlay_size[0] - margin, 
         base_size[1] - overlay_size[1] - margin),
    'center': lambda base_size, overlay_size, margin: 
        ((base_size[0] - overlay_size[0]) // 2, 
         (base_size[1] - overlay_size[1]) // 2),
}
```

#### Region Sizing

```python
def calculate_overlay_dimensions(base_dimensions: tuple, 
                                region_config: dict) -> tuple:
    """
    Calculate overlay dimensions based on region configuration.
    
    Supports:
    - Absolute pixels: {"width": 400, "height": 300}
    - Percentages: {"width": "40%", "height": "30%"}
    - Aspect ratio preservation: {"width": 400, "maintain_aspect": True}
    """
```

## Future Enhancements

After initial implementation, consider:

1. **Smart Positioning**: Auto-detect image content to avoid overlaying important areas
2. **Transparency Controls**: Per-overlay opacity and blending modes
3. **Conditional Overlays**: Show/hide based on conditions (time, weather, etc.)
4. **Animation Support**: Fade-in/out effects for overlays
5. **Template Gallery**: Pre-built composite layouts for common use cases
6. **Migration Path**: Evolve toward full Layout System (Approach 4) based on user feedback

## Security Considerations

1. **Resource Limits**: Prevent excessive overlay counts that could cause memory issues
2. **Plugin Validation**: Ensure child plugins exist and are valid
3. **Error Handling**: Gracefully handle child plugin failures
4. **Configuration Validation**: Validate overlay settings to prevent crashes

## Performance Considerations

1. **Image Caching**: Cache child plugin outputs when they don't need refresh
2. **Lazy Loading**: Only load overlay plugins when needed
3. **Memory Management**: Release overlay images after composition
4. **Resize Efficiency**: Use appropriate resampling methods for overlays

## Conclusion

The Composite Plugin approach provides the best balance of functionality, maintainability, and user experience for implementing plugin overlays. It addresses the immediate use case while providing a foundation for future enhancements toward a full modular layout system.
