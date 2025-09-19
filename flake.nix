{
  description = "Shunting yard in rust";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    naersk.url = "github:nix-community/naersk/master";

    treefmt-nix.url = "github:numtide/treefmt-nix";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs =
    {
      self,
      nixpkgs,
      naersk,
      flake-utils,
      treefmt-nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        project = "Shunting yard.rs";

        naersk-lib = pkgs.callPackage naersk { };
      in
      {
        defaultPackage = naersk-lib.buildPackage ./.;
        devShells.default = pkgs.mkShell {
          name = project;
          LSP_SERVER = "rust_analyzer";
          packages = with pkgs; [
            cargo
            rustfmt
            rustPackages.clippy

            rust-analyzer
            (writeShellScriptBin "clippy" ''
              cargo clippy -- -W clippy::all  -W clippy::pedantic
            '')
            (writeShellScriptBin "clippy-mad" ''
              cargo clippy -- -W clippy::all -W clippy::pedantic -W clippy::nursery -W clippy::restriction
            '')
            (writeShellScriptBin "clippy-fix" ''
              cargo clippy --fix -- -W clippy::all  -W clippy::pedantic
            '')

            manim
            (pkgs.python3.withPackages (python-pkgs: [
              python-pkgs.manim
            ]))
          ];
          shellHook = ''
            echo -e '(¬_¬") Entered ${project} :D'
          '';
        };
        formatter = treefmt-nix.lib.mkWrapper pkgs {
          projectRootFile = "flake.nix";
          programs = {
            nixfmt.enable = true;
            rustfmt.enable = true;
            black.enable = true;
          };
        };
      }
    );
}
