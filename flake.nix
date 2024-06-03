{
  description = "An flake to use a Python poetry project in an FHS environment when poetry2nix is uncooperative";
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/240b1d794bbfca3522dec880a3aa300932bbfd98";
  };
  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      fhsEnv =
        (pkgs.buildFHSUserEnv rec {
          name = "jn";
          targetPkgs = pkgs: (with pkgs; [
            zlib
            poetry
            libuuid
            file
            # add the system package here that are needed for the Python package dependencies
            libz # needed for 'numpy'
          ]);
          profile = ''
            export LD_LIBRARY_PATH="/lib:$LD_LIBRARY_PATH:${pkgs.lib.makeLibraryPath [pkgs.libuuid]}"
            poetry install # add --no-root here if this is just a metapackage
            source "$(poetry env info --path)"/bin/activate
          '';
        })
        .env;
    in {devShells.default = fhsEnv;});
}
