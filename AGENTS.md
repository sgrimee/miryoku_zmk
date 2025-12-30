# Miryoku ZMK - Agent Guidelines

This document provides guidance for agentic coding assistants working on the Miryoku ZMK keyboard layout repository.

## Project Overview

**Miryoku ZMK** is a ZMK firmware implementation of the Miryoku ergonomic keyboard layout. It supports many keyboards through mappings for different physical layouts and provides configurable layers via C preprocessor macros.

- **Language**: C (ZMK DeviceTree DTSI/header files)
- **Build System**: ZMK firmware build system (west)
- **CI/CD**: GitHub Actions workflows

## Build & Test Commands

### Local Build Setup
First, [set up the ZMK build environment](https://zmk.dev/docs/development/setup):
```bash
west init -l app/
west update
```

### Building Firmware Locally
Set the `ZMK_CONFIG` environment variable to the absolute path of the `config/` directory in this repo, then build:
```bash
export ZMK_CONFIG=/path/to/miryoku_zmk/config
cd <zmk-repo>
west build -s app -d build/my_keyboard -b <board> -- -DSHIELD="<shield>" -DKCONFIG_CONFIG="/path/to/config/<keyboard>.conf"
```

Example for Corne split keyboard:
```bash
west build -s app -d build/corne_left -b nice_nano -- -DSHIELD="corne_left"
```

### Testing via GitHub Actions
The repository includes several test workflows:
- **Test Build** (`test-build.yml`): Basic build test with nice_nano + corne_left
- **Test All Boards** (`test-all-boards.yml`): Tests all in-tree board definitions
- **Test All Shields** (`test-all-promicro-shields.yml`, `test-all-xiao-shields.yml`): Tests shield definitions
- **Test All Configs** (`test-all-configs.yml`): Tests configuration combinations
- **Build Inputs** (`build-inputs.yml`): Manual workflow with form inputs
- **Main** (`main.yml`): Core build workflow used by other workflows

### Running Single Builds
For testing a single keyboard configuration:
```bash
# Via GitHub Actions: Use "Run workflow" on test-build.yml and modify parameters
# Modify test-build.yml temporarily for local testing, or use build-inputs.yml workflow

# For a fresh build, clean previous artifacts:
cd <zmk-repo>
rm -rf build/
west build -s app -d build/corne_left -b nice_nano -- -DSHIELD="corne_left"
```

## Code Style Guidelines

### File Structure & Organization

1. **Keymap Files** (`config/*.keymap`)
   - Located in `config/` directory, named after keyboard (e.g., `corne.keymap`)
   - Include custom config, mapping, and Miryoku keymap in this order:
     ```c
     // Copyright comment required
     #include "../miryoku/custom_config.h"
     #include "../miryoku/mapping/XX/keyboard.h"
     #include "../miryoku/miryoku.dtsi"
     ```
   - Minimal content; most logic is in mapping and miryoku files

2. **Mapping Files** (`miryoku/mapping/XX/*.h`)
   - Define layout-specific mappings for keyboard physical layouts
   - Named by key count (e.g., `42/corne.h`, `36/minidox.h`)
   - Include guards with `#if !defined (MIRYOKU_LAYOUTMAPPING_KEYBOARDNAME)`
   - Define `MIRYOKU_LAYOUTMAPPING_*` macro with key bindings

3. **Behavior & Feature Files** (`miryoku/*.h`, `miryoku/*.dtsi`)
   - `miryoku.h`: Main header with macro definitions
   - `miryoku.dtsi`: Main DeviceTree Source Include file
   - `miryoku_behaviors.h`: Hold-tap and layer-tap behavior macros
   - Feature files: `miryoku_mousekeys.h`, `miryoku_clipboard.h`, etc.

### Naming Conventions

#### Macros (C Preprocessor)
- **Case**: ALL_UPPERCASE
- **Naming Pattern**:
  - Layout options: `MIRYOKU_ALPHAS_*`, `MIRYOKU_LAYERS_*`, `MIRYOKU_CLIPBOARD_*`
  - Examples: `MIRYOKU_ALPHAS_QWERTY`, `MIRYOKU_LAYERS_FLIP`, `MIRYOKU_CLIPBOARD_WIN`
  - Feature toggles: `MIRYOKU_KLUDGE_*` for experimental/workaround features
  - Internal macros: `U_*` (e.g., `U_MT`, `U_LT`, `U_NP`, `U_NA`, `U_NU`)
  - Layer macros: `MIRYOKU_LAYER_*` (e.g., `MIRYOKU_LAYER_BASE`, `MIRYOKU_LAYER_NAV`)

#### Layer Names
- Predefined: `MIRYOKU_LAYER_BASE`, `MIRYOKU_LAYER_EXTRA`, `MIRYOKU_LAYER_TAP`
- Nav/Symbol: `MIRYOKU_LAYER_NAV`, `MIRYOKU_LAYER_SYM`
- Advanced: `MIRYOKU_LAYER_MOUSE`, `MIRYOKU_LAYER_MEDIA`, `MIRYOKU_LAYER_NUM`, `MIRYOKU_LAYER_FUN`, `MIRYOKU_LAYER_BUTTON`

#### Internal References
- `u_*` prefix for behavior references (e.g., `&u_mt`, `&u_lt`, `&u_to_*`)
- `U_*` for macro definitions used in keymaps

### Formatting & Style

#### Line Length & Alignment
- Lines may exceed 100 characters for clarity and alignment in keymaps
- Keymap rows should align visually (commas line up)
- Use backslash continuation for long macro definitions

#### `custom_config.h` Layer Formatting Convention
The `miryoku/custom_config.h` file uses a specific format for layer definitions to maximize readability:

1. **5 keys per line** - Each line contains one half of a physical keyboard row (left or right hand)
2. **Blank lines between physical rows** - Use a backslash-only line (`\`) to visually separate rows
3. **Column alignment** - Pad key definitions with spaces so columns align vertically
4. **Row structure** (for a 36-key split keyboard):
   - Lines 1-2: Top row (left hand, right hand)
   - Blank line
   - Lines 3-4: Home row (left hand, right hand)
   - Blank line
   - Lines 5-6: Bottom row (left hand, right hand)
   - Blank line
   - Lines 7-8: Thumb keys (left hand, right hand)

Example formatting:
```c
#define MIRYOKU_LAYER_BASE \
&kp Q,             &kp W,             &kp E,             &kp R,             &kp T,             \
&kp Y,             &kp U,             &kp I,             &kp O,             &kp P,             \
\
U_MT(LCTRL, A),    U_MT(LALT, S),     U_MT(LGUI, D),     U_MT(LSHFT, F),    &kp G,             \
&kp H,             U_MT(LSHFT, J),    U_MT(RGUI, K),     U_MT(LALT, L),     U_MT(RCTRL, SQT),  \
\
U_LT(U_BUTTON, Z), U_MT(RALT, X),     &kp C,             &kp V,             &kp B,             \
&kp N,             &kp M,             &kp COMMA,         U_MT(RALT, DOT),   U_LT(U_BUTTON, SLASH), \
\
U_NP,              U_NP,              U_LT(U_FUN, ESC),  U_LT(U_NUM, TAB),   U_LT(U_NAV, SPACE), \
U_LT(U_SYM, BSPC), U_LT(U_BUTTON, RET), U_LT(U_MEDIA, DEL), U_NP,           U_NP
```

**IMPORTANT**: When editing `custom_config.h`, preserve this formatting structure. Do not collapse multiple physical rows onto single lines.

#### Comments
- Use `//` for comments (C style)
- Add copyright headers to all source files:
  ```c
  // Copyright 2022 Manna Harbour
  // https://github.com/manna-harbour/miryoku
  ```
- Document non-obvious mappings (especially for layout alternatives)

#### Preprocessor Directives
- Use `#if defined (OPTION_NAME)` for conditional compilation
- Prefer `#pragma once` for include guards in `.h` files
- Always include guards in mapping files using `#if !defined (MIRYOKU_LAYOUTMAPPING_NAME)`

### Type & Declaration Conventions

1. **Behaviors in DeviceTree**
   - Use reference syntax: `&kp`, `&mo`, `&to`, `&u_mt`, `&u_lt`
   - Behaviors are referenced with `&` prefix in DeviceTree
   - Custom behaviors defined in `.dtsi` files

2. **Macro Parameters**
   - Use descriptive names: `MOD` for modifiers, `TAP` for tap keys, `LAYER` for layer numbers
   - Single capital letter for key variables in mappings: `K00`, `K01`, etc.
   - Use `N##` prefix for keys not used in the Miryoku layout

3. **Key Codes**
   - ZMK key codes with `&kp` prefix (e.g., `&kp Q`, `&kp LCTRL`)
   - Special codes: `&none` for unmapped keys
   - Keymap-specific: `U_NP` (not present), `U_NA` (not available), `U_NU` (not used)

### Error Handling

1. **Build Configuration Errors**
   - Invalid layout options will fail at build time due to missing macro definitions
   - The build system validates `MIRYOKU_OPTION_*` definitions

2. **Compatibility Checks**
   - Verify mapping file exists for keyboard key count
   - Check that all referenced behaviors are defined in included files
   - Ensure feature flags (e.g., `MIRYOKU_KLUDGE_*`) match build options

3. **Common Issues**
   - Missing `#include` directives cause linker errors
   - Mismatched key count between mapping and keymap causes undefined behavior
   - Using undefined layer references in `&u_to_*` behaviors

### Imports & Includes

**Order of includes in keymap files:**
1. Custom config file: `#include "../miryoku/custom_config.h"`
2. Layout mapping: `#include "../miryoku/mapping/XX/keyboard.h"`
3. Main keymap: `#include "../miryoku/miryoku.dtsi"`

**Include guards pattern:**
```c
#pragma once
// or
#if !defined (MIRYOKU_LAYOUTMAPPING_KEYBOARDNAME)
// ... content ...
#endif
```

## Configuration System

- **Config File**: `miryoku/custom_config.h` - defines layer macros and feature toggles
- **Kconfig**: `config/<keyboard>.conf` - ZMK-specific hardware configuration
- **Build Options**: Workflow inputs allow passing custom config and Kconfig overrides
- **Environment Variables**: `ZMK_CONFIG` (path to config directory), `MIRYOKU_DEBUG` (enables debugging in CI)

## File Locations Reference

- `config/` - Keyboard keymap files
- `miryoku/` - Core Miryoku layout files and behaviors
- `miryoku/mapping/` - Physical layout mappings by key count
- `miryoku/miryoku_babel/` - Generated layer data from Miryoku Babel
- `.github/workflows/` - CI/CD workflow definitions
- `.github/workflows/outboards/` - Out-of-tree keyboard metadata

## Common Tasks

**Adding a new keyboard mapping:**
1. Create mapping file: `miryoku/mapping/XX/keyboard.h`
2. Define `MIRYOKU_LAYOUTMAPPING_KEYBOARD` macro
3. Create keymap: `config/keyboard.keymap` with includes
4. Add workflow test if desired

**Modifying layers:**
1. Edit layer macro in `miryoku/custom_config.h`
2. Rebuild with `ZMK_CONFIG` set correctly
3. Test via local build or GitHub Actions workflow

**Adding features:**
1. Create feature file: `miryoku/miryoku_feature.h`
2. Include in `miryoku/miryoku.h` conditionally
3. Add config option to toggle (e.g., `MIRYOKU_FEATURE_*)
