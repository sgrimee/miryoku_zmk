{
  description = "Miryoku ZMK firmware for Splitkb Aurora Sweep";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    zmk-nix = {
      url = "github:lilyinstarlight/zmk-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, zmk-nix }: let
    forAllSystems = nixpkgs.lib.genAttrs (nixpkgs.lib.attrNames zmk-nix.packages);
    zephyrDepsHash = "sha256-arF/XHsZXtL9LNgeN6Cni43nzRJyFuzyxKqqPJsvALA=";
  in {
    packages = forAllSystems (system: rec {
      default = firmware;

      # Main firmware (left + right halves with ZMK Studio)
      firmware = zmk-nix.legacyPackages.${system}.buildSplitKeyboard {
        name = "aurora-sweep-firmware";
        src = nixpkgs.lib.sourceFilesBySuffices self [
          ".board" ".cmake" ".conf" ".defconfig" ".dts" ".dtsi"
          ".json" ".keymap" ".overlay" ".shield" ".yml" "_defconfig" ".h"
        ];
        board = "nice_nano_v2";
        shield = "splitkb_aurora_sweep_%PART%";
        enableZmkStudio = true;
        inherit zephyrDepsHash;
        meta = {
          description = "Miryoku ZMK firmware for Aurora Sweep with ZMK Studio";
          license = nixpkgs.lib.licenses.mit;
          platforms = nixpkgs.lib.platforms.all;
        };
      };

      # Settings reset firmware (build separately with: nix build .#settings-reset)
      settings-reset = zmk-nix.legacyPackages.${system}.buildKeyboard {
        name = "settings-reset";
        src = nixpkgs.lib.sourceFilesBySuffices self [
          ".board" ".cmake" ".conf" ".defconfig" ".dts" ".dtsi"
          ".json" ".keymap" ".overlay" ".shield" ".yml" "_defconfig" ".h"
        ];
        board = "nice_nano_v2";
        shield = "settings_reset";
        inherit zephyrDepsHash;
        meta = {
          description = "Settings reset firmware for nice!nano v2";
          license = nixpkgs.lib.licenses.mit;
          platforms = nixpkgs.lib.platforms.all;
        };
      };

      flash = zmk-nix.packages.${system}.flash.override { inherit firmware; };
      update = zmk-nix.packages.${system}.update;
    });

    devShells = forAllSystems (system: {
      default = zmk-nix.devShells.${system}.default;
    });
  };
}
