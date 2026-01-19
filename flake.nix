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
       packages = forAllSystems (system: let
         pkgs = nixpkgs.legacyPackages.${system};
         firmware-base = zmk-nix.legacyPackages.${system}.buildSplitKeyboard {
           name = "aurora-sweep-firmware";
           src = nixpkgs.lib.sourceFilesBySuffices self [
             ".board" ".cmake" ".conf" ".defconfig" ".dts" ".dtsi"
             ".json" ".keymap" ".overlay" ".shield" ".yml" "_defconfig" ".h"
           ];
           board = "nice_nano";
           shield = "splitkb_aurora_sweep_%PART%";
           snippets = [ "zmk-usb-logging" ];
           enableZmkStudio = false;
           inherit zephyrDepsHash;
           extraCmakeFlags = [ "-DCONFIG_BUILD_OUTPUT_HEX=y" ];
          installPhase = ''
            runHook preInstall
            mkdir $out
            cp */*.uf2 $out/ 2>/dev/null || true
            cp */*.hex $out/ 2>/dev/null || true
            runHook postInstall
          '';
        };
      in rec {
        default = firmware;

        # Main firmware (left + right halves with ZMK Studio) - with HEX files in result/
        firmware = pkgs.runCommand "aurora-sweep-firmware-combined" {} ''
          mkdir $out
          ln -s ${firmware-base.left}/zmk.uf2 $out/zmk_left.uf2
          ln -s ${firmware-base.left}/zmk.hex $out/zmk_left.hex
          ln -s ${firmware-base.right}/zmk.uf2 $out/zmk_right.uf2
          ln -s ${firmware-base.right}/zmk.hex $out/zmk_right.hex
        '';

        firmware-base-export = firmware-base;

        # Settings reset firmware (build separately with: nix build .#settings-reset)
        settings-reset = zmk-nix.legacyPackages.${system}.buildKeyboard {
          name = "settings-reset";
          src = nixpkgs.lib.sourceFilesBySuffices self [
            ".board" ".cmake" ".conf" ".defconfig" ".dts" ".dtsi"
            ".json" ".keymap" ".overlay" ".shield" ".yml" "_defconfig" ".h"
          ];
          board = "nice_nano";
          shield = "settings_reset";
          inherit zephyrDepsHash;
          extraCmakeFlags = [ "-DCONFIG_BUILD_OUTPUT_HEX=y" ];
          installPhase = ''
            runHook preInstall
            mkdir $out
            cp */*.uf2 $out/ 2>/dev/null || true
            cp */*.hex $out/ 2>/dev/null || true
            runHook postInstall
          '';
          meta = {
            description = "Settings reset firmware for nice!nano v2";
            license = nixpkgs.lib.licenses.mit;
            platforms = nixpkgs.lib.platforms.all;
          };
        };

        flash = zmk-nix.packages.${system}.flash.override { firmware = firmware-base-export; };
        update = zmk-nix.packages.${system}.update;
     });

    devShells = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      default = zmk-nix.devShells.${system}.default.overrideAttrs (oldAttrs: {
        nativeBuildInputs = (oldAttrs.nativeBuildInputs or []) ++ [
          pkgs.picocom
        ];
      });
    });
  };
}
