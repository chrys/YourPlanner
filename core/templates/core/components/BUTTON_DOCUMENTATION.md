# Button Component Documentation

## Overview
The button component provides a consistent, reusable way to create buttons across the YourPlanner application. It follows the Figma design system and supports multiple variants and sizes.

## File Locations
- **Template**: `core/templates/core/components/button.html`
- **Styles**: `core/static/core/css/buttons.css`
- **Import**: Automatically included in `core/templates/core/base.html`

## Basic Usage

### Primary Button (Default - Green)
```django
{% include "core/components/button.html" with 
  text="Download Invoice" 
  url="{% url 'payments:download_invoice' %}" 
%}
```

### Button with Icon
```django
{% include "core/components/button.html" with 
  text="Download Invoice (PDF)" 
  url="{% url 'payments:download_invoice' %}" 
  icon_path="M19 15V17C19 18.1046 18.1046 19 17 19H7C5.89543 19 5 18.1046 5 17V15M12 5V15M12 15L10 13M12 15L14 13"
%}
```

## Variants

### Primary (Green) - Default
```django
{% include "core/components/button.html" with 
  text="Save Changes" 
  url="#" 
  variant="primary" 
%}
```
- Background: #79976e
- Text: #f4f6f3
- Use for: Primary actions, confirmations

### Secondary (Pink)
```django
{% include "core/components/button.html" with 
  text="Add Item" 
  url="#" 
  variant="secondary" 
%}
```
- Background: #e88ea1
- Text: #ffffff
- Use for: Secondary actions, alternative options

### Tertiary (White)
```django
{% include "core/components/button.html" with 
  text="Cancel" 
  url="#" 
  variant="tertiary" 
%}
```
- Background: #ffffff
- Border: #79976e
- Text: #79976e
- Use for: Cancel/back actions, neutral options

### Danger (Red)
```django
{% include "core/components/button.html" with 
  text="Delete" 
  url="#" 
  variant="danger" 
%}
```
- Background: #dc3545
- Text: #ffffff
- Use for: Destructive actions

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | String | Yes | - | Button label text |
| `url` | String | Yes | - | Link destination URL |
| `icon_path` | String | No | - | SVG path data for icon |
| `variant` | String | No | primary | Button style (primary, secondary, tertiary, danger) |
| `classes` | String | No | - | Additional CSS classes |
| `blank` | Boolean | No | False | Open link in new tab |

## Size Modifiers

### Small Button
```django
{% include "core/components/button.html" with 
  text="Edit" 
  url="#" 
  classes="btn-sm" 
%}
```

### Large Button
```django
{% include "core/components/button.html" with 
  text="Get Started" 
  url="#" 
  classes="btn-lg" 
%}
```

### Full Width Button
```django
{% include "core/components/button.html" with 
  text="Complete Order" 
  url="#" 
  classes="btn-full" 
%}
```

## Complex Example

```django
{% include "core/components/button.html" with 
  text="Download Report" 
  url="{% url 'reports:download' %}" 
  icon_path="M19 15V17C19 18.1046 18.1046 19 17 19H7C5.89543 19 5 18.1046 5 17V15M12 5V15M12 15L10 13M12 15L14 13"
  variant="secondary"
  classes="btn-lg btn-full"
  blank=True
%}
```

## Styling Customization

### Custom Colors (Via CSS)
To override button colors, add custom CSS:

```css
.btn-custom {
  background-color: #your-color;
  color: #text-color;
}

.btn-custom:hover {
  background-color: #your-hover-color;
}
```

Then use:
```django
{% include "core/components/button.html" with 
  text="Button" 
  url="#" 
  classes="btn-custom" 
%}
```

## Accessibility Features

- ✅ Focus states with outline
- ✅ Hover states for visual feedback
- ✅ Active states for click feedback
- ✅ Disabled state support
- ✅ Semantic HTML with proper link structure
- ✅ Color contrast meets WCAG AA standards

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Icon SVG Paths

Common icon paths for reuse:

### Download Icon
```
M19 15V17C19 18.1046 18.1046 19 17 19H7C5.89543 19 5 18.1046 5 17V15M12 5V15M12 15L10 13M12 15L14 13
```

## Best Practices

1. **Always use semantic URLs**: `{% url 'app_name:view_name' %}`
2. **Keep text short and action-oriented**: "Download", "Save", "Cancel"
3. **Use appropriate variants**: Primary for main actions, secondary for alternatives
4. **Include icons when helpful**: But don't overuse them
5. **Test on mobile**: Use size classes (btn-sm, btn-lg) as needed
6. **Avoid nested buttons**: Don't put buttons inside buttons
7. **Use disabled state for unavailable actions**: Instead of hiding buttons

## Migration Guide

### Old Style
```html
<button class="btn btn-primary">Click me</button>
```

### New Style
```django
{% include "core/components/button.html" with 
  text="Click me" 
  url="#" 
%}
```

## Troubleshooting

### Button not showing styles
- Ensure `core/templates/core/base.html` is extended
- Check that `buttons.css` is linked in base template
- Verify CSS file path is correct

### Icon not rendering
- Verify SVG path is valid
- Check that path syntax is correct (no quotes inside d="...")
- Test SVG path in a standalone SVG element

### Colors look wrong
- Check CSS specificity
- Ensure no other stylesheets override button styles
- Verify hex color codes in CSS
