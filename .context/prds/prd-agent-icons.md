# Agent Icons: Generation & Management

## Overview
This document outlines approaches for generating and managing agent icons in the MUXI Framework web UI.

## Auto-Generated Icons (Default)
- **Hash-based SVG generation**: Libraries like `jdenticon` or `blockies` to create deterministic geometric patterns from agent IDs/names
- **Gradient + symbol combinations**: Generate color gradients based on agent type/function with symbolic overlays
- **Initial-based icons**: Use the agent's first letter with consistent styling but varied background colors (Material UI style)

## Custom Icon Support
Allow users to upload custom branded icons through the web UI without modifying YAML configurations:

### Storage Options

#### 1. JSON File Approach
```javascript
{
  "agentIcons": {
    "agent-123": {
      "type": "custom",
      "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEU..."
    },
    "agent-456": {
      "type": "default"
      // No data needed - will use auto-generated SVG
    }
  }
}
```

**Pros**:
- Simple implementation
- No additional dependencies
- Works well for smaller deployments
- Easy to backup/restore
- No database setup required

**Cons**:
- Less scalable for many agents/users
- Requires file system access
- Potential concurrency issues

**Suggested location**: `data/agent-icons.json`

#### 2. Database Approach
Create a simple table structure:
```sql
CREATE TABLE agent_icons (
  agent_id TEXT PRIMARY KEY,
  icon_type TEXT NOT NULL, -- 'default' or 'custom'
  icon_data TEXT, -- base64 encoded data URI for custom icons
  updated_at TIMESTAMP
);
```

**Pros**:
- Better for scale
- Consistent with memory storage approach
- Better for multi-user/distributed setups
- Built-in concurrency handling

**Cons**:
- Additional database setup/migration
- More complex implementation

## Web UI Considerations
- Add icon upload button on agent configuration screens
- Show preview of current icon (default or custom)
- Provide option to reset to default
- Include size/format restrictions
- Implement client-side image resizing/optimization

## Implementation Notes
- Keep YAML configs clean (no icon specifications there)
- Web-only feature for better separation of concerns
- Default to auto-generated icons for new agents
- Consider caching mechanisms for performance
