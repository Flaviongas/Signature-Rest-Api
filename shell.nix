{ pkgs ? import <nixpkgs> {} }:
# For nix-shell

let
  libraryPath = with pkgs;
    lib.makeLibraryPath [
      # add other library packages here if needed
      stdenv.cc.cc
    ];
in
pkgs.mkShell {
  packages = [
    (pkgs.python312.withPackages (ps: with ps; [
      pandas
      numpy
      ]))
  ];
shellHook = ''
 export "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${libraryPath}"
 uv run manage.py runserver
  '';

}
