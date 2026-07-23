# Rayne-OS

Rayne-OS is an AI operating system concept built on Arch Linux around three core
upstream components:

- **AI runtime:** [Milla Rayne AI](https://github.com/mrdannyclark82/Milla-Rayne.git)
- **Boot manager:** [Aetherboot](https://github.com/mrdannyclark82/Aetherboot.git) or
  [Aether-Boot-Manager](https://github.com/mrdannyclark82/Aether-Boot-Manager.git)
- **Update system:** [SARIi](https://github.com/mrdannyclark82/SARIi.git)

## Architecture

Rayne-OS is intended to combine those projects into a single operating system
experience:

1. **Boot** with Aetherboot or Aether-Boot-Manager.
2. **Start the AI layer** with Milla Rayne AI as the primary system intelligence.
3. **Maintain and update the system** through SARIi.

## Repository scope

This repository defines the Rayne-OS composition and serves as the place where
the boot, AI, and update components are tied together into one platform.
